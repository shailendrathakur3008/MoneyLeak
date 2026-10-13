"""
Category management REST API endpoints:
Custom categories, Quick Access prioritized ordering, Default per transaction type,
Pinning, Reordering, and Archiving.
"""
from datetime import datetime, date
from flask import Blueprint, request, jsonify, g
from sqlalchemy import func
from app.extensions import db
from app.routes.auth import login_required
from app.models.category import Category, CategoryPreference
from app.models.transaction import Transaction
from app.services.money import to_minor_units, format_money

categories_bp = Blueprint('categories', __name__)

ALLOWED_GROUPS = {'NEEDS', 'WANTS', 'SAVINGS', 'INCOME'}
ALLOWED_CATEGORY_TYPES = {
    'EXPENSE', 'INCOME', 'SAVINGS_CONTRIBUTION', 'INVESTMENT',
    'TRANSFER', 'DEBT_REPAYMENT', 'REFUND', 'ALL'
}


def is_category_compatible(cat: Category, txn_type: str) -> bool:
    """Check if a category is compatible with a given transaction type."""
    if not cat:
        return False
    cat_type = (cat.transaction_type or 'EXPENSE').upper()
    tt = (txn_type or 'EXPENSE').upper()

    if cat_type == 'ALL' or tt == 'ALL':
        return True
    if cat_type == tt:
        return True
    if tt == 'SAVINGS_CONTRIBUTION' and cat_type in ('SAVINGS_CONTRIBUTION', 'INVESTMENT'):
        return True
    if tt == 'DEBT_REPAYMENT' and cat_type in ('DEBT_REPAYMENT', 'EXPENSE'):
        return True
    if tt == 'REFUND' and cat_type in ('REFUND', 'EXPENSE'):
        return True
    return False


def check_duplicate_category(user_id: int, name: str, txn_type: str, exclude_id: int = None) -> bool:
    """
    Prevent duplicate category names within the same applicable transaction type,
    ignoring letter case and unnecessary whitespace.
    """
    clean_name = name.strip().lower()
    target_type = (txn_type or 'EXPENSE').upper()

    query = Category.query.filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None)),
        Category.is_archived.is_(False),
        func.lower(func.trim(Category.name)) == clean_name
    )
    if exclude_id:
        query = query.filter(Category.id != exclude_id)

    candidates = query.all()
    for cat in candidates:
        cat_type = (cat.transaction_type or 'EXPENSE').upper()
        if target_type == 'ALL' or cat_type == 'ALL' or cat_type == target_type:
            return True
        if target_type in ('SAVINGS_CONTRIBUTION', 'INVESTMENT') and cat_type in ('SAVINGS_CONTRIBUTION', 'INVESTMENT'):
            return True
    return False


def get_user_quick_access(user_id: int, txn_type: str):
    """
    Determine Quick Access order using the required 4-tier priority:
    1. Categories explicitly pinned by the user (respecting display_order).
    2. Frequently used categories based on recent transaction history (tx_count > 0).
    3. Recently used categories (last_used_at or most recent transaction).
    4. Remaining active default categories.
    """
    tt = (txn_type or 'EXPENSE').upper()

    # Query all active, non-archived categories available to user
    all_cats = Category.query.filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None)),
        Category.is_active.is_(True),
        Category.is_archived.is_(False)
    ).all()

    compatible_cats = [c for c in all_cats if is_category_compatible(c, tt)]
    comp_ids = {c.id for c in compatible_cats}

    # Tier 1: Pinned categories (ordered by user display_order ASC, then name ASC)
    pinned = [c for c in compatible_cats if c.is_pinned]
    pinned.sort(key=lambda c: (c.display_order if c.display_order is not None else 9999, c.name.lower()))
    pinned_ids = {c.id for c in pinned}

    unpinned = [c for c in compatible_cats if c.id not in pinned_ids]

    # Query transaction frequency and most recent date for this user and transaction type
    usage_stats = db.session.query(
        Transaction.category_id,
        func.count(Transaction.id).label('tx_count'),
        func.max(Transaction.transaction_date).label('max_date'),
        func.max(Transaction.created_at).label('max_created')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == tt,
        Transaction.category_id.isnot(None)
    ).group_by(Transaction.category_id).all()

    tx_count_map = {row.category_id: row.tx_count for row in usage_stats}
    tx_recent_map = {row.category_id: (row.max_date, row.max_created) for row in usage_stats}

    # Tier 2: Frequently used categories (tx_count > 0), ordered by count DESC, date DESC
    frequent = [c for c in unpinned if tx_count_map.get(c.id, 0) > 0]
    frequent.sort(key=lambda c: (
        tx_count_map.get(c.id, 0),
        tx_recent_map.get(c.id, (date.min, datetime.min))[0] or date.min,
        c.last_used_at or datetime.min
    ), reverse=True)
    frequent_ids = {c.id for c in frequent}

    # Tier 3: Recently used categories
    remaining_unpinned = [c for c in unpinned if c.id not in frequent_ids]
    recent = [c for c in remaining_unpinned if c.last_used_at is not None]
    recent.sort(key=lambda c: c.last_used_at or datetime.min, reverse=True)
    recent_ids = {c.id for c in recent}

    # Tier 4: Remaining active default categories (alphabetical or default display order)
    defaults = [c for c in remaining_unpinned if c.id not in recent_ids]
    defaults.sort(key=lambda c: (c.display_order if c.display_order is not None else 9999, c.name.lower()))

    ordered_quick = pinned + frequent + recent + defaults

    # Resolve default category:
    # Check 1: User's saved default in CategoryPreference
    pref = CategoryPreference.query.filter_by(user_id=user_id, transaction_type=tt).first()
    default_cat_id = None
    if pref and pref.default_category_id in comp_ids:
        default_cat_id = pref.default_category_id
    else:
        # Check category is_default flag
        for c in compatible_cats:
            if c.is_default:
                default_cat_id = c.id
                break

    # Check 2: If no default configured, select most recently used valid category
    if default_cat_id is None:
        most_recent_tx = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == tt,
            Transaction.category_id.isnot(None)
        ).order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).first()
        if most_recent_tx and most_recent_tx.category_id in comp_ids:
            default_cat_id = most_recent_tx.category_id
        else:
            cats_with_last = [c for c in compatible_cats if c.last_used_at]
            if cats_with_last:
                cats_with_last.sort(key=lambda c: c.last_used_at, reverse=True)
                default_cat_id = cats_with_last[0].id

    # Check 3: If neither exists, leave None (unselected)
    return ordered_quick, compatible_cats, default_cat_id


@categories_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    user = g.current_user
    txn_type = request.args.get('type')
    include_archived = request.args.get('include_archived', 'false').lower() in ('true', '1')

    query = Category.query.filter(
        (Category.user_id == user.id) | (Category.user_id.is_(None)),
        Category.is_active.is_(True)
    )
    if not include_archived:
        query = query.filter(Category.is_archived.is_(False))

    cats = query.order_by(Category.display_order.asc(), Category.name.asc()).all()

    if txn_type:
        cats = [c for c in cats if is_category_compatible(c, txn_type)]

    results = []
    for c in cats:
        d = c.to_dict()
        if c.monthly_budget_minor_units:
            d['monthly_budget_formatted'] = format_money(c.monthly_budget_minor_units, user.currency)
        else:
            d['monthly_budget_formatted'] = None
        results.append(d)

    return jsonify({'success': True, 'categories': results})


@categories_bp.route('/api/categories/quick-access', methods=['GET'])
@login_required
def get_quick_access_categories():
    user = g.current_user
    txn_type = request.args.get('type', 'EXPENSE')

    quick_list, all_compat, default_id = get_user_quick_access(user.id, txn_type)

    def format_cat(c):
        d = c.to_dict()
        if c.monthly_budget_minor_units:
            d['monthly_budget_formatted'] = format_money(c.monthly_budget_minor_units, user.currency)
        else:
            d['monthly_budget_formatted'] = None
        return d

    return jsonify({
        'success': True,
        'transaction_type': txn_type.upper(),
        'quick_access': [format_cat(c) for c in quick_list],
        'categories': [format_cat(c) for c in all_compat],
        'default_category_id': default_id
    })


@categories_bp.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    user = g.current_user
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    group = (data.get('budget_group') or 'WANTS').upper()
    txn_type = (data.get('transaction_type') or 'EXPENSE').upper()
    description = (data.get('description') or '').strip()
    icon = (data.get('icon') or 'tag').strip()
    color = (data.get('color') or '#161917').strip()
    is_pinned = bool(data.get('is_pinned', False))
    is_default = bool(data.get('is_default', False))
    display_order = int(data.get('display_order', 0))
    monthly_budget_raw = data.get('monthly_budget')

    if not name:
        return jsonify({'success': False, 'error': 'Category name is required.'}), 400

    if group not in ALLOWED_GROUPS:
        return jsonify({'success': False, 'error': f'Budget group must be one of {list(ALLOWED_GROUPS)}.'}), 400

    if txn_type not in ALLOWED_CATEGORY_TYPES:
        return jsonify({'success': False, 'error': f'Transaction type must be one of {list(ALLOWED_CATEGORY_TYPES)}.'}), 400

    # Prevent duplicate category name per transaction type
    if check_duplicate_category(user.id, name, txn_type):
        return jsonify({
            'success': False,
            'error': f"A category named '{name}' already exists for transaction type {txn_type}."
        }), 400

    monthly_budget_minor = None
    if monthly_budget_raw:
        try:
            monthly_budget_minor = to_minor_units(monthly_budget_raw, user.currency)
        except Exception:
            pass

    new_cat = Category(
        user_id=user.id,
        name=name,
        budget_group=group,
        transaction_type=txn_type,
        description=description,
        icon=icon,
        color=color,
        monthly_budget_minor_units=monthly_budget_minor,
        is_active=True,
        is_pinned=is_pinned,
        display_order=display_order,
        is_default=is_default,
        is_archived=False
    )
    db.session.add(new_cat)
    db.session.flush()

    if is_default:
        # Update or create CategoryPreference
        pref = CategoryPreference.query.filter_by(user_id=user.id, transaction_type=txn_type).first()
        if not pref:
            pref = CategoryPreference(user_id=user.id, transaction_type=txn_type, default_category_id=new_cat.id)
            db.session.add(pref)
        else:
            pref.default_category_id = new_cat.id

        # Clear other default flags for user
        Category.query.filter(
            Category.user_id == user.id,
            Category.transaction_type == txn_type,
            Category.id != new_cat.id
        ).update({'is_default': False})

    db.session.commit()
    return jsonify({'success': True, 'category': new_cat.to_dict()}), 201


@categories_bp.route('/api/categories/<int:cat_id>', methods=['PATCH', 'PUT'])
@login_required
def update_category(cat_id):
    user = g.current_user
    cat = Category.query.filter(
        Category.id == cat_id,
        ((Category.user_id == user.id) | (Category.user_id.is_(None)))
    ).first()
    if not cat:
        return jsonify({'success': False, 'error': 'Category not found.'}), 404

    # If it's a system category and user wants to modify it, clone as user category or update user preference
    if cat.user_id is None:
        cat = Category(
            user_id=user.id,
            name=cat.name,
            budget_group=cat.budget_group,
            transaction_type=cat.transaction_type,
            description=cat.description,
            icon=cat.icon,
            color=cat.color,
            monthly_budget_minor_units=cat.monthly_budget_minor_units,
            is_active=True,
            is_pinned=cat.is_pinned,
            display_order=cat.display_order,
            is_default=cat.is_default,
            is_archived=False
        )
        db.session.add(cat)
        db.session.flush()

    data = request.get_json() or {}

    new_name = (data.get('name') or cat.name).strip()
    new_type = (data.get('transaction_type') or cat.transaction_type).upper()

    if 'name' in data or 'transaction_type' in data:
        if not new_name:
            return jsonify({'success': False, 'error': 'Category name cannot be empty.'}), 400
        if check_duplicate_category(user.id, new_name, new_type, exclude_id=cat.id):
            return jsonify({
                'success': False,
                'error': f"A category named '{new_name}' already exists for transaction type {new_type}."
            }), 400
        cat.name = new_name
        cat.transaction_type = new_type

    if 'budget_group' in data and data['budget_group'].upper() in ALLOWED_GROUPS:
        cat.budget_group = data['budget_group'].upper()

    if 'description' in data:
        cat.description = data['description'].strip()

    if 'icon' in data:
        cat.icon = data['icon'].strip()

    if 'color' in data:
        cat.color = data['color'].strip()

    if 'is_pinned' in data:
        cat.is_pinned = bool(data['is_pinned'])

    if 'display_order' in data:
        cat.display_order = int(data['display_order'])

    if 'is_archived' in data:
        cat.is_archived = bool(data['is_archived'])

    if 'is_active' in data:
        cat.is_active = bool(data['is_active'])

    if 'is_default' in data:
        cat.is_default = bool(data['is_default'])
        target_t = cat.transaction_type or 'EXPENSE'
        pref = CategoryPreference.query.filter_by(user_id=user.id, transaction_type=target_t).first()
        if cat.is_default:
            if not pref:
                pref = CategoryPreference(user_id=user.id, transaction_type=target_t, default_category_id=cat.id)
                db.session.add(pref)
            else:
                pref.default_category_id = cat.id
            Category.query.filter(
                Category.user_id == user.id,
                Category.transaction_type == target_t,
                Category.id != cat.id
            ).update({'is_default': False})
        else:
            if pref and pref.default_category_id == cat.id:
                pref.default_category_id = None

    if 'monthly_budget' in data:
        if data['monthly_budget']:
            cat.monthly_budget_minor_units = to_minor_units(data['monthly_budget'], user.currency)
        else:
            cat.monthly_budget_minor_units = None

    db.session.commit()
    return jsonify({'success': True, 'category': cat.to_dict()})


@categories_bp.route('/api/categories/defaults', methods=['POST'])
@login_required
def set_default_category():
    user = g.current_user
    data = request.get_json() or {}
    txn_type = (data.get('transaction_type') or 'EXPENSE').upper()
    cat_id = data.get('category_id')

    if cat_id:
        cat = Category.query.filter(
            Category.id == cat_id,
            ((Category.user_id == user.id) | (Category.user_id.is_(None)))
        ).first()
        if not cat:
            return jsonify({'success': False, 'error': 'Category not found.'}), 404
        if not cat.is_active or cat.is_archived:
            return jsonify({'success': False, 'error': 'Cannot set inactive or archived category as default.'}), 400
        if not is_category_compatible(cat, txn_type):
            return jsonify({'success': False, 'error': 'Category is incompatible with this transaction type.'}), 400

        pref = CategoryPreference.query.filter_by(user_id=user.id, transaction_type=txn_type).first()
        if not pref:
            pref = CategoryPreference(user_id=user.id, transaction_type=txn_type, default_category_id=cat.id)
            db.session.add(pref)
        else:
            pref.default_category_id = cat.id

        Category.query.filter(
            Category.user_id == user.id,
            Category.transaction_type == txn_type
        ).update({'is_default': False})
        cat.is_default = True
    else:
        # Clear default
        pref = CategoryPreference.query.filter_by(user_id=user.id, transaction_type=txn_type).first()
        if pref:
            pref.default_category_id = None
        Category.query.filter(
            Category.user_id == user.id,
            Category.transaction_type == txn_type
        ).update({'is_default': False})

    db.session.commit()
    return jsonify({'success': True, 'message': f'Default category updated for {txn_type}.'})


@categories_bp.route('/api/categories/reorder', methods=['POST'])
@login_required
def reorder_categories():
    user = g.current_user
    data = request.get_json() or {}
    ordered_ids = data.get('ordered_ids') or []

    for index, cid in enumerate(ordered_ids):
        cat = Category.query.filter_by(id=cid, user_id=user.id).first()
        if cat:
            cat.display_order = index + 1
            cat.is_pinned = True

    db.session.commit()
    return jsonify({'success': True, 'message': 'Category order updated successfully.'})


@categories_bp.route('/api/categories/<int:cat_id>/archive', methods=['POST'])
@login_required
def archive_category(cat_id):
    user = g.current_user
    cat = Category.query.filter(
        Category.id == cat_id,
        ((Category.user_id == user.id) | (Category.user_id.is_(None)))
    ).first()
    if not cat:
        return jsonify({'success': False, 'error': 'Category not found.'}), 404

    cat.is_archived = True
    cat.is_pinned = False
    if cat.is_default:
        cat.is_default = False
        pref = CategoryPreference.query.filter_by(user_id=user.id, transaction_type=cat.transaction_type).first()
        if pref and pref.default_category_id == cat.id:
            pref.default_category_id = None

    db.session.commit()
    return jsonify({'success': True, 'message': f"Category '{cat.name}' archived."})


@categories_bp.route('/api/categories/<int:cat_id>/unarchive', methods=['POST'])
@login_required
def unarchive_category(cat_id):
    user = g.current_user
    cat = Category.query.filter(
        Category.id == cat_id,
        ((Category.user_id == user.id) | (Category.user_id.is_(None)))
    ).first()
    if not cat:
        return jsonify({'success': False, 'error': 'Category not found.'}), 404

    cat.is_archived = False
    db.session.commit()
    return jsonify({'success': True, 'message': f"Category '{cat.name}' restored."})


@categories_bp.route('/api/categories/<int:cat_id>', methods=['DELETE'])
@login_required
def delete_category(cat_id):
    user = g.current_user
    cat = Category.query.filter_by(id=cat_id, user_id=user.id).first()
    if not cat:
        return jsonify({'success': False, 'error': 'Category not found or cannot delete system category.'}), 404

    cat.is_active = False
    cat.is_archived = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Category deactivated.'})
