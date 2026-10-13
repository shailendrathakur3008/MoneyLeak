"""
Comprehensive Acceptance Tests for Custom Categories, Quick Access, Default Selections,
Pinning, Reordering, Archival, and Transaction-Type Compatibility.
"""
from datetime import date, datetime
from app.extensions import db
from app.models.category import Category, CategoryPreference
from app.models.transaction import Transaction


def test_default_categories_remain_available(client, test_user):
    """1. Existing default categories remain available."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/api/categories')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    names = [c['name'] for c in data['categories']]
    assert 'Essential Groceries' in names
    assert 'Housing & Rent' in names
    assert 'Dining Out & Cafes' in names


def test_custom_category_creation_and_dropdown(client, test_user):
    """2. Custom categories appear in the appropriate dropdown and support duplicate prevention."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Create custom expense category
    res = client.post('/api/categories', json={
        'name': 'Art Supplies',
        'budget_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'description': 'Paints and canvases'
    })
    assert res.status_code == 201
    cat_id = res.get_json()['category']['id']

    # Appears in dropdown for EXPENSE
    res_get = client.get('/api/categories?type=EXPENSE')
    assert res_get.status_code == 200
    names = [c['name'] for c in res_get.get_json()['categories']]
    assert 'Art Supplies' in names

    # Does not appear in incompatible type dropdown (e.g. INCOME)
    res_income = client.get('/api/categories?type=INCOME')
    names_income = [c['name'] for c in res_income.get_json()['categories']]
    assert 'Art Supplies' not in names_income

    # Duplicate check: ignoring letter case and unnecessary whitespace
    res_dup = client.post('/api/categories', json={
        'name': '  art supplies  ',
        'budget_group': 'WANTS',
        'transaction_type': 'EXPENSE'
    })
    assert res_dup.status_code == 400
    assert 'already exists' in res_dup.get_json()['error'].lower()


def test_saved_default_preselection_and_fallback(client, test_user):
    """3. The saved default category is preselected correctly, with recent-usage fallback."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    groceries = Category.query.filter_by(user_id=test_user.id, name='Essential Groceries').first()
    dining = Category.query.filter_by(user_id=test_user.id, name='Dining Out & Cafes').first()
    assert groceries is not None
    assert dining is not None

    # Step A: No default and no transactions -> default_category_id is None
    res = client.get('/api/categories/quick-access?type=EXPENSE')
    assert res.status_code == 200
    # Before transactions or default, might be None
    assert res.get_json()['default_category_id'] is None

    # Step B: Record a transaction with Dining Out & Cafes -> fallback selects most recent
    txn = Transaction(
        user_id=test_user.id,
        category_id=dining.id,
        amount_minor_units=50000,
        transaction_type='EXPENSE',
        transaction_date=date.today(),
        description='Lunch at cafe'
    )
    db.session.add(txn)
    db.session.commit()

    res_recent = client.get('/api/categories/quick-access?type=EXPENSE')
    assert res_recent.status_code == 200
    assert res_recent.get_json()['default_category_id'] == dining.id

    # Step C: Explicit default configured -> overrides recent transaction
    res_set_default = client.post('/api/categories/defaults', json={
        'transaction_type': 'EXPENSE',
        'category_id': groceries.id
    })
    assert res_set_default.status_code == 200

    res_default = client.get('/api/categories/quick-access?type=EXPENSE')
    assert res_default.status_code == 200
    assert res_default.get_json()['default_category_id'] == groceries.id


def test_quick_access_priority_order_and_adaptation(client, test_user):
    """6 & 7. Users can pin, unpin, reorder; Quick Access prioritizes Pinned -> Frequent -> Recent -> Defaults."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    groceries = Category.query.filter_by(user_id=test_user.id, name='Essential Groceries').first()
    dining = Category.query.filter_by(user_id=test_user.id, name='Dining Out & Cafes').first()
    fuel = Category.query.filter_by(user_id=test_user.id, name='Essential Commute & Fuel').first()

    # Create transactions: Dining has 5 transactions, Fuel has 2 transactions
    for _ in range(5):
        db.session.add(Transaction(
            user_id=test_user.id,
            category_id=dining.id,
            amount_minor_units=20000,
            transaction_type='EXPENSE',
            transaction_date=date.today(),
            description='Dining out'
        ))
    for _ in range(2):
        db.session.add(Transaction(
            user_id=test_user.id,
            category_id=fuel.id,
            amount_minor_units=15000,
            transaction_type='EXPENSE',
            transaction_date=date.today(),
            description='Fuel refill'
        ))
    db.session.commit()

    # Pin Groceries (even though 0 transactions, pinned must be Tier 1)
    client.patch(f'/api/categories/{groceries.id}', json={'is_pinned': True, 'display_order': 1})

    res = client.get('/api/categories/quick-access?type=EXPENSE')
    assert res.status_code == 200
    qa_list = res.get_json()['quick_access']
    qa_ids = [c['id'] for c in qa_list]

    # Groceries (Pinned) is #1
    assert qa_ids[0] == groceries.id
    # Dining (5 tx) comes before Fuel (2 tx) in Tier 2
    assert qa_ids.index(dining.id) < qa_ids.index(fuel.id)

    # Reorder pinned: Pin Fuel as #1, Groceries as #2
    client.post('/api/categories/reorder', json={'ordered_ids': [fuel.id, groceries.id]})

    res_reordered = client.get('/api/categories/quick-access?type=EXPENSE')
    reordered_ids = [c['id'] for c in res_reordered.get_json()['quick_access']]
    assert reordered_ids[0] == fuel.id
    assert reordered_ids[1] == groceries.id


def test_transaction_type_changes_remove_incompatible_selections(client, test_user):
    """8. Transaction-type changes validate compatibility and prevent incompatible saves."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    groceries = Category.query.filter_by(user_id=test_user.id, name='Essential Groceries').first()
    assert groceries.transaction_type == 'EXPENSE'

    # Try saving an INCOME transaction with an EXPENSE category -> rejected
    res_incompatible = client.post('/api/transactions', json={
        'amount': '5000.00',
        'transaction_type': 'INCOME',
        'category_id': groceries.id,
        'transaction_date': date.today().isoformat(),
        'description': 'Freelance payment'
    })
    assert res_incompatible.status_code == 400
    assert 'incompatible' in res_incompatible.get_json()['error'].lower()

    # Valid transaction with compatible type succeeds
    res_valid = client.post('/api/transactions', json={
        'amount': '500.00',
        'transaction_type': 'EXPENSE',
        'category_id': groceries.id,
        'transaction_date': date.today().isoformat(),
        'description': 'Milk & Vegetables'
    })
    assert res_valid.status_code == 201


def test_archived_category_behavior(client, test_user):
    """10 & 11. Archived categories cannot be selected for new transactions, existing transactions retain category."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Create category and log an existing transaction
    res_c = client.post('/api/categories', json={
        'name': 'Old Vintage Subscriptions',
        'budget_group': 'WANTS',
        'transaction_type': 'EXPENSE'
    })
    cat_id = res_c.get_json()['category']['id']

    res_t = client.post('/api/transactions', json={
        'amount': '299.00',
        'transaction_type': 'EXPENSE',
        'category_id': cat_id,
        'transaction_date': date.today().isoformat(),
        'description': 'Magazine subscription'
    })
    assert res_t.status_code == 201
    txn_id = res_t.get_json()['transaction']['id']

    # Archive the category
    res_arch = client.post(f'/api/categories/{cat_id}/archive')
    assert res_arch.status_code == 200

    # 1. Not in active categories list
    res_list = client.get('/api/categories?type=EXPENSE')
    active_ids = [c['id'] for c in res_list.get_json()['categories']]
    assert cat_id not in active_ids

    # 2. Cannot be selected for new transactions
    res_new_txn = client.post('/api/transactions', json={
        'amount': '150.00',
        'transaction_type': 'EXPENSE',
        'category_id': cat_id,
        'transaction_date': date.today().isoformat(),
        'description': 'New transaction with archived cat'
    })
    assert res_new_txn.status_code == 400
    assert 'archived' in res_new_txn.get_json()['error'].lower()

    # 3. Existing transaction preserves original category association
    res_get_txn = client.get(f'/api/transactions/{txn_id}')
    assert res_get_txn.status_code == 200
    txn_data = res_get_txn.get_json()['transaction']
    assert txn_data['category_id'] == cat_id
    assert txn_data['category_name'] == 'Old Vintage Subscriptions'


def test_persistence_of_categories_and_preferences(app, test_user):
    """9. Custom categories and preferences persist in database across operations."""
    with app.app_context():
        # Add custom category and set default preference directly in DB
        custom = Category(
            user_id=test_user.id,
            name='Side Project Cloud Hosting',
            budget_group='NEEDS',
            transaction_type='EXPENSE',
            is_pinned=True,
            display_order=5
        )
        db.session.add(custom)
        db.session.flush()

        pref = CategoryPreference(
            user_id=test_user.id,
            transaction_type='EXPENSE',
            default_category_id=custom.id
        )
        db.session.add(pref)
        db.session.commit()

        custom_id = custom.id

    # In a new session / context
    with app.app_context():
        loaded_cat = Category.query.get(custom_id)
        assert loaded_cat is not None
        assert loaded_cat.name == 'Side Project Cloud Hosting'
        assert loaded_cat.is_pinned is True
        assert loaded_cat.display_order == 5

        loaded_pref = CategoryPreference.query.filter_by(user_id=test_user.id, transaction_type='EXPENSE').first()
        assert loaded_pref is not None
        assert loaded_pref.default_category_id == custom_id
