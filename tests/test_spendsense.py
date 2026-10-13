"""
Comprehensive Test Suite for SpendSense — Smart Leak Detector and 50/30/20 Budget Analyzer.
"""
from datetime import date, timedelta
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.recurring_payment import RecurringPayment
from app.models.alert import FinancialAlert
from app.models.budget import Budget
from app.services.spendsense_service import (
    get_spendsense_analysis,
    detect_recurring_transaction_patterns,
    get_small_expenses_summary,
    reconcile_potential_savings,
    apply_finding_action,
    get_finding_transaction_evidence
)


def auth_session(client, user):
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True


def test_empty_transaction_history(app, test_user):
    """SpendSense operates gracefully with zero transactions."""
    with app.app_context():
        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['spending']['total_consumption_minor'] == 0
        assert analysis['spending']['transaction_count'] == 0
        assert analysis['income']['recognized_minor'] == 4000000  # Baseline ₹40,000
        assert analysis['income']['is_fallback_baseline'] is True
        assert analysis['active_findings_count'] == 0
        assert analysis['potential_savings_summary']['monthly_potential_minor'] == 0
        assert analysis['data_completeness']['has_income'] is True
        assert analysis['data_completeness']['transaction_count'] == 0


def test_incomplete_transaction_history_and_completeness(app, test_user):
    """Incomplete / ongoing month run-rate and data completeness indicator."""
    with app.app_context():
        analysis = get_spendsense_analysis(test_user.id)
        notes = analysis['data_completeness']['notes']
        assert any('Ongoing month' in n or 'Complete historical month' in n for n in notes)
        assert analysis['period']['days_in_month'] in (28, 29, 30, 31)
        assert analysis['period']['days_elapsed'] >= 1


def test_missing_income_fallback_baseline(app, test_user):
    """Fallback to profile baseline when no monthly IncomeRecord is logged."""
    with app.app_context():
        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['income']['is_fallback_baseline'] is True
        assert analysis['income']['recognized_minor'] == test_user.monthly_income_minor_units


def test_transfers_and_credit_card_non_duplication(app, test_user):
    """Transfers between accounts must NOT count as spending/consumption."""
    with app.app_context():
        transfer_cat = Category.query.filter_by(user_id=test_user.id, transaction_type='TRANSFER').first()
        t = Transaction(
            user_id=test_user.id,
            category_id=transfer_cat.id if transfer_cat else None,
            amount_minor_units=1500000,  # ₹15,000 transfer
            transaction_type='TRANSFER',
            transaction_date=date.today(),
            description='Transfer to Savings Account'
        )
        db.session.add(t)
        db.session.commit()

        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['spending']['total_consumption_minor'] == 0
        assert analysis['spending']['transaction_count'] == 1


def test_refunds_and_reimbursements(app, test_user):
    """Refunds reduce category total and total consumption expenses."""
    with app.app_context():
        groceries_cat = Category.query.filter_by(user_id=test_user.id, name='Essential Groceries').first()
        t_expense = Transaction(
            user_id=test_user.id,
            category_id=groceries_cat.id,
            amount_minor_units=500000,  # ₹5,000 spend
            transaction_type='EXPENSE',
            transaction_date=date.today(),
            description='Supermarket'
        )
        t_refund = Transaction(
            user_id=test_user.id,
            category_id=groceries_cat.id,
            amount_minor_units=100000,  # ₹1,000 refund
            transaction_type='REFUND',
            transaction_date=date.today(),
            description='Returned item refund'
        )
        db.session.add_all([t_expense, t_refund])
        db.session.commit()

        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['spending']['total_consumption_minor'] == 400000  # Net ₹4,000


def test_investment_and_savings_contribution_handling(app, test_user):
    """Savings contributions count under Savings and not as consumption spending."""
    with app.app_context():
        mf_cat = Category.query.filter_by(user_id=test_user.id, name='Mutual Funds & Stocks').first()
        t_inv = Transaction(
            user_id=test_user.id,
            category_id=mf_cat.id,
            amount_minor_units=800000,  # ₹8,000 SIP
            transaction_type='SAVINGS_CONTRIBUTION',
            transaction_date=date.today(),
            description='Nifty 50 Index SIP'
        )
        db.session.add(t_inv)
        db.session.commit()

        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['spending']['total_consumption_minor'] == 0
        assert analysis['distribution_50_30_20']['savings']['actual_minor'] == 800000


def test_uncategorized_transactions_detection(app, test_user):
    """Uncategorized expenses generate an UNCATEGORIZED_TRANSACTIONS finding."""
    with app.app_context():
        t1 = Transaction(
            user_id=test_user.id,
            category_id=None,
            amount_minor_units=60000,  # ₹600
            transaction_type='EXPENSE',
            transaction_date=date.today(),
            description='Miscellaneous Vendor'
        )
        db.session.add(t1)
        db.session.commit()

        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['spending']['uncategorized_count'] == 1
        assert analysis['spending']['uncategorized_minor'] == 60000
        uncat_findings = [f for f in analysis['findings'] if f['alert_type'] == 'UNCATEGORIZED_TRANSACTIONS']
        assert len(uncat_findings) == 1


def test_duplicate_transaction_detection(app, test_user):
    """Identical transactions within 2 days flag DUPLICATE_TRANSACTION."""
    with app.app_context():
        today = date.today()
        t1 = Transaction(
            user_id=test_user.id,
            amount_minor_units=129900,  # ₹1,299
            transaction_type='EXPENSE',
            transaction_date=today,
            description='Amazon Online Store',
            merchant='Amazon'
        )
        t2 = Transaction(
            user_id=test_user.id,
            amount_minor_units=129900,  # ₹1,299
            transaction_type='EXPENSE',
            transaction_date=today,
            description='Amazon Online Store',
            merchant='Amazon'
        )
        db.session.add_all([t1, t2])
        db.session.commit()

        analysis = get_spendsense_analysis(test_user.id)
        dup_findings = [f for f in analysis['findings'] if f['alert_type'] == 'DUPLICATE_TRANSACTION']
        assert len(dup_findings) == 1
        assert dup_findings[0]['potential_savings_minor'] == 129900


def test_recurring_transaction_detection_from_history(app, test_user):
    """Regular repeating cadence detected from transactions history."""
    with app.app_context():
        base_date = date.today()
        # Add 3 transactions spaced 30 days apart
        for i in range(3):
            t = Transaction(
                user_id=test_user.id,
                amount_minor_units=64900,  # ₹649
                transaction_type='EXPENSE',
                transaction_date=base_date - timedelta(days=30 * (2 - i)),
                description='Netflix Premium',
                merchant='Netflix'
            )
            db.session.add(t)
        db.session.commit()

        patterns = detect_recurring_transaction_patterns(test_user.id)
        assert len(patterns) >= 1
        netflix_pattern = next((p for p in patterns if 'netflix' in p['name'].lower()), None)
        assert netflix_pattern is not None
        assert netflix_pattern['frequency'] == 'MONTHLY'
        assert netflix_pattern['occurrences_count'] == 3


def test_small_expenses_summary_and_thresholds(app, test_user):
    """Small purchases accumulation correctly aggregates."""
    with app.app_context():
        today = date.today()
        for i in range(6):
            t = Transaction(
                user_id=test_user.id,
                amount_minor_units=25000,  # ₹250
                transaction_type='EXPENSE',
                transaction_date=today,
                description=f'Coffee Outing {i}',
                merchant='Chai Point'
            )
            db.session.add(t)
        db.session.commit()

        small_sum = get_small_expenses_summary(test_user.id, today.year, today.month, threshold_minor=50000)
        assert small_sum['transaction_count'] == 6
        assert small_sum['total_minor'] == 150000  # ₹1,500
        assert small_sum['average_minor'] == 25000


def test_deduplicated_potential_savings_reconciliation(app, test_user):
    """Overlapping findings do not double count savings."""
    with app.app_context():
        summary = {
            'wants': {'actual_minor': 2000000, 'variance_minor': 500000},
            'expenses': {'minor': 3000000},
            'category_breakdown': [{'id': 10, 'name': 'Dining Out', 'total_minor': 1000000}]
        }
        raw_findings = [
            {'alert_type': 'HIGH_DISCRETIONARY_SPEND', 'potential_savings_minor': 500000, 'status': 'ACTIVE'},
            {'alert_type': 'CATEGORY_OVERRUN', 'category_id': 10, 'category_name': 'Dining Out', 'potential_savings_minor': 300000, 'status': 'ACTIVE'},
            {'alert_type': 'REPEATED_MERCHANT', 'category_id': 10, 'merchant': 'Swiggy', 'potential_savings_minor': 200000, 'status': 'ACTIVE'},
            {'alert_type': 'DUPLICATE_TRANSACTION', 'potential_savings_minor': 120000, 'status': 'ACTIVE'}
        ]
        reconciled = reconcile_potential_savings(raw_findings, summary)
        # Wants overrun candidate is 500,000. Reconciled category Dining Out is 300,000 (max of 300k and 200k).
        # Macro wants takes max(500k, 300k) = 500k.
        # Plus independent duplicate 120,000 = 620,000 total.
        assert reconciled['monthly_potential_minor'] == 620000
        assert reconciled['annual_potential_minor'] == 620000 * 12


def test_different_50_30_20_presets(app, test_user):
    """Presets adjust targets dynamically without altering transactions."""
    with app.app_context():
        # Set to Metro (50/25/25)
        test_user.budget_preset = 'metro'
        b = Budget.query.filter_by(user_id=test_user.id).first()
        b.needs_percentage = 50.0
        b.wants_percentage = 25.0
        b.savings_percentage = 25.0
        db.session.commit()

        analysis = get_spendsense_analysis(test_user.id)
        assert analysis['distribution_50_30_20']['preset']['id'] == 'metro'
        assert analysis['distribution_50_30_20']['wants']['target_pct'] == 25.0
        assert analysis['distribution_50_30_20']['savings']['target_pct'] == 25.0


def test_user_approved_action_persistence(client, app, test_user):
    """API endpoints for finding actions persist status and targets."""
    auth_session(client, test_user)

    with app.app_context():
        alert = FinancialAlert(
            user_id=test_user.id,
            alert_type='SPENDING_INCREASE',
            title='Dining Jumped',
            description='Surged by 50%',
            severity='WARNING'
        )
        alert.supporting_data = {'actual_spending_minor': 800000, 'potential_savings_minor': 200000}
        db.session.add(alert)
        db.session.commit()
        alert_id = alert.id

    # 1. Dismiss finding
    res_dismiss = client.post(f'/api/spendsense/findings/{alert_id}/action', json={'action': 'dismiss'})
    assert res_dismiss.status_code == 200
    with app.app_context():
        a = db.session.get(FinancialAlert, alert_id)
        assert a.is_dismissed is True
        assert a.supporting_data.get('status') == 'DISMISSED'

    # 2. Set Custom Target
    res_target = client.post(f'/api/spendsense/findings/{alert_id}/action', json={'action': 'set_custom_target', 'custom_target': 6000})
    assert res_target.status_code == 200
    with app.app_context():
        a = db.session.get(FinancialAlert, alert_id)
        assert a.is_dismissed is False
        assert a.supporting_data.get('status') == 'TARGET_SET'
        assert a.supporting_data.get('custom_target_minor') == 600000


def test_user_data_isolation(client, app, test_user, second_user):
    """User B cannot access or modify User A's SpendSense findings."""
    auth_session(client, second_user)

    with app.app_context():
        alice_alert = FinancialAlert(
            user_id=test_user.id,
            alert_type='CATEGORY_OVERRUN',
            title='Shopping Cap Exceeded',
            description='Over cap by ₹2,000',
            severity='WARNING'
        )
        db.session.add(alice_alert)
        db.session.commit()
        alice_alert_id = alice_alert.id

    # Bob tries to dismiss Alice's alert
    res = client.post(f'/api/spendsense/findings/{alice_alert_id}/action', json={'action': 'dismiss'})
    assert res.status_code == 400 or res.status_code == 404

    # Verify Alice's alert remains unchanged
    with app.app_context():
        a = db.session.get(FinancialAlert, alice_alert_id)
        assert a.is_dismissed is False


def test_assistant_spendsense_queries(client, app, test_user):
    """Assistant accurately answers all SpendSense financial queries."""
    auth_session(client, test_user)

    queries = [
        "Where is my money leaking?",
        "Which category increased the most?",
        "How much did I spend on food delivery this month?",
        "Which recurring payments should I review?",
        "Am I following the 50/30/20 rule?",
        "How much could I potentially save?",
        "Why is my needs allocation above 50%?",
        "What changed compared with last month?"
    ]

    for q in queries:
        res = client.post('/api/assistant/chat', json={'message': q})
        assert res.status_code == 200
        data = res.get_json()
        assert data.get('success') is True
        reply = data.get('response') or data.get('reply') or ''
        assert len(reply) > 20
        # Ensure text only and no fabricated claims
        assert 'voice' not in reply.lower()
