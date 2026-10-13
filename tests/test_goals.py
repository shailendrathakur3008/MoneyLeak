from datetime import date, timedelta
from app.extensions import db
from app.models.goal import SavingsGoal, GoalContribution
from app.services.goal_engine import calculate_goal_metrics


def test_goal_metrics_and_monthly_required(app, test_user):
    today = date.today()
    target_dt = today + timedelta(days=180)  # ~6 months

    goal = SavingsGoal(
        user_id=test_user.id,
        name='Emergency Fund Target',
        target_amount_minor_units=6000000,  # ₹60,000
        target_date=target_dt,
        category_type='EMERGENCY_FUND',
        status='ACTIVE'
    )
    db.session.add(goal)
    db.session.flush()

    # Log initial contribution of ₹20,000 (2,000,000 minor)
    contrib = GoalContribution(
        user_id=test_user.id,
        goal_id=goal.id,
        amount_minor_units=2000000,
        contribution_date=today,
        notes='Initial deposit'
    )
    db.session.add(contrib)
    db.session.commit()

    metrics = calculate_goal_metrics(goal, test_user.currency)

    assert metrics['target_minor'] == 6000000
    assert metrics['contributed_minor'] == 2000000
    assert metrics['remaining_minor'] == 4000000
    assert metrics['progress_pct'] == 33.3
    assert metrics['months_remaining'] == 6
    assert metrics['required_monthly_minor'] == 666666  # ~₹6,666/mo
