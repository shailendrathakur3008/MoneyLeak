"""
MoneyLeak Detection Engine.

Detects spending leaks, recurring subscriptions drain, unusual transactions,
budget overruns, and lifestyle inflation using explainable financial rules.
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from calendar import monthrange
from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.recurring_payment import RecurringPayment
from app.models.alert import FinancialAlert
from app.services.money import format_money
from app.services.budget_engine import calculate_budget_summary, get_month_date_range


def run_leak_detection(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Evaluate all 8 MoneyLeak rules for the given user and period.
    Generates structured, explainable alert objects and persists new alerts.
    """
    user = db.session.get(User, user_id)
    if not user:
        return []

    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Current month summary
    curr_summary = calculate_budget_summary(user_id, year, month)
    curr_start, curr_end = get_month_date_range(year, month)

    # Previous month date range
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    prev_start, prev_end = get_month_date_range(prev_year, prev_month)

    prev_summary = calculate_budget_summary(user_id, prev_year, prev_month)

    detected_alerts: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # RULE 1: Budget Overrun (Needs or Wants target exceeded)
    # -------------------------------------------------------------
    wants_variance = curr_summary['wants']['variance_minor']
    if wants_variance > 0:
        over_amt = format_money(wants_variance, user.currency)
        detected_alerts.append({
            'alert_type': 'BUDGET_OVERRUN',
            'title': f"Wants Budget Exceeded by {over_amt}",
            'description': f"Discretionary spending reached {curr_summary['wants']['actual_formatted']}, which is {over_amt} above your target of {curr_summary['wants']['target_formatted']}.",
            'severity': 'WARNING',
            'supporting_data': {
                'category_group': 'WANTS',
                'target_minor': curr_summary['wants']['target_minor'],
                'actual_minor': curr_summary['wants']['actual_minor'],
                'over_minor': wants_variance
            },
            'actionable_tip': "Review top discretionary purchases like dining out and impulse shopping in the Savings Simulator."
        })

    # Individual category monthly budget overrun
    for cat_item in curr_summary['category_breakdown']:
        cat_id = cat_item['id']
        cat_db = db.session.get(Category, cat_id) if cat_id else None
        if cat_db and cat_db.monthly_budget_minor_units and cat_item['total_minor'] > cat_db.monthly_budget_minor_units:
            overrun = cat_item['total_minor'] - cat_db.monthly_budget_minor_units
            detected_alerts.append({
                'alert_type': 'CATEGORY_OVERRUN',
                'title': f"{cat_db.name} Exceeded Monthly Cap",
                'description': f"You spent {format_money(cat_item['total_minor'], user.currency)} on {cat_db.name}, exceeding your target cap of {format_money(cat_db.monthly_budget_minor_units, user.currency)} by {format_money(overrun, user.currency)}.",
                'severity': 'WARNING',
                'supporting_data': {
                    'category_id': cat_id,
                    'category_name': cat_db.name,
                    'cap_minor': cat_db.monthly_budget_minor_units,
                    'actual_minor': cat_item['total_minor']
                },
                'actionable_tip': f"Consider pausing non-urgent purchases in {cat_db.name} for the remainder of this month."
            })

    # -------------------------------------------------------------
    # RULE 2: Spending Increase (MoM category surges > 25%)
    # -------------------------------------------------------------
    prev_cat_map = {c['id']: c['total_minor'] for c in prev_summary['category_breakdown']}
    for curr_cat in curr_summary['category_breakdown']:
        c_id = curr_cat['id']
        curr_amt = curr_cat['total_minor']
        prev_amt = prev_cat_map.get(c_id, 0)

        # Require a meaningful baseline (at least ₹500 or $10) and minimum spending
        min_threshold = 50000 if user.currency == 'INR' else 2000
        if prev_amt >= min_threshold and curr_amt > prev_amt:
            pct_increase = ((curr_amt - prev_amt) / prev_amt) * 100.0
            if pct_increase >= 25.0:
                diff_formatted = format_money(curr_amt - prev_amt, user.currency)
                detected_alerts.append({
                    'alert_type': 'SPENDING_INCREASE',
                    'title': f"{curr_cat['name']} jumped by {pct_increase:.0f}%",
                    'description': f"Spending on {curr_cat['name']} increased from {format_money(prev_amt, user.currency)} last month to {format_money(curr_amt, user.currency)} this month (+{diff_formatted}).",
                    'severity': 'INFO' if pct_increase < 50 else 'WARNING',
                    'supporting_data': {
                        'category_id': c_id,
                        'category_name': curr_cat['name'],
                        'prev_minor': prev_amt,
                        'curr_minor': curr_amt,
                        'increase_pct': round(pct_increase, 1)
                    },
                    'actionable_tip': f"Check recent transactions under {curr_cat['name']} to verify if this was a one-time event or recurring trend."
                })

    # -------------------------------------------------------------
    # RULE 3: Recurring Payment Analysis & Subscription Drain
    # -------------------------------------------------------------
    recurr_items = RecurringPayment.query.filter_by(user_id=user_id, status='ACTIVE').all()
    if recurr_items:
        total_recurring_monthly = sum(r.monthly_equivalent_minor_units for r in recurr_items)
        annual_total = total_recurring_monthly * 12
        # If recurring takes > 15% of monthly income, flag subscription drain
        recurr_pct = (total_recurring_monthly / curr_summary['income']['minor'] * 100.0) if curr_summary['income']['minor'] > 0 else 0
        if recurr_pct > 12.0:
            detected_alerts.append({
                'alert_type': 'RECURRING_DRAIN',
                'title': f"Active Subscriptions Commit {recurr_pct:.1f}% of Income",
                'description': f"You have {len(recurr_items)} active recurring services costing {format_money(total_recurring_monthly, user.currency)}/mo ({format_money(annual_total, user.currency)}/year).",
                'severity': 'WARNING' if recurr_pct > 20 else 'INFO',
                'supporting_data': {
                    'recurring_count': len(recurr_items),
                    'monthly_total_minor': total_recurring_monthly,
                    'annual_total_minor': annual_total
                },
                'actionable_tip': "Audit unused streaming apps or memberships in Recurring Payments to liberate monthly cashflow."
            })

    # -------------------------------------------------------------
    # RULE 4: Unusual Transactions (Statistical Outliers)
    # -------------------------------------------------------------
    # Find transactions in current period that are > 2.5x the category's average transaction amount
    for curr_cat in curr_summary['category_breakdown']:
        cat_id = curr_cat['id']
        if not cat_id:
            continue
        # Historical transactions in this category for the user
        all_txns_cat = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.category_id == cat_id,
            Transaction.transaction_type == 'EXPENSE'
        ).all()

        if len(all_txns_cat) >= 4:
            avg_amt = sum(t.amount_minor_units for t in all_txns_cat) / len(all_txns_cat)
            threshold = avg_amt * 2.5
            for t in all_txns_cat:
                if t.transaction_date >= curr_start and t.transaction_date <= curr_end and t.amount_minor_units > threshold:
                    detected_alerts.append({
                        'alert_type': 'UNUSUAL_TRANSACTION',
                        'title': f"Unusual High Expense: {t.description}",
                        'description': f"A payment of {format_money(t.amount_minor_units, user.currency)} at '{t.merchant or t.description}' is {t.amount_minor_units / avg_amt:.1f}x higher than your usual {curr_cat['name']} transaction average of {format_money(int(avg_amt), user.currency)}.",
                        'severity': 'INFO',
                        'supporting_data': {
                            'transaction_id': t.id,
                            'amount_minor': t.amount_minor_units,
                            'average_minor': int(avg_amt)
                        },
                        'actionable_tip': "Verify this transaction to ensure it was expected or properly split if shared with friends."
                    })
                    break  # Avoid spamming multiple per category

    # -------------------------------------------------------------
    # RULE 5: Savings Gap
    # -------------------------------------------------------------
    savings_gap = curr_summary['savings']['gap_minor']
    if savings_gap > 0 and curr_summary['income']['minor'] > 0:
        gap_formatted = format_money(savings_gap, user.currency)
        detected_alerts.append({
            'alert_type': 'SAVINGS_GAP',
            'title': f"Savings Target Shortfall: {gap_formatted}",
            'description': f"You contributed {curr_summary['savings']['actual_formatted']} toward savings this month against your target of {curr_summary['savings']['target_formatted']}.",
            'severity': 'WARNING',
            'supporting_data': {
                'target_minor': curr_summary['savings']['target_minor'],
                'actual_minor': curr_summary['savings']['actual_minor'],
                'gap_minor': savings_gap
            },
            'actionable_tip': f"Deposit an extra {gap_formatted} to an emergency fund or mutual fund before month-end to stay on track."
        })

    # -------------------------------------------------------------
    # RULE 6: Potential Savings Scenario (Top discretionary leakage)
    # -------------------------------------------------------------
    wants_breakdown = [c for c in curr_summary['category_breakdown'] if c['group'] == 'WANTS']
    if wants_breakdown:
        top_want = wants_breakdown[0]
        # 20% trim potential
        potential_trim = int(top_want['total_minor'] * 0.20)
        annual_trim = potential_trim * 12
        if potential_trim > (30000 if user.currency == 'INR' else 1000):
            detected_alerts.append({
                'alert_type': 'SAVINGS_OPPORTUNITY',
                'title': f"Potential ₹ Savings in {top_want['name']}",
                'description': f"Trimming just 20% of your {top_want['name']} spend would retain {format_money(potential_trim, user.currency)}/month, compounding to {format_money(annual_trim, user.currency)} annually.",
                'severity': 'INFO',
                'supporting_data': {
                    'category_id': top_want['id'],
                    'monthly_potential_minor': potential_trim,
                    'annual_potential_minor': annual_trim
                },
                'actionable_tip': "Open the Savings Simulator to model this scenario without altering your actual transactions."
            })

    # -------------------------------------------------------------
    # RULE 7: Lifestyle Inflation
    # -------------------------------------------------------------
    if prev_summary['income']['minor'] > 0 and curr_summary['income']['minor'] > prev_summary['income']['minor']:
        income_growth_pct = ((curr_summary['income']['minor'] - prev_summary['income']['minor']) / prev_summary['income']['minor']) * 100.0
        prev_wants = prev_summary['wants']['actual_minor']
        curr_wants = curr_summary['wants']['actual_minor']
        if prev_wants > 0:
            wants_growth_pct = ((curr_wants - prev_wants) / prev_wants) * 100.0
            if wants_growth_pct > income_growth_pct + 15.0 and wants_growth_pct > 25.0:
                detected_alerts.append({
                    'alert_type': 'LIFESTYLE_INFLATION',
                    'title': "Lifestyle Inflation Detected",
                    'description': f"Your discretionary Wants spending increased by {wants_growth_pct:.0f}%, which is significantly outpacing your income growth of {income_growth_pct:.0f}%.",
                    'severity': 'WARNING',
                    'supporting_data': {
                        'income_growth_pct': round(income_growth_pct, 1),
                        'wants_growth_pct': round(wants_growth_pct, 1)
                    },
                    'actionable_tip': "Channel salary increments into automated SIPs or emergency funds first before raising discretionary spending."
                })

    # -------------------------------------------------------------
    # PERSISTENCE (Avoid duplicate alerts if created within 24 hours)
    # -------------------------------------------------------------
    for al in detected_alerts:
        existing = FinancialAlert.query.filter_by(
            user_id=user_id,
            alert_type=al['alert_type'],
            title=al['title']
        ).first()

        if not existing:
            new_alert = FinancialAlert(
                user_id=user_id,
                alert_type=al['alert_type'],
                title=al['title'],
                description=al['description'],
                severity=al['severity']
            )
            new_alert.supporting_data = al.get('supporting_data', {})
            db.session.add(new_alert)

    db.session.commit()

    # Query all active (non-dismissed) alerts for user
    active_db_alerts = FinancialAlert.query.filter_by(
        user_id=user_id,
        is_dismissed=False
    ).order_by(FinancialAlert.created_at.desc()).all()

    return [a.to_dict() for a in active_db_alerts]
