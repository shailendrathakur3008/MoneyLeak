from datetime import date
from app.extensions import db
from app.models.transaction import Transaction
from app.models.goal import SavingsGoal


def test_unauthenticated_access_rejected(client):
    res = client.get('/api/dashboard')
    assert res.status_code == 401

    res_txn = client.get('/api/transactions')
    assert res_txn.status_code == 401

    res_page = client.get('/dashboard')
    assert res_page.status_code == 302
    assert '/login' in res_page.headers['Location']


def test_user_data_isolation(client, test_user, second_user):
    # Create transaction owned by second_user (Bob)
    bob_txn = Transaction(
        user_id=second_user.id,
        amount_minor_units=500000,
        transaction_type='EXPENSE',
        transaction_date=date.today(),
        description="Bob's Private Secret Purchase"
    )
    db.session.add(bob_txn)
    db.session.commit()

    # Log in as test_user (Alice)
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Alice tries to GET Bob's transaction
    res = client.get(f'/api/transactions/{bob_txn.id}')
    assert res.status_code == 404

    # Alice tries to DELETE Bob's transaction
    res_del = client.delete(f'/api/transactions/{bob_txn.id}')
    assert res_del.status_code == 404

    # Bob's transaction must still exist in DB unmodified
    assert Transaction.query.get(bob_txn.id) is not None
