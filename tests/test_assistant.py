"""
Comprehensive tests for Financial Assistant Page, Assistant Modules,
and Smart Finance Chatbot API.
"""
import pytest
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.services.budget_engine import seed_default_categories


def test_assistant_page_requires_auth(client):
    """Test that /assistant requires user login."""
    res = client.get('/assistant')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


def test_assistant_page_renders_for_authenticated_user(client, test_user):
    """Test that /assistant renders successfully with all modules and quick actions."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/assistant')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Your Financial Assistant' in html
    assert 'Available Assistant Modules' in html
    assert 'Quick Actions & Workflows' in html
    assert 'Spending Leak Detector' in html
    assert '50/30/20 Budget Allocator' in html
    assert 'Investment Scheme Matcher' in html
    assert 'data-lucide' in html


def test_api_chat_validation_and_auth(client, test_user):
    """Test chat API validation: auth, empty message, and length limit."""
    # 1. Unauthenticated
    res_unauth = client.post('/api/assistant/chat', json={'message': 'Hello'})
    assert res_unauth.status_code in (302, 401)

    # 2. Authenticated
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Empty message
    res_empty = client.post('/api/assistant/chat', json={'message': ''})
    assert res_empty.status_code == 400
    assert res_empty.get_json()['success'] is False

    # Oversized message (> 1000 chars)
    res_long = client.post('/api/assistant/chat', json={'message': 'a' * 1001})
    assert res_long.status_code == 400
    assert res_long.get_json()['success'] is False


def test_api_chat_answers_spending_with_actual_data(client, app, test_user):
    """Test that chat accurately reflects real user transaction data."""
    with app.app_context():
        # Add an expense transaction
        cat = Category.query.filter_by(user_id=test_user.id, name='Groceries').first()
        if not cat:
            cat = Category(name='Groceries', budget_group='NEEDS', user_id=test_user.id)
            db.session.add(cat)
            db.session.commit()

        txn = Transaction(
            user_id=test_user.id,
            category_id=cat.id,
            amount_minor_units=450000,  # ₹4,500.00
            transaction_type='EXPENSE',
            description='Supermarket run'
        )
        db.session.add(txn)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.post('/api/assistant/chat', json={'message': 'How much did I spend this month?'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'response' in data
    assert '4,500' in data['response']
    assert 'Needs' in data['response']
    assert len(data['actions']) > 0


def test_api_chat_navigation_and_troubleshooting(client, test_user):
    """Test that chatbot returns step-by-step navigation and action links."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Navigation question
    res_nav = client.post('/api/assistant/chat', json={'message': 'Where is the investment calculator?'})
    assert res_nav.status_code == 200
    data_nav = res_nav.get_json()
    assert data_nav['success'] is True
    assert '/calculator' in [a['url'] for a in data_nav['actions']] or 'calculator' in data_nav['response'].lower()

    # Troubleshooting question
    res_trouble = client.post('/api/assistant/chat', json={'message': 'My transactions are missing, how do I troubleshoot?'})
    assert res_trouble.status_code == 200
    data_trouble = res_trouble.get_json()
    assert data_trouble['success'] is True
    assert 'troubleshoot' in data_trouble['response'].lower() or 'filter' in data_trouble['response'].lower()


def test_api_chat_user_data_isolation(client, app, test_user, second_user):
    """Ensure user data is strictly isolated: Bob cannot see Alice's numbers."""
    with app.app_context():
        # Alice spends ₹12,000
        cat_alice = Category(name='Alice Unique Cat', budget_group='WANTS', user_id=test_user.id)
        db.session.add(cat_alice)
        db.session.flush()
        txn_alice = Transaction(
            user_id=test_user.id,
            category_id=cat_alice.id,
            amount_minor_units=1200000,
            transaction_type='EXPENSE',
            description='Alice Luxury Shopping'
        )
        db.session.add(txn_alice)

        # Bob spends ₹500
        cat_bob = Category(name='Bob Unique Cat', budget_group='NEEDS', user_id=second_user.id)
        db.session.add(cat_bob)
        db.session.flush()
        txn_bob = Transaction(
            user_id=second_user.id,
            category_id=cat_bob.id,
            amount_minor_units=50000,
            transaction_type='EXPENSE',
            description='Bob Small Item'
        )
        db.session.add(txn_bob)
        db.session.commit()

    # Query as Bob
    with client.session_transaction() as sess:
        sess['user_id'] = second_user.id

    res_bob = client.post('/api/assistant/chat', json={'message': 'How much did I spend this month?'})
    data_bob = res_bob.get_json()
    assert '12,000' not in data_bob['response']
    assert 'Alice Unique Cat' not in data_bob['response']
    assert '500' in data_bob['response']


def test_assistant_modules_execution(client, test_user):
    """Test that all assistant modules execute and return valid metrics."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    module_ids = [
        'leak_detector',
        'leak_trimmer',
        'budget_analyzer',
        'cashflow_surplus',
        'expense_breakdown',
        'goals_tracker',
        'investment_matcher',
        'future_calculator',
        'health_audit'
    ]

    for mod_id in module_ids:
        res = client.post(f'/api/assistant/module/{mod_id}/run')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        result = data['result']
        assert result['module_id'] == mod_id
        assert 'metric_highlight' in result
        assert 'title' in result
        assert 'details' in result
        assert len(result['details']) > 0
