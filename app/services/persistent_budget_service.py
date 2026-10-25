"""
Persistent Budget Service for MoneyLeak.

Core Rule: Never automatically change a user's saved budget.
Only update it when the user explicitly enters a new budget and confirms it.
Carries forward previous month's budget across months and years with monthly confirmation.
"""
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from calendar import month_name

from app.extensions import db
from app.models.user import User
from app.models.budget import Budget, MonthlyBudget
from app.services.money import format_money, from_minor_units, get_currency_symbol, to_minor_units


def get_previous_month(year: int, month: int):
    """Calculates previous (year, month)."""
    if month == 1:
        return year - 1, 12
    return year, month - 1


def get_next_month(year: int, month: int):
    """Calculates next (year, month)."""
    if month == 12:
        return year + 1, 1
    return year, month + 1


def get_or_create_monthly_budget(user_id: int, year: int, month: int) -> MonthlyBudget:
    """
    Retrieves or initializes the MonthlyBudget for the requested period.
    Carries forward the latest saved budget without altering historical records.
    Ensures exactly one active budget record per user per month.
    """
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f"User ID {user_id} not found.")

    mb = MonthlyBudget.query.filter_by(user_id=user_id, year=year, month=month).first()
    if mb:
        return mb

    # Carry forward logic: Find the most recent prior monthly budget
    prior = MonthlyBudget.query.filter(
        MonthlyBudget.user_id == user_id,
        (MonthlyBudget.year < year) | ((MonthlyBudget.year == year) & (MonthlyBudget.month < month))
    ).order_by(MonthlyBudget.year.desc(), MonthlyBudget.month.desc()).first()

    carried_amount = 0
    source_month = None

    if prior and prior.budget_amount_minor_units > 0:
        carried_amount = prior.budget_amount_minor_units
        source_month = f"{prior.year}-{prior.month:02d}"
    elif user.monthly_budget_minor_units and user.monthly_budget_minor_units > 0:
        # Fallback to user's saved master persistent budget
        carried_amount = user.monthly_budget_minor_units
    elif user.monthly_income_minor_units and user.monthly_income_minor_units > 0:
        # Initial default seed when user enters monthly income/allowance on profile setup
        carried_amount = user.monthly_income_minor_units

    mb = MonthlyBudget(
        user_id=user_id,
        year=year,
        month=month,
        budget_amount_minor_units=carried_amount,
        source_month=source_month,
        is_manually_set=False,
        confirmation_status='pending',
        prompt_shown_at=None
    )
    db.session.add(mb)

    # Also ensure user master persistent budget is populated if it was 0
    if (not user.monthly_budget_minor_units or user.monthly_budget_minor_units == 0) and carried_amount > 0:
        user.monthly_budget_minor_units = carried_amount

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # If created concurrently by another request, fetch existing
        mb = MonthlyBudget.query.filter_by(user_id=user_id, year=year, month=month).first()
        if not mb:
            raise

    return mb


def set_monthly_budget(
    user_id: int,
    year: int,
    month: int,
    amount_minor_units: int,
    update_future: bool = True
) -> MonthlyBudget:
    """
    Explicitly updates and confirms a new monthly budget.
    Only called when the user explicitly confirms a new amount.
    Updates future unconfirmed carried-forward months so the new budget persists across the year.
    Never alters past historical months.
    """
    if amount_minor_units < 0:
        raise ValueError("Budget amount cannot be negative.")

    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f"User ID {user_id} not found.")

    mb = MonthlyBudget.query.filter_by(user_id=user_id, year=year, month=month).first()
    if not mb:
        mb = MonthlyBudget(
            user_id=user_id,
            year=year,
            month=month,
            budget_amount_minor_units=amount_minor_units,
            is_manually_set=True,
            confirmation_status='confirmed_new',
            confirmed_at=datetime.utcnow()
        )
        db.session.add(mb)
    else:
        mb.budget_amount_minor_units = amount_minor_units
        mb.is_manually_set = True
        mb.confirmation_status = 'confirmed_new'
        mb.confirmed_at = datetime.utcnow()
        mb.source_month = None

    # Update user's persistent master default budget
    user.monthly_budget_minor_units = amount_minor_units

    # Cascade to future months that were not manually configured
    if update_future:
        future_records = MonthlyBudget.query.filter(
            MonthlyBudget.user_id == user_id,
            (MonthlyBudget.year > year) | ((MonthlyBudget.year == year) & (MonthlyBudget.month > month)),
            MonthlyBudget.is_manually_set.is_(False)
        ).all()
        for fut in future_records:
            fut.budget_amount_minor_units = amount_minor_units
            fut.source_month = f"{year}-{month:02d}"

    db.session.commit()
    return mb


def confirm_retained_budget(user_id: int, year: int, month: int) -> MonthlyBudget:
    """
    Confirms using the previous month's budget without modifying the saved amount.
    """
    mb = get_or_create_monthly_budget(user_id, year, month)
    mb.confirmation_status = 'confirmed_retained'
    mb.confirmed_at = datetime.utcnow()
    db.session.commit()
    return mb


def postpone_budget_confirmation(user_id: int, year: int, month: int) -> MonthlyBudget:
    """
    User chose 'Remind Me Later'. Postpones the prompt without changing the budget.
    """
    mb = get_or_create_monthly_budget(user_id, year, month)
    mb.confirmation_status = 'postponed'
    db.session.commit()
    return mb


def dismiss_budget_prompt(user_id: int, year: int, month: int) -> MonthlyBudget:
    """
    User closed or dismissed the prompt. Retains active budget.
    """
    mb = get_or_create_monthly_budget(user_id, year, month)
    mb.confirmation_status = 'dismissed'
    db.session.commit()
    return mb


def get_user_current_date(user: Optional[User] = None) -> date:
    """
    Returns the current date respecting the user's timezone.
    For users in India or by default, uses Asia/Kolkata (IST, UTC+5:30).
    """
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=5, minutes=30))
    if user and user.country and user.country != 'India':
        tz = timezone.utc
    return datetime.now(tz).date()


def mark_prompt_shown(user_id: int, year: int, month: int) -> None:
    """Records that the monthly confirmation prompt was presented to the user."""
    mb = get_or_create_monthly_budget(user_id, year, month)
    if not mb.prompt_shown_at:
        mb.prompt_shown_at = datetime.utcnow()
        if mb.confirmation_status in ('pending', 'not_prompted'):
            mb.confirmation_status = 'prompt_shown'
        db.session.commit()


def get_monthly_prompt_info(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
    """
    Compiles all contextual data for the monthly confirmation prompt:
    - Current month name & year (timezone-aware)
    - Previous month name & previous budget
    - Active carried forward budget amount
    - Whether prompt should be displayed
    """
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f"User ID {user_id} not found.")

    user_today = get_user_current_date(user)
    if year is None:
        year = user_today.year
    if month is None:
        month = user_today.month

    mb = get_or_create_monthly_budget(user_id, year, month)

    # Resolve prior month & prior budget
    prev_y, prev_m = get_previous_month(year, month)
    prior = MonthlyBudget.query.filter(
        MonthlyBudget.user_id == user_id,
        (MonthlyBudget.year < year) | ((MonthlyBudget.year == year) & (MonthlyBudget.month < month)),
        MonthlyBudget.budget_amount_minor_units > 0
    ).order_by(MonthlyBudget.year.desc(), MonthlyBudget.month.desc()).first()

    if prior:
        prev_amount_minor = prior.budget_amount_minor_units
        prev_y, prev_m = prior.year, prior.month
    elif user.monthly_budget_minor_units and user.monthly_budget_minor_units > 0:
        prev_amount_minor = user.monthly_budget_minor_units
    elif user.monthly_income_minor_units and user.monthly_income_minor_units > 0:
        prev_amount_minor = user.monthly_income_minor_units
    else:
        prev_amount_minor = mb.budget_amount_minor_units

    # Should prompt if not yet confirmed or dismissed
    is_confirmed = mb.confirmation_status in (
        'confirmed_new', 'new_budget_saved',
        'confirmed_retained', 'previous_budget_retained',
        'dismissed', 'prompt_dismissed'
    )
    should_prompt = not is_confirmed

    # Get budget distribution percentages
    budget = Budget.query.filter_by(user_id=user_id).order_by(Budget.created_at.desc()).first()
    needs_pct = float(budget.needs_percentage) if budget else 50.0
    wants_pct = float(budget.wants_percentage) if budget else 30.0
    savings_pct = float(budget.savings_percentage) if budget else 20.0

    curr = user.currency
    sym = get_currency_symbol(curr)

    # Human-readable status mapping
    status_display = {
        'not_prompted': 'Not Prompted',
        'pending': 'Pending',
        'prompt_shown': 'Prompt Shown',
        'confirmed_new': 'New Budget Saved',
        'new_budget_saved': 'New Budget Saved',
        'confirmed_retained': 'Previous Budget Retained',
        'previous_budget_retained': 'Previous Budget Retained',
        'postponed': 'Reminder Postponed',
        'reminder_postponed': 'Reminder Postponed',
        'dismissed': 'Prompt Dismissed',
        'prompt_dismissed': 'Prompt Dismissed'
    }.get(mb.confirmation_status, mb.confirmation_status)

    return {
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'prev_year': prev_y,
        'prev_month': prev_m,
        'prev_month_name': month_name[prev_m],
        'current_budget_minor': mb.budget_amount_minor_units,
        'current_budget_amount': mb.budget_amount_minor_units / 100.0,
        'current_budget_formatted': format_money(mb.budget_amount_minor_units, curr),
        'previous_budget_minor': prev_amount_minor,
        'previous_budget_amount': prev_amount_minor / 100.0,
        'previous_budget_formatted': format_money(prev_amount_minor, curr),
        'confirmation_status': mb.confirmation_status,
        'confirmation_status_display': status_display,
        'is_manually_set': mb.is_manually_set,
        'source_month': mb.source_month,
        'should_prompt': should_prompt,
        'needs_pct': needs_pct,
        'wants_pct': wants_pct,
        'savings_pct': savings_pct,
        'currency': curr,
        'currency_symbol': sym
    }


def get_budget_history(user_id: int, limit: int = 12) -> List[Dict[str, Any]]:
    """Retrieves chronological monthly budget history for reports and charts."""
    user = db.session.get(User, user_id)
    if not user:
        return []

    records = MonthlyBudget.query.filter_by(user_id=user_id)\
        .order_by(MonthlyBudget.year.desc(), MonthlyBudget.month.desc())\
        .limit(limit).all()

    return [
        {
            'id': r.id,
            'year': r.year,
            'month': r.month,
            'month_name': month_name[r.month],
            'label': f"{month_name[r.month][:3]} {r.year}",
            'amount_minor': r.budget_amount_minor_units,
            'amount_formatted': format_money(r.budget_amount_minor_units, user.currency),
            'is_manually_set': r.is_manually_set,
            'confirmation_status': r.confirmation_status,
            'source_month': r.source_month,
            'created_at': r.created_at.isoformat() if r.created_at else None
        }
        for r in reversed(records)
    ]
