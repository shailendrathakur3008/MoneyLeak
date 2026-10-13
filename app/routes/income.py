"""
Income management REST API endpoints.
"""
from datetime import datetime, date
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.routes.auth import login_required
from app.models.income import IncomeRecord
from app.services.money import to_minor_units, format_money

income_bp = Blueprint('income', __name__)


@income_bp.route('/api/income', methods=['GET'])
@login_required
def get_incomes():
    user = g.current_user
    records = IncomeRecord.query.filter_by(user_id=user.id).order_by(IncomeRecord.received_date.desc()).all()
    results = []
    for inc in records:
        d = inc.to_dict()
        d['formatted_amount'] = format_money(inc.amount_minor_units, user.currency)
        results.append(d)
    return jsonify({'success': True, 'incomes': results})


@income_bp.route('/api/income', methods=['POST'])
@login_required
def create_income():
    user = g.current_user
    data = request.get_json() or {}

    amount_raw = data.get('amount')
    source = (data.get('income_source') or '').strip()
    date_raw = data.get('received_date')
    notes = (data.get('notes') or '').strip()

    if not amount_raw or not source:
        return jsonify({'success': False, 'error': 'Amount and Income Source are required.'}), 400

    try:
        amount_minor = to_minor_units(amount_raw, user.currency)
        if amount_minor <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid amount.'}), 400

    try:
        rec_date = datetime.strptime(date_raw, '%Y-%m-%d').date() if date_raw else date.today()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD).'}), 400

    new_income = IncomeRecord(
        user_id=user.id,
        amount_minor_units=amount_minor,
        income_source=source,
        received_date=rec_date,
        notes=notes
    )

    db.session.add(new_income)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Income record added successfully.',
        'income': new_income.to_dict()
    }), 201


@income_bp.route('/api/income/<int:inc_id>', methods=['PATCH', 'PUT'])
@login_required
def update_income(inc_id):
    user = g.current_user
    inc = IncomeRecord.query.filter_by(id=inc_id, user_id=user.id).first()
    if not inc:
        return jsonify({'success': False, 'error': 'Income record not found.'}), 404

    data = request.get_json() or {}

    if 'amount' in data:
        try:
            inc.amount_minor_units = to_minor_units(data['amount'], user.currency)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid amount.'}), 400

    if 'income_source' in data:
        inc.income_source = data['income_source'].strip()

    if 'received_date' in data and data['received_date']:
        try:
            inc.received_date = datetime.strptime(data['received_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format.'}), 400

    if 'notes' in data:
        inc.notes = data['notes'].strip()

    db.session.commit()
    return jsonify({'success': True, 'income': inc.to_dict()})


@income_bp.route('/api/income/<int:inc_id>', methods=['DELETE'])
@login_required
def delete_income(inc_id):
    user = g.current_user
    inc = IncomeRecord.query.filter_by(id=inc_id, user_id=user.id).first()
    if not inc:
        return jsonify({'success': False, 'error': 'Income record not found.'}), 404

    db.session.delete(inc)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Income record deleted.'})
