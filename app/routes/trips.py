"""
TripWise — Smart Trip Budget Planner Routes and API.
"""
from datetime import date, datetime
from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for
from app.extensions import db
from app.routes.auth import login_required
from app.models.trip import Trip
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.trip_engine import (
    estimate_trip_budget,
    generate_scenario_comparison,
    check_trip_affordability,
    generate_budget_adjustment_suggestions
)
from app.services.budget_engine import calculate_budget_summary
from app.services.money import to_minor_units, format_money, from_minor_units

trips_bp = Blueprint('trips', __name__)


@trips_bp.route('/trips')
@login_required
def view_trips():
    user = g.current_user
    today = date.today()
    user_trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.departure_date.asc()).all()

    # Selected trip from query params, or default to the most recent upcoming/active trip
    selected_trip_id = request.args.get('trip_id', type=int)
    active_trip = None
    if selected_trip_id:
        active_trip = Trip.query.filter_by(id=selected_trip_id, user_id=user.id).first()
    if not active_trip and user_trips:
        # Prioritize upcoming or planning trips
        active_trip = next((t for t in user_trips if t.status in ('PLANNING', 'ACTIVE')), user_trips[0])

    # Affordability context for user
    summary = calculate_budget_summary(user.id, today.year, today.month)
    current_available_cash = max(0, (user.opening_balance_minor_units or 0) + summary['surplus']['minor'])

    # User's recent unlinked transactions for the "+ Link Transaction" modal
    unlinked_txns = Transaction.query.filter_by(
        user_id=user.id,
        trip_id=None,
        transaction_type='EXPENSE'
    ).order_by(Transaction.transaction_date.desc()).limit(30).all()

    # Expense categories for "+ Log Expense"
    expense_categories = Category.query.filter_by(
        user_id=user.id,
        transaction_type='EXPENSE',
        is_archived=False
    ).order_by(Category.name.asc()).all()

    # If active trip exists, compute its live affordability and suggestions
    affordability = None
    suggestions = []
    if active_trip:
        affordability = check_trip_affordability(
            user.id,
            active_trip.total_budget_minor_units,
            departure_date=active_trip.departure_date,
            trip_nature=active_trip.trip_nature
        )
        suggestions = generate_budget_adjustment_suggestions(
            user.id,
            {
                'travel_style': active_trip.travel_style,
                'transport_mode': active_trip.transport_mode,
                'duration_days': active_trip.duration_days,
                'travellers_count': active_trip.travellers_count
            },
            affordability
        )

    return render_template(
        'trips.html',
        user=user,
        trips=user_trips,
        active_trip=active_trip,
        affordability=affordability,
        suggestions=suggestions,
        unlinked_transactions=unlinked_txns,
        expense_categories=expense_categories,
        current_available_cash=current_available_cash,
        today_iso=today.isoformat()
    )


@trips_bp.route('/trips/<int:trip_id>')
@login_required
def view_single_trip(trip_id):
    return redirect(url_for('trips.view_trips', trip_id=trip_id))


@trips_bp.route('/api/trips/estimate', methods=['POST'])
@login_required
def api_estimate_trip():
    user = g.current_user
    data = request.get_json() or {}

    origin = (data.get('starting_city') or 'Delhi').strip()
    destination = (data.get('destination') or 'Jaipur').strip()
    departure_str = data.get('departure_date')
    return_str = data.get('return_date')
    duration_days = max(1, int(data.get('duration_days') or 1))
    travellers = max(1, int(data.get('travellers_count') or 1))
    style = (data.get('travel_style') or 'STANDARD').upper()
    transport = (data.get('transport_mode') or 'TRAIN').upper()
    accommodation = (data.get('accommodation_type') or 'STANDARD_HOTEL').upper()
    nature = (data.get('trip_nature') or 'PLANNED').upper()

    departure_date = None
    if departure_str:
        try:
            departure_date = datetime.strptime(departure_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if return_str and departure_date:
        try:
            return_date = datetime.strptime(return_str, '%Y-%m-%d').date()
            if return_date >= departure_date:
                duration_days = max(1, (return_date - departure_date).days + 1)
        except ValueError:
            pass

    params = {
        'starting_city': origin,
        'destination': destination,
        'departure_date': departure_date,
        'duration_days': duration_days,
        'travellers_count': travellers,
        'travel_style': style,
        'transport_mode': transport,
        'accommodation_type': accommodation,
        'trip_nature': nature
    }

    # 1. Budget breakdown estimation
    estimation = estimate_trip_budget(params, user.currency)

    # 2. Side-by-side scenario comparison
    scenarios = generate_scenario_comparison(params, user.currency)

    # 3. Affordability check
    custom_reserve = data.get('custom_reserve')
    custom_reserve_minor = to_minor_units(custom_reserve, user.currency) if custom_reserve is not None and custom_reserve != '' else None

    affordability = check_trip_affordability(
        user.id,
        estimation['total_budget_minor'],
        departure_date=departure_date,
        trip_nature=nature,
        custom_reserve_minor=custom_reserve_minor
    )

    # 4. Budget adjustment suggestions
    suggestions = generate_budget_adjustment_suggestions(user.id, params, affordability)

    return jsonify({
        'success': True,
        'params': {
            'starting_city': origin,
            'destination': destination,
            'duration_days': duration_days,
            'travellers_count': travellers,
            'travel_style': style,
            'transport_mode': transport,
            'accommodation_type': accommodation,
            'trip_nature': nature
        },
        'estimation': estimation,
        'scenarios': scenarios,
        'affordability': affordability,
        'suggestions': suggestions
    })


@trips_bp.route('/api/trips', methods=['GET'])
@login_required
def api_get_trips():
    user = g.current_user
    trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.departure_date.asc()).all()
    return jsonify({
        'success': True,
        'trips': [t.to_dict() for t in trips]
    })


@trips_bp.route('/api/trips', methods=['POST'])
@login_required
def api_create_trip():
    user = g.current_user
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    origin = (data.get('starting_city') or '').strip()
    destination = (data.get('destination') or '').strip()
    departure_str = data.get('departure_date')
    return_str = data.get('return_date')
    travellers = max(1, int(data.get('travellers_count') or 1))
    duration_days = max(1, int(data.get('duration_days') or 1))
    style = (data.get('travel_style') or 'STANDARD').upper()
    transport = (data.get('transport_mode') or 'TRAIN').upper()
    accommodation = (data.get('accommodation_type') or 'STANDARD_HOTEL').upper()
    nature = (data.get('trip_nature') or 'PLANNED').upper()
    notes = (data.get('notes') or '').strip()

    if not destination:
        return jsonify({'success': False, 'error': 'Destination city is required.'}), 400

    if not name:
        name = f"Trip to {destination}"

    today = date.today()
    departure_date = today
    if departure_str:
        try:
            departure_date = datetime.strptime(departure_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    return_date = departure_date
    if return_str:
        try:
            return_date = datetime.strptime(return_str, '%Y-%m-%d').date()
            if return_date >= departure_date:
                duration_days = max(1, (return_date - departure_date).days + 1)
        except ValueError:
            pass

    # Category estimates: either supplied directly or estimated
    estimates = data.get('category_estimates')
    total_budget_minor = 0
    if estimates and isinstance(estimates, dict):
        total_budget_minor = sum(
            int(item.get('estimated_cost_minor', 0)) for item in estimates.values() if isinstance(item, dict)
        )
    else:
        calc_params = {
            'starting_city': origin or 'Delhi',
            'destination': destination,
            'duration_days': duration_days,
            'travellers_count': travellers,
            'travel_style': style,
            'transport_mode': transport,
            'accommodation_type': accommodation,
            'trip_nature': nature
        }
        est_result = estimate_trip_budget(calc_params, user.currency)
        estimates = est_result['breakdown']
        total_budget_minor = est_result['total_budget_minor']

    # Optional custom budget target
    custom_target = data.get('custom_budget_target')
    custom_target_minor = to_minor_units(custom_target, user.currency) if custom_target is not None and custom_target != '' else None

    trip = Trip(
        user_id=user.id,
        name=name,
        starting_city=origin or 'Delhi',
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        duration_days=duration_days,
        travellers_count=travellers,
        travel_style=style,
        transport_mode=transport,
        accommodation_type=accommodation,
        trip_nature=nature,
        total_budget_minor_units=total_budget_minor,
        custom_budget_target_minor_units=custom_target_minor,
        status='PLANNING',
        notes=notes
    )
    trip.category_estimates = estimates

    db.session.add(trip)
    db.session.commit()

    return jsonify({'success': True, 'trip': trip.to_dict()}), 201


@trips_bp.route('/api/trips/<int:trip_id>', methods=['GET'])
@login_required
def api_get_trip(trip_id):
    user = g.current_user
    trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
    if not trip:
        return jsonify({'success': False, 'error': 'Trip not found.'}), 404

    affordability = check_trip_affordability(
        user.id,
        trip.total_budget_minor_units,
        departure_date=trip.departure_date,
        trip_nature=trip.trip_nature
    )

    return jsonify({
        'success': True,
        'trip': trip.to_dict(),
        'transactions': [t.to_dict() for t in trip.transactions],
        'affordability': affordability
    })


@trips_bp.route('/api/trips/<int:trip_id>', methods=['PUT'])
@login_required
def api_update_trip(trip_id):
    user = g.current_user
    trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
    if not trip:
        return jsonify({'success': False, 'error': 'Trip not found.'}), 404

    data = request.get_json() or {}

    if 'name' in data and data['name'].strip():
        trip.name = data['name'].strip()
    if 'status' in data:
        trip.status = data['status'].upper()
    if 'notes' in data:
        trip.notes = data['notes']
    if 'booking_links' in data:
        trip.booking_links = data['booking_links']
    if 'starting_city' in data and data['starting_city'].strip():
        trip.starting_city = data['starting_city'].strip()
    if 'destination' in data and data['destination'].strip():
        trip.destination = data['destination'].strip()
    if 'travel_style' in data:
        trip.travel_style = data['travel_style'].upper()
    if 'transport_mode' in data:
        trip.transport_mode = data['transport_mode'].upper()
    if 'accommodation_type' in data:
        trip.accommodation_type = data['accommodation_type'].upper()
    if 'trip_nature' in data:
        trip.trip_nature = data['trip_nature'].upper()
    if 'travellers_count' in data:
        trip.travellers_count = max(1, int(data['travellers_count']))

    if 'departure_date' in data and data['departure_date']:
        try:
            trip.departure_date = datetime.strptime(str(data['departure_date']).split('T')[0], '%Y-%m-%d').date()
        except ValueError:
            pass
    if 'return_date' in data and data['return_date']:
        try:
            trip.return_date = datetime.strptime(str(data['return_date']).split('T')[0], '%Y-%m-%d').date()
            if trip.return_date >= trip.departure_date:
                trip.duration_days = max(1, (trip.return_date - trip.departure_date).days + 1)
        except ValueError:
            pass

    if 'total_budget_minor_units' in data and data['total_budget_minor_units'] is not None:
        trip.total_budget_minor_units = int(data['total_budget_minor_units'])

    if 'custom_budget_target_minor_units' in data:
        trip.custom_budget_target_minor_units = data['custom_budget_target_minor_units']

    # Update category estimates if provided
    if 'category_estimates' in data and isinstance(data['category_estimates'], dict):
        updated_estimates = data['category_estimates']
        total_minor = 0
        for cat_k, cat_val in updated_estimates.items():
            if isinstance(cat_val, dict):
                # Ensure formatted_cost is in sync with estimated_cost_minor
                minor_amt = int(cat_val.get('estimated_cost_minor', 0))
                cat_val['formatted_cost'] = format_money(minor_amt, user.currency)
                total_minor += minor_amt

        trip.category_estimates = updated_estimates
        if 'total_budget_minor_units' not in data:
            trip.total_budget_minor_units = total_minor

    db.session.commit()
    return jsonify({'success': True, 'trip': trip.to_dict()})


@trips_bp.route('/api/trips/<int:trip_id>', methods=['DELETE'])
@login_required
def api_delete_trip(trip_id):
    user = g.current_user
    trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
    if not trip:
        return jsonify({'success': False, 'error': 'Trip not found.'}), 404

    # Unlink all linked transactions safely without deleting the transaction records
    for txn in trip.transactions:
        txn.trip_id = None

    db.session.delete(trip)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Trip plan deleted successfully.'})


@trips_bp.route('/api/trips/<int:trip_id>/transactions', methods=['POST'])
@login_required
def api_link_or_create_trip_transaction(trip_id):
    user = g.current_user
    trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
    if not trip:
        return jsonify({'success': False, 'error': 'Trip not found.'}), 404

    data = request.get_json() or {}

    # Case 1: Linking an existing transaction
    existing_txn_id = data.get('transaction_id')
    if existing_txn_id:
        txn = Transaction.query.filter_by(id=existing_txn_id, user_id=user.id).first()
        if not txn:
            return jsonify({'success': False, 'error': 'Transaction not found.'}), 404
        txn.trip_id = trip.id
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Transaction linked to trip.',
            'trip': trip.to_dict(),
            'transaction': txn.to_dict()
        })

    # Case 2: Creating a new transaction logged directly to this trip
    amount_raw = data.get('amount')
    description = (data.get('description') or f"Trip expense for {trip.destination}").strip()
    category_id = data.get('category_id')
    txn_date_str = data.get('transaction_date')

    if amount_raw is None or str(amount_raw).strip() == '':
        return jsonify({'success': False, 'error': 'Amount is required.'}), 400

    amount_minor = to_minor_units(amount_raw, user.currency)
    if amount_minor <= 0:
        return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400

    txn_date = date.today()
    if txn_date_str:
        try:
            txn_date = datetime.strptime(txn_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    new_txn = Transaction(
        user_id=user.id,
        category_id=category_id,
        amount_minor_units=amount_minor,
        transaction_type='EXPENSE',
        transaction_date=txn_date,
        description=description,
        merchant=data.get('merchant', ''),
        notes=data.get('notes', f"Trip: {trip.name}"),
        trip_id=trip.id
    )
    db.session.add(new_txn)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Expense recorded and linked to trip.',
        'trip': trip.to_dict(),
        'transaction': new_txn.to_dict()
    }), 201


@trips_bp.route('/api/trips/<int:trip_id>/transactions/<int:txn_id>', methods=['DELETE'])
@login_required
def api_unlink_trip_transaction(trip_id, txn_id):
    user = g.current_user
    trip = Trip.query.filter_by(id=trip_id, user_id=user.id).first()
    if not trip:
        return jsonify({'success': False, 'error': 'Trip not found.'}), 404

    txn = Transaction.query.filter_by(id=txn_id, user_id=user.id, trip_id=trip.id).first()
    if not txn:
        return jsonify({'success': False, 'error': 'Transaction not linked to this trip.'}), 404

    # Unlink without deleting the transaction
    txn.trip_id = None
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Transaction unlinked from trip.',
        'trip': trip.to_dict()
    })
