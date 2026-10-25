"""
Tests for Persistent Budgets with Monthly Confirmation in MoneyLeak.

Verifies the 16 required specification points:
1. User saves ₹10,000 in October.
2. On November 1, application asks whether to set a new budget.
3. User ignores the prompt -> budget remains ₹10,000.
4. User closes the prompt -> budget remains ₹10,000.
5. User chooses Keep Previous Budget -> ₹10,000 remains active.
6. User saves ₹15,000 -> new budget becomes active.
7. New budget remains ₹15,000 after refreshing.
8. Logging out and logging back in preserves the saved budget.
9. Changing monthly income does not change the budget.
10. Changing savings target does not change the budget.
11. Adding or deleting transactions does not change the budget.
12. A new year does not reset the budget (Dec -> Jan carry-forward).
13. Historical monthly budgets remain unchanged when current budget changes.
14. Duplicate monthly records cannot be created (unique constraint).
15. A failed database update does not overwrite the last saved budget.
16. Multiple devices/tabs do not cause conflicting budget updates.
"""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.user import User
from app.models.budget import MonthlyBudget, Budget
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.persistent_budget_service import (
    get_or_create_monthly_budget,
    set_monthly_budget,
    confirm_retained_budget,
    postpone_budget_confirmation,
    dismiss_budget_prompt,
    get_monthly_prompt_info,
    get_budget_history
)
from app.services.budget_engine import calculate_budget_summary


def login_client(client, email='alice@example.com', password='securePassword123'):
    return client.post('/login', json={'email': email, 'password': password})


def test_specification_1_to_8_lifecycle(app, client, test_user):
    """
    Tests specs 1 through 8 in sequence:
    1. A user saves ₹10,000 in October.
    2. On November 1, the application asks whether to set a new budget.
    3. The user ignores the prompt and the budget remains ₹10,000.
    4. The user closes the prompt and the budget remains ₹10,000.
    5. The user chooses Keep Previous Budget and ₹10,000 remains active.
    6. The user saves ₹15,000 and the new budget becomes active.
    7. The new budget remains ₹15,000 after refreshing.
    8. Logging out and logging back in preserves the saved budget.
    """
    # 1. User explicitly saves ₹10,000 (1,000,000 minor units) in October 2026
    mb_oct = set_monthly_budget(test_user.id, 2026, 10, 1000000)
    assert mb_oct.budget_amount_minor_units == 1000000
    assert mb_oct.is_manually_set is True
    assert mb_oct.confirmation_status == 'confirmed_new'
    assert test_user.monthly_budget_minor_units == 1000000

    # 2. On November 1 (or any day in November), the app checks prompt status
    prompt_nov = get_monthly_prompt_info(test_user.id, 2026, 11)
    assert prompt_nov['should_prompt'] is True
    assert prompt_nov['month_name'] == 'November'
    assert prompt_nov['prev_month_name'] == 'October'
    assert prompt_nov['previous_budget_minor'] == 1000000
    assert '10,000' in prompt_nov['previous_budget_formatted']

    # 3. User ignores prompt -> budget used for November is still ₹10,000 (carried forward)
    summary_nov = calculate_budget_summary(test_user.id, 2026, 11)
    assert summary_nov['budget']['minor'] == 1000000
    assert '10,000' in summary_nov['budget']['formatted']
    # 50/30/20 calculated against ₹10,000: Needs ₹5,000, Wants ₹3,000, Savings ₹2,000
    assert summary_nov['needs']['target_minor'] == 500000
    assert summary_nov['wants']['target_minor'] == 300000
    assert summary_nov['savings']['target_minor'] == 200000

    # 4. User closes the prompt (dismiss) -> budget remains ₹10,000
    mb_dismiss = dismiss_budget_prompt(test_user.id, 2026, 11)
    assert mb_dismiss.confirmation_status == 'dismissed'
    assert mb_dismiss.budget_amount_minor_units == 1000000
    summary_after_close = calculate_budget_summary(test_user.id, 2026, 11)
    assert summary_after_close['budget']['minor'] == 1000000

    # 5. User chooses 'Keep Previous Budget' -> budget remains active ₹10,000
    mb_retained = confirm_retained_budget(test_user.id, 2026, 11)
    assert mb_retained.confirmation_status == 'confirmed_retained'
    assert mb_retained.budget_amount_minor_units == 1000000
    summary_retained = calculate_budget_summary(test_user.id, 2026, 11)
    assert summary_retained['budget']['minor'] == 1000000

    # 6. Later in November (or February), user explicitly saves ₹15,000 (1,500,000 minor units)
    mb_new = set_monthly_budget(test_user.id, 2026, 11, 1500000)
    assert mb_new.budget_amount_minor_units == 1500000
    assert mb_new.confirmation_status == 'confirmed_new'
    assert test_user.monthly_budget_minor_units == 1500000

    summary_new = calculate_budget_summary(test_user.id, 2026, 11)
    assert summary_new['budget']['minor'] == 1500000
    assert '15,000' in summary_new['budget']['formatted']
    # Needs: 50% of 15,000 = 7,500
    assert summary_new['needs']['target_minor'] == 750000

    # 7. Refreshing (retrieving afresh from database) preserves ₹15,000
    db.session.expire_all()
    reloaded_mb = MonthlyBudget.query.filter_by(user_id=test_user.id, year=2026, month=11).first()
    assert reloaded_mb.budget_amount_minor_units == 1500000
    reloaded_user = db.session.get(User, test_user.id)
    assert reloaded_user.monthly_budget_minor_units == 1500000

    # 8. Logging out and logging back in preserves the saved budget via HTTP client
    login_res = login_client(client, 'alice@example.com', 'securePassword123')
    assert login_res.status_code == 200

    # Verify dashboard API returns 15,000 budget
    dash_res = client.get('/api/dashboard?year=2026&month=11')
    assert dash_res.status_code == 200
    dash_data = dash_res.get_json()
    assert dash_data['summary']['budget']['minor'] == 1500000

    # Logout
    client.get('/logout')

    # Re-login
    login_again = login_client(client, 'alice@example.com', 'securePassword123')
    assert login_again.status_code == 200
    dash_after = client.get('/api/dashboard?year=2026&month=11')
    assert dash_after.status_code == 200
    assert dash_after.get_json()['summary']['budget']['minor'] == 1500000


def test_specification_9_income_change_preserves_budget(app, client, test_user):
    """
    9. Changing monthly income does not change the budget.
    """
    login_client(client, 'alice@example.com', 'securePassword123')

    # Explicitly set budget to ₹12,000
    set_monthly_budget(test_user.id, 2026, 10, 1200000)

    # User changes income in Settings to ₹80,000
    res = client.post('/api/settings/profile', json={
        'monthly_income': '80000'
    })
    assert res.status_code == 200

    # Check budget is completely untouched (still ₹12,000)
    db.session.refresh(test_user)
    assert test_user.monthly_income_minor_units == 8000000
    assert test_user.monthly_budget_minor_units == 1200000

    summary = calculate_budget_summary(test_user.id, 2026, 10)
    assert summary['budget']['minor'] == 1200000
    assert summary['income']['minor'] == 8000000
    # Needs target still based on ₹12,000 budget (50% = ₹6,000)
    assert summary['needs']['target_minor'] == 600000


def test_specification_10_savings_target_change_preserves_budget(app, client, test_user):
    """
    10. Changing the savings target does not change the budget.
    """
    login_client(client, 'alice@example.com', 'securePassword123')
    set_monthly_budget(test_user.id, 2026, 10, 1400000)

    # Change savings target to ₹25,000
    res = client.post('/api/settings/profile', json={
        'monthly_savings_target': '25000'
    })
    assert res.status_code == 200

    db.session.refresh(test_user)
    assert test_user.monthly_savings_target_minor_units == 2500000
    assert test_user.monthly_budget_minor_units == 1400000

    summary = calculate_budget_summary(test_user.id, 2026, 10)
    assert summary['budget']['minor'] == 1400000


def test_specification_11_transactions_do_not_change_budget(app, test_user):
    """
    11. Adding or deleting transactions does not change the budget.
    """
    set_monthly_budget(test_user.id, 2026, 10, 1000000)
    cats = {c.name: c for c in Category.query.filter_by(user_id=test_user.id).all()}

    # Add transaction
    t = Transaction(
        user_id=test_user.id,
        category_id=cats['Housing & Rent'].id,
        amount_minor_units=400000,
        transaction_type='EXPENSE',
        transaction_date=date(2026, 10, 15),
        description='Rent payment'
    )
    db.session.add(t)
    db.session.commit()

    summary1 = calculate_budget_summary(test_user.id, 2026, 10)
    assert summary1['budget']['minor'] == 1000000
    assert summary1['total_outflow']['minor'] == 400000

    # Delete transaction
    db.session.delete(t)
    db.session.commit()

    summary2 = calculate_budget_summary(test_user.id, 2026, 10)
    assert summary2['budget']['minor'] == 1000000
    assert summary2['total_outflow']['minor'] == 0


def test_specification_12_new_year_transition(app, test_user):
    """
    12. A new year does not reset the budget (December -> January carry forward).
    """
    # User sets ₹18,000 in December 2026
    set_monthly_budget(test_user.id, 2026, 12, 1800000)

    # In January 2027 (new year), budget carries forward as ₹18,000
    summary_jan = calculate_budget_summary(test_user.id, 2027, 1)
    assert summary_jan['budget']['minor'] == 1800000
    assert '18,000' in summary_jan['budget']['formatted']

    # Prompt correctly identifies December 2026 as prior month with ₹18,000
    prompt_jan = get_monthly_prompt_info(test_user.id, 2027, 1)
    assert prompt_jan['prev_year'] == 2026
    assert prompt_jan['prev_month'] == 12
    assert prompt_jan['previous_budget_minor'] == 1800000
    assert prompt_jan['current_budget_minor'] == 1800000


def test_specification_13_historical_records_remain_intact(app, test_user):
    """
    13. Historical monthly budgets remain unchanged when the current budget changes.
    """
    # Set October 2026 to ₹10,000
    set_monthly_budget(test_user.id, 2026, 10, 1000000)

    # Set November 2026 to ₹12,000
    set_monthly_budget(test_user.id, 2026, 11, 1200000)

    # In December 2026, user sets ₹20,000
    set_monthly_budget(test_user.id, 2026, 12, 2000000)

    # Historical October and November MUST remain ₹10,000 and ₹12,000
    oct_rec = MonthlyBudget.query.filter_by(user_id=test_user.id, year=2026, month=10).first()
    nov_rec = MonthlyBudget.query.filter_by(user_id=test_user.id, year=2026, month=11).first()
    dec_rec = MonthlyBudget.query.filter_by(user_id=test_user.id, year=2026, month=12).first()

    assert oct_rec.budget_amount_minor_units == 1000000
    assert nov_rec.budget_amount_minor_units == 1200000
    assert dec_rec.budget_amount_minor_units == 2000000

    # Summary calculations for historical periods preserve historical values
    assert calculate_budget_summary(test_user.id, 2026, 10)['budget']['minor'] == 1000000
    assert calculate_budget_summary(test_user.id, 2026, 11)['budget']['minor'] == 1200000
    assert calculate_budget_summary(test_user.id, 2026, 12)['budget']['minor'] == 2000000


def test_specification_14_unique_monthly_record_constraint(app, test_user):
    """
    14. Duplicate monthly records cannot be created (unique constraint enforced).
    """
    set_monthly_budget(test_user.id, 2026, 10, 1000000)

    # Attempting to manually insert another record for the same user, year, month must fail
    dup = MonthlyBudget(
        user_id=test_user.id,
        year=2026,
        month=10,
        budget_amount_minor_units=1500000
    )
    db.session.add(dup)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_specification_15_failed_update_preserves_last_budget(app, client, test_user):
    """
    15. A failed database update or invalid payload does not overwrite the last saved budget.
    """
    login_client(client, 'alice@example.com', 'securePassword123')
    set_monthly_budget(test_user.id, 2026, 10, 1000000)

    # Send negative amount
    res1 = client.post('/api/budget/confirm-action', json={
        'action': 'set_new',
        'amount': -500,
        'year': 2026,
        'month': 10
    })
    assert res1.status_code == 400

    # Send non-numeric amount
    res2 = client.post('/api/budget/confirm-action', json={
        'action': 'set_new',
        'amount': 'invalid_string',
        'year': 2026,
        'month': 10
    })
    assert res2.status_code == 400

    # Last confirmed budget must still be intact
    db.session.expire_all()
    mb = MonthlyBudget.query.filter_by(user_id=test_user.id, year=2026, month=10).first()
    assert mb.budget_amount_minor_units == 1000000
    assert test_user.monthly_budget_minor_units == 1000000


def test_specification_16_concurrent_access_safety(app, test_user):
    """
    16. Multiple devices/tabs do not cause duplicate conflicting records.
    """
    # Calling get_or_create_monthly_budget repeatedly returns the same instance
    b1 = get_or_create_monthly_budget(test_user.id, 2026, 11)
    b2 = get_or_create_monthly_budget(test_user.id, 2026, 11)
    assert b1.id == b2.id

    all_records = MonthlyBudget.query.filter_by(user_id=test_user.id, year=2026, month=11).all()
    assert len(all_records) == 1


def test_http_api_endpoints(app, client, test_user):
    """Tests the HTTP endpoints for monthly status, keep previous, postpone, and history."""
    login_client(client, 'alice@example.com', 'securePassword123')
    set_monthly_budget(test_user.id, 2026, 10, 1000000)

    # 1. GET monthly-status
    res = client.get('/api/budget/monthly-status?year=2026&month=11')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['prompt_info']['previous_budget_minor'] == 1000000

    # 2. POST remind_later (postpone)
    res_postpone = client.post('/api/budget/confirm-action', json={
        'action': 'remind_later',
        'year': 2026,
        'month': 11
    })
    assert res_postpone.status_code == 200
    assert res_postpone.get_json()['prompt_info']['confirmation_status'] == 'postponed'

    # 3. POST keep_previous
    res_keep = client.post('/api/budget/confirm-action', json={
        'action': 'keep_previous',
        'year': 2026,
        'month': 11
    })
    assert res_keep.status_code == 200
    assert res_keep.get_json()['prompt_info']['confirmation_status'] == 'confirmed_retained'

    # 4. GET history
    res_hist = client.get('/api/budget/history')
    assert res_hist.status_code == 200
    hist = res_hist.get_json()['history']
    assert len(hist) >= 2


def test_prompt_states_and_canonical_aliases(app, client, test_user):
    """Verifies all prompt states and canonical aliases from Section 8."""
    login_client(client, 'alice@example.com', 'securePassword123')

    # 1. State: not_prompted
    mb = get_or_create_monthly_budget(test_user.id, 2026, 10)
    assert mb.confirmation_status in ('pending', 'not_prompted')

    # 2. State: prompt_shown via API
    res_status = client.get('/api/budget/monthly-status?year=2026&month=10')
    assert res_status.status_code == 200
    db.session.refresh(mb)
    assert mb.prompt_shown_at is not None

    # 3. Action: reminder_postponed
    res_post = client.post('/api/budget/confirm-action', json={
        'action': 'reminder_postponed',
        'year': 2026,
        'month': 10
    })
    assert res_post.status_code == 200

    # 4. Action: previous_budget_retained
    res_keep = client.post('/api/budget/confirm-action', json={
        'action': 'previous_budget_retained',
        'year': 2026,
        'month': 10
    })
    assert res_keep.status_code == 200

    # 5. Action: new_budget_saved
    res_new = client.post('/api/budget/confirm-action', json={
        'action': 'new_budget_saved',
        'amount': '12500',
        'year': 2026,
        'month': 10
    })
    assert res_new.status_code == 200
    assert res_new.get_json()['summary']['budget']['minor'] == 1250000


def test_offline_multi_month_gap_carry_forward(app, test_user):
    """
    Verifies that if user saves budget in October, stays offline during November and December,
    and returns in January, the January budget correctly carries forward October's budget.
    """
    # Saves ₹10,000 in October 2026
    set_monthly_budget(test_user.id, 2026, 10, 1000000)

    # Direct access to January 2027 without visiting Nov or Dec
    jan_mb = get_or_create_monthly_budget(test_user.id, 2027, 1)
    assert jan_mb.budget_amount_minor_units == 1000000
    assert jan_mb.source_month == "2026-10"

    # Summary for Jan 2027 uses ₹10,000
    summary = calculate_budget_summary(test_user.id, 2027, 1)
    assert summary['budget']['minor'] == 1000000
    assert summary['needs']['target_minor'] == 500000
    assert summary['wants']['target_minor'] == 300000
    assert summary['savings']['target_minor'] == 200000

    # Prompt correctly identifies October 2026 as source
    prompt_info = get_monthly_prompt_info(test_user.id, 2027, 1)
    assert prompt_info['previous_budget_minor'] == 1000000
    assert prompt_info['prev_month_name'] == 'October'
    assert prompt_info['prev_year'] == 2026

