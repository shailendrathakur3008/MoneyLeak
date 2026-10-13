from datetime import date
from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction
from app.services.budget_engine import calculate_budget_summary


def test_standard_50_30_20_targets(app, test_user):
    # test_user has 40,000 income (4,000,000 minor units) and default 50/30/20
    summary = calculate_budget_summary(test_user.id)

    assert summary['income']['minor'] == 4000000
    assert summary['needs']['target_minor'] == 2000000   # ₹20,000
    assert summary['wants']['target_minor'] == 1200000   # ₹12,000
    assert summary['savings']['target_minor'] == 800000  # ₹8,000


def test_budget_actuals_and_refunds(app, test_user):
    today = date.today()
    cats = {c.name: c for c in Category.query.filter_by(user_id=test_user.id).all()}

    # Add Needs expense: ₹15,000
    t1 = Transaction(
        user_id=test_user.id,
        category_id=cats['Housing & Rent'].id,
        amount_minor_units=1500000,
        transaction_type='EXPENSE',
        transaction_date=today,
        description='Rent'
    )
    # Add Wants expense: ₹5,000
    t2 = Transaction(
        user_id=test_user.id,
        category_id=cats['Dining Out & Cafes'].id,
        amount_minor_units=500000,
        transaction_type='EXPENSE',
        transaction_date=today,
        description='Dinner'
    )
    # Add Wants refund: ₹1,000
    t3 = Transaction(
        user_id=test_user.id,
        category_id=cats['Dining Out & Cafes'].id,
        amount_minor_units=100000,
        transaction_type='REFUND',
        transaction_date=today,
        description='Refund for cancelled item'
    )
    # Add Savings contribution: ₹8,000
    t4 = Transaction(
        user_id=test_user.id,
        category_id=cats['Mutual Funds & Stocks'].id,
        amount_minor_units=800000,
        transaction_type='SAVINGS_CONTRIBUTION',
        transaction_date=today,
        description='SIP'
    )
    db.session.add_all([t1, t2, t3, t4])
    db.session.commit()

    summary = calculate_budget_summary(test_user.id)

    # Needs: 15,000
    assert summary['needs']['actual_minor'] == 1500000
    assert summary['needs']['remaining_minor'] == 500000

    # Wants: 5,000 - 1,000 refund = 4,000
    assert summary['wants']['actual_minor'] == 400000
    assert summary['wants']['remaining_minor'] == 800000

    # Savings: 8,000
    assert summary['savings']['actual_minor'] == 800000
    assert summary['savings']['gap_minor'] == 0
    assert summary['savings']['is_met'] is True

    # Consumption Expenses: 15,000 + 4,000 = 19,000
    assert summary['expenses']['minor'] == 1900000

    # Total Outflow: Consumption (19,000) + Savings (8,000) = 27,000
    assert summary['total_outflow']['minor'] == 2700000

    # Surplus: 40,000 - 27,000 = 13,000
    assert summary['surplus']['minor'] == 1300000
    assert summary['savings_rate'] == 20.0


def test_zero_income_safe_handling(app, test_user):
    test_user.monthly_income_minor_units = 0
    db.session.commit()

    summary = calculate_budget_summary(test_user.id)
    assert summary['income']['minor'] == 0
    assert summary['savings_rate'] == 0.0
    assert summary['needs']['target_minor'] == 0
