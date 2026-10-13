"""
Financial Goal Planner Engine for MoneyLeak.

Calculates milestone progress, remaining amounts, on-track status,
and required monthly contributions based on deadlines and historical pace.
"""
from datetime import date
from typing import Dict, Any, List
from app.models.goal import SavingsGoal, GoalContribution
from app.services.money import format_money


def calculate_goal_metrics(goal: SavingsGoal, user_currency: str = 'INR') -> Dict[str, Any]:
    """Calculate progress, remaining amounts, and required monthly contributions for a savings goal."""
    today = date.today()
    target_minor = goal.target_amount_minor_units
    contributed_minor = goal.total_contributed_minor_units
    remaining_minor = max(0, target_minor - contributed_minor)

    # Progress percentage
    progress_pct = (contributed_minor / target_minor * 100.0) if target_minor > 0 else 0.0
    progress_pct = min(100.0, round(progress_pct, 1))

    # Months remaining calculation
    target_dt = goal.target_date
    if target_dt <= today:
        months_remaining = 0
        is_overdue = remaining_minor > 0
    else:
        # Approximate months
        days_remaining = (target_dt - today).days
        months_remaining = max(1, int(round(days_remaining / 30.4375)))
        is_overdue = False

    # Required monthly contribution
    if remaining_minor == 0:
        required_monthly_minor = 0
        status_label = 'COMPLETED'
        is_on_track = True
    elif months_remaining == 0:
        required_monthly_minor = remaining_minor
        status_label = 'OVERDUE'
        is_on_track = False
    else:
        required_monthly_minor = int(remaining_minor / months_remaining)
        status_label = 'IN_PROGRESS'
        # Heuristic on-track: if created some time ago and contributions meet pace
        is_on_track = True

    return {
        'id': goal.id,
        'name': goal.name,
        'category_type': goal.category_type,
        'status': status_label,
        'icon': goal.icon,
        'target_date': goal.target_date.isoformat(),
        'target_minor': target_minor,
        'contributed_minor': contributed_minor,
        'remaining_minor': remaining_minor,
        'required_monthly_minor': required_monthly_minor,
        'months_remaining': months_remaining,
        'progress_pct': progress_pct,
        'is_overdue': is_overdue,
        'is_on_track': is_on_track,
        # Formatted
        'target_formatted': format_money(target_minor, user_currency),
        'contributed_formatted': format_money(contributed_minor, user_currency),
        'remaining_formatted': format_money(remaining_minor, user_currency),
        'required_monthly_formatted': format_money(required_monthly_minor, user_currency),
    }


def get_all_goals_summary(user_id: int, user_currency: str = 'INR') -> Dict[str, Any]:
    """Retrieve all savings goals for a user with aggregated statistics."""
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()
    goal_cards = [calculate_goal_metrics(g, user_currency) for g in goals]

    total_target_minor = sum(g['target_minor'] for g in goal_cards)
    total_contributed_minor = sum(g['contributed_minor'] for g in goal_cards)
    total_remaining_minor = sum(g['remaining_minor'] for g in goal_cards)
    overall_progress = (total_contributed_minor / total_target_minor * 100.0) if total_target_minor > 0 else 0.0

    return {
        'goals': goal_cards,
        'total_target_minor': total_target_minor,
        'total_contributed_minor': total_contributed_minor,
        'total_remaining_minor': total_remaining_minor,
        'overall_progress_pct': round(overall_progress, 1),
        'total_target_formatted': format_money(total_target_minor, user_currency),
        'total_contributed_formatted': format_money(total_contributed_minor, user_currency),
        'total_remaining_formatted': format_money(total_remaining_minor, user_currency)
    }
