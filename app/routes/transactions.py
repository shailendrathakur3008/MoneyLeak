"""
Transaction management routes and REST API (CRUD, Search, Filter, Pagination).
"""
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, g, flash, redirect, url_for
from app.extensions import db
from app.routes.auth import login_required
from app.models.transaction import Transaction
from app.models.category import Category
from app.routes.categories import is_category_compatible
from app.services.money import to_minor_units, format_money

transactions_bp = Blueprint('transactions', __name__)

ALLOWED_TYPES = {'EXPENSE', 'INCOME', 'REFUND', 'TRANSFER', 'SAVINGS_CONTRIBUTION', 'DEBT_REPAYMENT'}


@transactions_bp.route('/transactions')
@login_required
def view_transactions():
    user = g.current_user
    categories = Category.query.filter(
        (Category.user_id == user.id) | (Category.user_id.is_(None)),
        Category.is_active.is_(True)
    ).order_by(Category.name.asc()).all()
    return render_template('transactions.html', user=user, categories=categories)


@transactions_bp.route('/api/transactions', methods=['GET'])
@login_required
def api_get_transactions():
    user = g.current_user
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id')
    txn_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', 'date_desc')

    query = Transaction.query.filter_by(user_id=user.id)

    # Filters
    if category_id and category_id.isdigit():
        query = query.filter_by(category_id=int(category_id))

    if txn_type and txn_type.upper() in ALLOWED_TYPES:
        query = query.filter_by(transaction_type=txn_type.upper())

    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date >= sd)
        except ValueError:
            pass

    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date <= ed)
        except ValueError:
            pass

    if search:
        term = f"%{search}%"
        query = query.filter(
            (Transaction.description.ilike(term)) |
            (Transaction.merchant.ilike(term)) |
            (Transaction.notes.ilike(term))
        )

    # Sorting
    if sort_by == 'date_asc':
        query = query.order_by(Transaction.transaction_date.asc(), Transaction.id.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount_minor_units.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount_minor_units.asc())
    else:
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for t in pagination.items:
        data = t.to_dict()
        data['formatted_amount'] = format_money(t.amount_minor_units, user.currency)
        results.append(data)

    return jsonify({
        'success': True,
        'transactions': results,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@transactions_bp.route('/api/transactions', methods=['POST'])
@login_required
def api_create_transaction():
    user = g.current_user
    data = request.get_json() or {}

    amount_raw = data.get('amount')
    txn_type = (data.get('transaction_type') or 'EXPENSE').upper()
    cat_id = data.get('category_id')
    txn_date_raw = data.get('transaction_date')
    description = (data.get('description') or '').strip()
    merchant = (data.get('merchant') or '').strip()
    notes = (data.get('notes') or '').strip()

    # Validations
    if not amount_raw or not description:
        return jsonify({'success': False, 'error': 'Amount and Description are required.'}), 400

    try:
        amount_minor = to_minor_units(amount_raw, user.currency)
        if amount_minor <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid monetary amount.'}), 400

    if txn_type not in ALLOWED_TYPES:
        return jsonify({'success': False, 'error': f'Invalid transaction type. Must be one of {list(ALLOWED_TYPES)}.'}), 400

    try:
        t_date = datetime.strptime(txn_date_raw, '%Y-%m-%d').date() if txn_date_raw else date.today()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD).'}), 400

    # Category ownership & compatibility validation
    category = None
    if cat_id:
        category = Category.query.filter(
            (Category.id == cat_id) &
            ((Category.user_id == user.id) | (Category.user_id.is_(None)))
        ).first()
        if not category:
            return jsonify({'success': False, 'error': 'Selected category was not found or not owned.'}), 400
        if not category.is_active or category.is_archived:
            return jsonify({'success': False, 'error': 'Archived or inactive categories cannot be selected for new transactions.'}), 400
        if not is_category_compatible(category, txn_type):
            return jsonify({'success': False, 'error': f"Category '{category.name}' is incompatible with transaction type {txn_type}."}), 400

        category.last_used_at = datetime.utcnow()

    new_txn = Transaction(
        user_id=user.id,
        category_id=category.id if category else None,
        amount_minor_units=amount_minor,
        transaction_type=txn_type,
        transaction_date=t_date,
        description=description,
        merchant=merchant,
        notes=notes
    )

    db.session.add(new_txn)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Transaction recorded successfully.',
        'transaction': new_txn.to_dict()
    }), 201


@transactions_bp.route('/api/transactions/<int:txn_id>', methods=['GET'])
@login_required
def api_get_single_transaction(txn_id):
    user = g.current_user
    txn = Transaction.query.filter_by(id=txn_id, user_id=user.id).first()
    if not txn:
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404
    data = txn.to_dict()
    data['formatted_amount'] = format_money(txn.amount_minor_units, user.currency)
    return jsonify({'success': True, 'transaction': data})


@transactions_bp.route('/api/transactions/<int:txn_id>', methods=['PATCH', 'PUT'])
@login_required
def api_update_transaction(txn_id):
    user = g.current_user
    txn = Transaction.query.filter_by(id=txn_id, user_id=user.id).first()
    if not txn:
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404

    data = request.get_json() or {}

    if 'amount' in data:
        try:
            amt_minor = to_minor_units(data['amount'], user.currency)
            if amt_minor <= 0:
                return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
            txn.amount_minor_units = amt_minor
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid amount.'}), 400

    target_type = txn.transaction_type
    if 'transaction_type' in data:
        t_type = data['transaction_type'].upper()
        if t_type not in ALLOWED_TYPES:
            return jsonify({'success': False, 'error': 'Invalid transaction type.'}), 400
        txn.transaction_type = t_type
        target_type = t_type

    if 'category_id' in data:
        c_id = data['category_id']
        if c_id:
            cat = Category.query.filter(
                (Category.id == c_id) &
                ((Category.user_id == user.id) | (Category.user_id.is_(None)))
            ).first()
            if not cat:
                return jsonify({'success': False, 'error': 'Invalid category.'}), 400
            if not cat.is_active or cat.is_archived:
                return jsonify({'success': False, 'error': 'Archived or inactive categories cannot be selected.'}), 400
            if not is_category_compatible(cat, target_type):
                return jsonify({'success': False, 'error': f"Category '{cat.name}' is incompatible with transaction type {target_type}."}), 400
            txn.category_id = cat.id
            cat.last_used_at = datetime.utcnow()
        else:
            txn.category_id = None

    if 'transaction_date' in data and data['transaction_date']:
        try:
            txn.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format.'}), 400

    if 'description' in data:
        txn.description = data['description'].strip()
    if 'merchant' in data:
        txn.merchant = data['merchant'].strip()
    if 'notes' in data:
        txn.notes = data['notes'].strip()

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Transaction updated successfully.',
        'transaction': txn.to_dict()
    })


@transactions_bp.route('/api/transactions/<int:txn_id>', methods=['DELETE'])
@login_required
def api_delete_transaction(txn_id):
    user = g.current_user
    txn = Transaction.query.filter_by(id=txn_id, user_id=user.id).first()
    if not txn:
        return jsonify({'success': False, 'error': 'Transaction not found or not owned.'}), 404

    db.session.delete(txn)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Transaction deleted.'})
