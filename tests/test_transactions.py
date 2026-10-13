from datetime import date
from app.models.transaction import Transaction


def test_transaction_crud_api(client, test_user):
    # Log in as test_user
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # 1. CREATE Transaction
    res = client.post('/api/transactions', json={
        'amount': '1250.50',
        'transaction_type': 'EXPENSE',
        'category_id': test_user.categories.first().id,
        'transaction_date': date.today().isoformat(),
        'description': 'Supermarket Groceries',
        'merchant': 'Nature Basket',
        'notes': 'Weekly basket'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    txn_id = data['transaction']['id']
    assert data['transaction']['amount_minor_units'] == 125050

    # 2. READ Transaction
    res_get = client.get(f'/api/transactions/{txn_id}')
    assert res_get.status_code == 200
    assert res_get.get_json()['transaction']['description'] == 'Supermarket Groceries'

    # 3. UPDATE Transaction
    res_patch = client.patch(f'/api/transactions/{txn_id}', json={
        'amount': '1500.00',
        'description': 'Updated Supermarket Groceries'
    })
    assert res_patch.status_code == 200
    assert res_patch.get_json()['transaction']['amount_minor_units'] == 150000

    # 4. DELETE Transaction
    res_del = client.delete(f'/api/transactions/{txn_id}')
    assert res_del.status_code == 200

    # Verify deleted
    assert Transaction.query.get(txn_id) is None


def test_transaction_validation_errors(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Missing amount
    res = client.post('/api/transactions', json={
        'description': 'Coffee'
    })
    assert res.status_code == 400

    # Negative amount
    res2 = client.post('/api/transactions', json={
        'amount': '-100',
        'description': 'Invalid negative'
    })
    assert res2.status_code == 400

    # Invalid type
    res3 = client.post('/api/transactions', json={
        'amount': '100',
        'transaction_type': 'ILLEGAL_TYPE',
        'description': 'Invalid type'
    })
    assert res3.status_code == 400
