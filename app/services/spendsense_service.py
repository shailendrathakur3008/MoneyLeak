"""
SpendSense — Smart Expense Leak Detector and 50/30/20 Budget Analyzer Service.

Provides:
1. Comprehensive 50/30/20 budget analysis adhering to strict accounting rules.
2. Rule-based spending leak detection grounded in verified user ledger records:
   - High discretionary spending (Wants overrun)
   - Category budget cap overruns
   - Month-over-month category spending surges (>= 25%)
   - Frequent small purchases (micro-leakage)
   - Recurring subscriptions drain & category overlap
   - Repeated purchases at the same merchant
   - Potential duplicate transactions
   - Statistical outliers / unusual transactions
   - Uncategorized transactions blindspot
   - Lifestyle inflation
   - Savings target shortfalls
3. Deduplicated, defensible potential savings calculator.
4. Auto-detection of recurring payment patterns from transaction history.
5. Small expense analysis with configurable thresholds.
6. Spending trends: daily burn-rate run-rate comparisons against previous complete month.
7. Data completeness and transparency indicators.
"""
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from calendar import monthrange
from collections import defaultdict
from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.recurring_payment import RecurringPayment
from app.models.alert import FinancialAlert
from app.services.money import format_money, to_minor_units
from app.services.budget_engine import calculate_budget_summary, get_month_date_range
from app.services.location_service import BUDGET_PRESETS


def detect_recurring_transaction_patterns(user_id: int, lookback_days: int = 120) -> List[Dict[str, Any]]:
    """
    Scans the user's historical transactions to detect recurring payment patterns
    (e.g., streaming services, utilities, gym memberships, subscriptions)
    based on repetitive merchant/description names and regular cadence.
    """
    user = db.session.get(User, user_id)
    if not user:
        return []

    cutoff_date = date.today() - timedelta(days=lookback_days)
    txns = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'EXPENSE',
        Transaction.transaction_date >= cutoff_date
    ).order_by(Transaction.transaction_date.asc()).all()

    # Group by normalized merchant or description
    groups: Dict[str, List[Transaction]] = defaultdict(list)
    for t in txns:
        norm_key = (t.merchant.strip() if t.merchant else t.description.strip()).lower()
        if len(norm_key) >= 3:
            groups[norm_key].append(t)

    # Existing registered recurring payments for the user
    existing_recurring = RecurringPayment.query.filter_by(user_id=user_id).all()
    existing_names = {r.name.strip().lower(): r for r in existing_recurring}

    patterns: List[Dict[str, Any]] = []

    for name_key, group_txns in groups.items():
        if len(group_txns) < 2:
            continue

        # Sort chronologically
        sorted_txns = sorted(group_txns, key=lambda x: x.transaction_date)
        amounts = [t.amount_minor_units for t in sorted_txns]
        dates = [t.transaction_date for t in sorted_txns]

        # Calculate amount consistency (within 8% tolerance)
        avg_amt = sum(amounts) / len(amounts)
        amount_variance = max(abs(a - avg_amt) for a in amounts) / avg_amt if avg_amt > 0 else 0

        if amount_variance > 0.12:
            # Amounts vary too widely to be a fixed recurring subscription
            continue

        # Calculate intervals in days between consecutive occurrences
        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        if not intervals:
            continue

        avg_interval = sum(intervals) / len(intervals)

        # Detect cadence
        cadence = None
        if 5 <= avg_interval <= 9:
            cadence = 'WEEKLY'
        elif 24 <= avg_interval <= 35:
            cadence = 'MONTHLY'
        elif 80 <= avg_interval <= 100:
            cadence = 'QUARTERLY'
        elif 340 <= avg_interval <= 380:
            cadence = 'YEARLY'
        else:
            # Check if occurrences happen approximately on same day of month
            dom_diffs = [abs(dates[i].day - dates[i - 1].day) for i in range(1, len(dates))]
            if dom_diffs and (sum(dom_diffs) / len(dom_diffs)) <= 3 and 20 <= avg_interval <= 40:
                cadence = 'MONTHLY'

        if not cadence:
            continue

        # Check if already registered
        matched_reg = existing_names.get(name_key)
        for r_name, r_obj in existing_names.items():
            if r_name in name_key or name_key in r_name:
                matched_reg = r_obj
                break

        display_name = sorted_txns[-1].merchant.strip() if sorted_txns[-1].merchant else sorted_txns[-1].description.strip()
        last_txn = sorted_txns[-1]
        category = last_txn.category

        # Calculate monthly equivalent
        if cadence == 'WEEKLY':
            monthly_equiv = int((avg_amt * 52) / 12)
        elif cadence == 'MONTHLY':
            monthly_equiv = int(avg_amt)
        elif cadence == 'QUARTERLY':
            monthly_equiv = int(avg_amt / 3)
        elif cadence == 'YEARLY':
            monthly_equiv = int(avg_amt / 12)
        else:
            monthly_equiv = int(avg_amt)

        confidence = "High" if len(sorted_txns) >= 3 or matched_reg else "Medium"

        patterns.append({
            'name': display_name,
            'observed_amount_minor': int(avg_amt),
            'observed_amount_formatted': format_money(int(avg_amt), user.currency),
            'monthly_equivalent_minor': monthly_equiv,
            'monthly_equivalent_formatted': format_money(monthly_equiv, user.currency),
            'annual_equivalent_minor': monthly_equiv * 12,
            'annual_equivalent_formatted': format_money(monthly_equiv * 12, user.currency),
            'frequency': cadence,
            'occurrences_count': len(sorted_txns),
            'most_recent_date': last_txn.transaction_date.isoformat(),
            'category_name': category.name if category else 'Uncategorized',
            'category_id': category.id if category else None,
            'is_registered': matched_reg is not None,
            'registered_id': matched_reg.id if matched_reg else None,
            'registered_status': matched_reg.status if matched_reg else None,
            'confidence': confidence,
            'status_label': 'Confirmed Subscription' if matched_reg else 'Possible recurring payment',
            'transaction_ids': [t.id for t in sorted_txns]
        })

    return patterns


def get_small_expenses_summary(
    user_id: int,
    year: int,
    month: int,
    threshold_minor: int = 50000,
    category_id: Optional[int] = None,
    merchant_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes low-value purchases in the given period to detect micro-spending leaks.
    """
    user = db.session.get(User, user_id)
    if not user:
        return {}

    start_date, end_date = get_month_date_range(year, month)

    query = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'EXPENSE',
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
        Transaction.amount_minor_units <= threshold_minor
    )

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    if merchant_query:
        mq = f"%{merchant_query.strip()}%"
        query = query.filter(
            (Transaction.merchant.ilike(mq)) | (Transaction.description.ilike(mq))
        )

    small_txns = query.order_by(Transaction.transaction_date.desc()).all()

    total_small_minor = sum(t.amount_minor_units for t in small_txns)
    count = len(small_txns)
    avg_minor = (total_small_minor // count) if count > 0 else 0

    # Group by merchant
    merchant_agg: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'count': 0, 'total_minor': 0})
    for t in small_txns:
        m_name = (t.merchant.strip() if t.merchant else t.description.strip()) or 'Unknown Merchant'
        merchant_agg[m_name]['count'] += 1
        merchant_agg[m_name]['total_minor'] += t.amount_minor_units

    top_merchants = []
    for m_name, agg in sorted(merchant_agg.items(), key=lambda x: x[1]['total_minor'], reverse=True)[:6]:
        top_merchants.append({
            'merchant': m_name,
            'count': agg['count'],
            'total_minor': agg['total_minor'],
            'total_formatted': format_money(agg['total_minor'], user.currency),
            'avg_formatted': format_money(agg['total_minor'] // agg['count'], user.currency)
        })

    # Total month expenses for percentage calculation
    all_expenses = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'EXPENSE',
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).all()
    all_expense_minor = sum(t.amount_minor_units for t in all_expenses)

    pct_of_total = (total_small_minor / all_expense_minor * 100.0) if all_expense_minor > 0 else 0.0

    return {
        'threshold_minor': threshold_minor,
        'threshold_formatted': format_money(threshold_minor, user.currency),
        'transaction_count': count,
        'total_minor': total_small_minor,
        'total_formatted': format_money(total_small_minor, user.currency),
        'average_minor': avg_minor,
        'average_formatted': format_money(avg_minor, user.currency),
        'pct_of_total_expenses': round(pct_of_total, 1),
        'top_merchants': top_merchants,
        'transactions': [
            {
                'id': t.id,
                'date': t.transaction_date.isoformat(),
                'description': t.description,
                'merchant': t.merchant,
                'category_name': t.category.name if t.category else 'Uncategorized',
                'amount_minor': t.amount_minor_units,
                'amount_formatted': format_money(t.amount_minor_units, user.currency)
            }
            for t in small_txns[:25]
        ]
    }


def get_spending_trends(user_id: int, year: int, month: int) -> Dict[str, Any]:
    """
    Compares current month (ongoing or complete) against the previous complete month,
    and calculates 3-month history and rising/declining category trajectories.
    """
    user = db.session.get(User, user_id)
    if not user:
        return {}

    today = date.today()
    curr_summary = calculate_budget_summary(user_id, year, month)
    curr_start, curr_end = get_month_date_range(year, month)
    days_in_curr_month = curr_end.day

    # Check if reviewing ongoing month or past complete month
    is_ongoing_curr = (year == today.year and month == today.month)
    days_elapsed_curr = min(today.day, days_in_curr_month) if is_ongoing_curr else days_in_curr_month
    days_elapsed_curr = max(1, days_elapsed_curr)

    curr_spending_minor = curr_summary['expenses']['minor']
    daily_burn_rate_minor = curr_spending_minor // days_elapsed_curr
    projected_month_end_minor = daily_burn_rate_minor * days_in_curr_month

    # Previous complete month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    prev_summary = calculate_budget_summary(user_id, prev_year, prev_month)
    _, prev_end = get_month_date_range(prev_year, prev_month)
    days_in_prev_month = prev_end.day

    prev_spending_minor = prev_summary['expenses']['minor']
    prev_daily_burn_rate_minor = prev_spending_minor // days_in_prev_month if days_in_prev_month > 0 else 0

    burn_rate_diff_pct = 0.0
    if prev_daily_burn_rate_minor > 0:
        burn_rate_diff_pct = ((daily_burn_rate_minor - prev_daily_burn_rate_minor) / prev_daily_burn_rate_minor) * 100.0

    # 3-Month Historical Series
    history = []
    for offset in range(3, 0, -1):
        # Calculate past months
        m_val = month - offset
        y_val = year
        while m_val <= 0:
            m_val += 12
            y_val -= 1

        h_summary = calculate_budget_summary(user_id, y_val, m_val)
        h_date = date(y_val, m_val, 1)
        history.append({
            'year': y_val,
            'month': m_val,
            'label': h_date.strftime('%b %Y'),
            'spending_minor': h_summary['expenses']['minor'],
            'spending_formatted': h_summary['expenses']['formatted'],
            'income_minor': h_summary['income']['minor'],
            'income_formatted': h_summary['income']['formatted'],
            'savings_rate': h_summary['savings_rate']
        })

    # Category Shifts (Rising vs Declining)
    prev_cat_map = {c['id']: c['total_minor'] for c in prev_summary['category_breakdown']}
    rising_categories = []
    declining_categories = []

    for c in curr_summary['category_breakdown']:
        c_id = c['id']
        c_curr = c['total_minor']
        c_prev = prev_cat_map.get(c_id, 0)

        # Baseline threshold of ₹400 / $10
        min_thresh = 40000 if user.currency == 'INR' else 1000
        if c_prev >= min_thresh:
            diff = c_curr - c_prev
            pct = (diff / c_prev) * 100.0
            item = {
                'id': c_id,
                'name': c['name'],
                'group': c['group'],
                'curr_minor': c_curr,
                'curr_formatted': format_money(c_curr, user.currency),
                'prev_minor': c_prev,
                'prev_formatted': format_money(c_prev, user.currency),
                'diff_minor': abs(diff),
                'diff_formatted': format_money(abs(diff), user.currency),
                'pct_change': round(pct, 1)
            }
            if pct >= 15.0:
                rising_categories.append(item)
            elif pct <= -15.0:
                declining_categories.append(item)

    rising_categories.sort(key=lambda x: x['diff_minor'], reverse=True)
    declining_categories.sort(key=lambda x: x['diff_minor'], reverse=True)

    return {
        'current_month': {
            'year': year,
            'month': month,
            'label': date(year, month, 1).strftime('%B %Y'),
            'is_ongoing': is_ongoing_curr,
            'days_in_month': days_in_curr_month,
            'days_elapsed': days_elapsed_curr,
            'total_spending_minor': curr_spending_minor,
            'total_spending_formatted': format_money(curr_spending_minor, user.currency),
            'daily_burn_rate_minor': daily_burn_rate_minor,
            'daily_burn_rate_formatted': format_money(daily_burn_rate_minor, user.currency),
            'projected_month_end_minor': projected_month_end_minor,
            'projected_month_end_formatted': format_money(projected_month_end_minor, user.currency)
        },
        'previous_month': {
            'year': prev_year,
            'month': prev_month,
            'label': date(prev_year, prev_month, 1).strftime('%B %Y'),
            'is_complete': True,
            'days_in_month': days_in_prev_month,
            'total_spending_minor': prev_spending_minor,
            'total_spending_formatted': format_money(prev_spending_minor, user.currency),
            'daily_burn_rate_minor': prev_daily_burn_rate_minor,
            'daily_burn_rate_formatted': format_money(prev_daily_burn_rate_minor, user.currency),
            'burn_rate_diff_pct': round(burn_rate_diff_pct, 1),
            'income_minor': prev_summary['income']['minor'],
            'income_formatted': prev_summary['income']['formatted'],
            'savings_rate': prev_summary['savings_rate']
        },
        'history_3_months': history,
        'rising_categories': rising_categories[:5],
        'declining_categories': declining_categories[:5]
    }


def reconcile_potential_savings(raw_findings: List[Dict[str, Any]], summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mathematically reconciles and deduplicates potential savings opportunities across
    overlapping findings to guarantee zero double-counting.
    """
    category_savings_map: Dict[int, int] = defaultdict(int)
    merchant_savings_map: Dict[str, int] = defaultdict(int)
    independent_savings_minor = 0

    category_actual_map = {c['id']: c['total_minor'] for c in summary.get('category_breakdown', [])}
    wants_actual_minor = summary.get('wants', {}).get('actual_minor', 0)

    categories_affected = set()

    for finding in raw_findings:
        # Ignore dismissed or not relevant findings
        status = finding.get('status', 'ACTIVE')
        if status in ('DISMISSED', 'NOT_RELEVANT') or finding.get('is_dismissed'):
            continue

        savings_cand = finding.get('potential_savings_minor', 0)
        if savings_cand <= 0:
            continue

        f_type = finding.get('alert_type')
        cat_id = finding.get('category_id')
        cat_name = finding.get('category_name')

        if cat_name:
            categories_affected.add(cat_name)

        if f_type == 'DUPLICATE_TRANSACTION':
            # Direct duplicate entry: independent potential savings
            independent_savings_minor += savings_cand

        elif f_type in ('CATEGORY_OVERRUN', 'SPENDING_INCREASE'):
            if cat_id:
                # Cap candidate savings to the actual category spend
                cat_spend = category_actual_map.get(cat_id, savings_cand)
                category_savings_map[cat_id] = max(category_savings_map[cat_id], min(savings_cand, cat_spend))

        elif f_type == 'REPEATED_MERCHANT':
            merchant_name = (finding.get('merchant') or '').lower()
            merchant_savings_map[merchant_name] = max(merchant_savings_map[merchant_name], savings_cand)
            if cat_id:
                # Merge into category savings without exceeding category total
                cat_spend = category_actual_map.get(cat_id, savings_cand)
                category_savings_map[cat_id] = max(category_savings_map[cat_id], min(savings_cand, cat_spend))

        elif f_type == 'SUBSCRIPTION_DRAIN':
            # Subscription reduction
            independent_savings_minor += savings_cand

        elif f_type == 'FREQUENT_SMALL_PURCHASES':
            # Micro-spending aggregate trim
            independent_savings_minor += savings_cand

        elif f_type in ('HIGH_DISCRETIONARY_SPEND', 'BUDGET_OVERRUN'):
            # Macro wants overrun
            # Will be reconciled against the sum of category-level savings
            pass

    # Sum category-level savings, capped at total WANTS spend
    total_category_savings = sum(category_savings_map.values())

    # Macro Wants overrun candidate
    wants_variance = max(0, summary.get('wants', {}).get('variance_minor', 0))
    # Take the maximum of macro wants overrun or sum of reconciled category trims, capped at wants spend
    reconciled_wants_savings = min(max(wants_variance, total_category_savings), wants_actual_minor)

    # Reconciled total monthly potential savings
    reconciled_total_monthly = reconciled_wants_savings + independent_savings_minor

    # Guarantee total savings never exceeds total actual expenses
    total_consumption = summary.get('expenses', {}).get('minor', 0)
    reconciled_total_monthly = max(0, min(reconciled_total_monthly, total_consumption))

    return {
        'monthly_potential_minor': reconciled_total_monthly,
        'annual_potential_minor': reconciled_total_monthly * 12,
        'categories_affected': sorted(list(categories_affected)),
        'reconciliation_notes': (
            "Potential savings are strictly deduplicated across overlapping categories, merchants, and macro budget targets. "
            "Annual projections are hypothetical estimates assuming consistent monthly discipline."
        )
    }


def get_spendsense_analysis(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
    """
    Main SpendSense Engine:
    Combines verified 50/30/20 accounting, rule-based leak detection, recurring analysis,
    small-expense monitoring, trend run-rates, and defensible savings calculations.
    """
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found")

    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    start_date, end_date = get_month_date_range(year, month)
    days_in_month = end_date.day
    is_ongoing_month = (year == today.year and month == today.month)
    days_elapsed = min(today.day, days_in_month) if is_ongoing_month else days_in_month
    days_remaining = max(0, days_in_month - days_elapsed)

    # 1. Base Accounting Summary
    summary = calculate_budget_summary(user_id, year, month)

    # Previous Month Summary
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    prev_summary = calculate_budget_summary(user_id, prev_year, prev_month)

    # Transactions for this period
    txns = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).all()

    expense_txns = [t for t in txns if t.transaction_type == 'EXPENSE']
    uncategorized_txns = [t for t in expense_txns if t.category_id is None]
    uncat_minor = sum(t.amount_minor_units for t in uncategorized_txns)

    # 2. RUN LEAK DETECTION RULES
    detected_alerts: List[Dict[str, Any]] = []

    # RULE 1: High Discretionary Spending (Wants Target Exceeded)
    wants_variance = summary['wants']['variance_minor']
    if wants_variance > 0:
        over_formatted = format_money(wants_variance, user.currency)
        detected_alerts.append({
            'alert_type': 'HIGH_DISCRETIONARY_SPEND',
            'title': f"Wants Budget Exceeded by {over_formatted}",
            'category_name': 'Lifestyle & Wants',
            'category_id': None,
            'actual_spending_minor': summary['wants']['actual_minor'],
            'actual_spending_formatted': summary['wants']['actual_formatted'],
            'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
            'reason': (
                f"Discretionary lifestyle spending reached {summary['wants']['actual_formatted']} "
                f"({summary['wants']['actual_pct']}% of income), exceeding your target allocation of "
                f"{summary['wants']['target_formatted']} ({summary['wants']['target_pct']}%)."
            ),
            'calculation': f"Actual Wants ({summary['wants']['actual_formatted']}) − Target ({summary['wants']['target_formatted']}) = {over_formatted} overrun",
            'suggested_action': "Review top discretionary categories (dining, food delivery, shopping) and set category caps.",
            'potential_savings_minor': min(wants_variance, summary['wants']['actual_minor']),
            'confidence': 'High',
            'severity': 'WARNING',
            'supporting_data': {
                'target_minor': summary['wants']['target_minor'],
                'actual_minor': summary['wants']['actual_minor'],
                'over_minor': wants_variance
            }
        })

    # RULE 2: Category Monthly Budget Cap Overrun
    for cat_item in summary['category_breakdown']:
        cat_id = cat_item['id']
        cat_db = db.session.get(Category, cat_id) if cat_id else None
        if cat_db and cat_db.monthly_budget_minor_units and cat_item['total_minor'] > cat_db.monthly_budget_minor_units:
            overrun = cat_item['total_minor'] - cat_db.monthly_budget_minor_units
            over_fmt = format_money(overrun, user.currency)
            cap_fmt = format_money(cat_db.monthly_budget_minor_units, user.currency)
            act_fmt = format_money(cat_item['total_minor'], user.currency)
            detected_alerts.append({
                'alert_type': 'CATEGORY_OVERRUN',
                'title': f"{cat_db.name} Exceeded Monthly Cap by {over_fmt}",
                'category_name': cat_db.name,
                'category_id': cat_id,
                'actual_spending_minor': cat_item['total_minor'],
                'actual_spending_formatted': act_fmt,
                'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
                'reason': f"Spending on {cat_db.name} reached {act_fmt}, surpassing your planned cap of {cap_fmt}.",
                'calculation': f"Actual ({act_fmt}) − Planned Cap ({cap_fmt}) = {over_fmt} overrun",
                'suggested_action': f"Pause discretionary purchases in {cat_db.name} for the rest of this month.",
                'potential_savings_minor': overrun,
                'confidence': 'High',
                'severity': 'WARNING',
                'supporting_data': {
                    'category_id': cat_id,
                    'cap_minor': cat_db.monthly_budget_minor_units,
                    'actual_minor': cat_item['total_minor']
                }
            })

    # RULE 3: Month-over-Month Category Spending Surges (>= 25%)
    prev_cat_map = {c['id']: c['total_minor'] for c in prev_summary['category_breakdown']}
    for curr_cat in summary['category_breakdown']:
        c_id = curr_cat['id']
        curr_amt = curr_cat['total_minor']
        prev_amt = prev_cat_map.get(c_id, 0)
        min_threshold = 40000 if user.currency == 'INR' else 1000

        if prev_amt >= min_threshold and curr_amt > prev_amt:
            pct_increase = ((curr_amt - prev_amt) / prev_amt) * 100.0
            if pct_increase >= 25.0:
                diff_minor = curr_amt - prev_amt
                diff_fmt = format_money(diff_minor, user.currency)
                prev_fmt = format_money(prev_amt, user.currency)
                curr_fmt = format_money(curr_amt, user.currency)

                # Defensible savings candidate: half of the excess surge if WANTS
                suggested_savings = int(diff_minor * 0.5) if curr_cat['group'] == 'WANTS' else 0

                detected_alerts.append({
                    'alert_type': 'SPENDING_INCREASE',
                    'title': f"{curr_cat['name']} jumped by {pct_increase:.0f}%",
                    'category_name': curr_cat['name'],
                    'category_id': c_id,
                    'actual_spending_minor': curr_amt,
                    'actual_spending_formatted': curr_fmt,
                    'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
                    'reason': f"Outflow on {curr_cat['name']} expanded from {prev_fmt} last month to {curr_fmt} (+{diff_fmt}).",
                    'calculation': f"(({curr_fmt} − {prev_fmt}) / {prev_fmt}) × 100 = +{pct_increase:.1f}%",
                    'suggested_action': f"Audit recent transactions in {curr_cat['name']} to verify whether this was an isolated event or continuing trend.",
                    'potential_savings_minor': suggested_savings,
                    'confidence': 'High',
                    'severity': 'INFO' if pct_increase < 50 else 'WARNING',
                    'supporting_data': {
                        'category_id': c_id,
                        'prev_minor': prev_amt,
                        'curr_minor': curr_amt,
                        'increase_pct': round(pct_increase, 1)
                    }
                })

    # RULE 4: Frequent Small Purchases (Micro-Leakage)
    small_summary = get_small_expenses_summary(user_id, year, month, threshold_minor=50000 if user.currency == 'INR' else 1000)
    if small_summary.get('transaction_count', 0) >= 5 and small_summary.get('total_minor', 0) >= (120000 if user.currency == 'INR' else 2000):
        s_total = small_summary['total_minor']
        s_count = small_summary['transaction_count']
        s_avg = small_summary['average_minor']
        # 20% trim potential
        micro_trim = int(s_total * 0.20)
        detected_alerts.append({
            'alert_type': 'FREQUENT_SMALL_PURCHASES',
            'title': f"Frequent Small Purchases Totaling {format_money(s_total, user.currency)}",
            'category_name': 'Micro-Purchases',
            'category_id': None,
            'actual_spending_minor': s_total,
            'actual_spending_formatted': format_money(s_total, user.currency),
            'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
            'reason': f"You logged {s_count} small purchases under {small_summary['threshold_formatted']}, aggregating to {format_money(s_total, user.currency)}.",
            'calculation': f"{s_count} transactions, averaging {format_money(s_avg, user.currency)} each ({small_summary['pct_of_total_expenses']}% of total expenses)",
            'suggested_action': "Consolidate daily convenience orders or allocate a weekly petty cash budget to prevent cumulative drain.",
            'potential_savings_minor': micro_trim,
            'confidence': 'Observed',
            'severity': 'INFO',
            'supporting_data': {
                'count': s_count,
                'total_minor': s_total,
                'threshold_minor': small_summary['threshold_minor']
            }
        })

    # RULE 5: Subscriptions Drain & Committed Burden
    recurr_items = RecurringPayment.query.filter_by(user_id=user_id, status='ACTIVE').all()
    if recurr_items:
        total_recurring_monthly = sum(r.monthly_equivalent_minor_units for r in recurr_items)
        annual_total = total_recurring_monthly * 12
        inc_minor = summary['income']['minor']
        recurr_pct = (total_recurring_monthly / inc_minor * 100.0) if inc_minor > 0 else 0.0

        if recurr_pct > 12.0 or len(recurr_items) >= 4:
            # Savings candidate: lowest recurring service cost
            min_recurring = min(r.monthly_equivalent_minor_units for r in recurr_items)
            detected_alerts.append({
                'alert_type': 'SUBSCRIPTION_DRAIN',
                'title': f"Active Subscriptions Commit {recurr_pct:.1f}% of Income",
                'category_name': 'Subscriptions & Recurring',
                'category_id': None,
                'actual_spending_minor': total_recurring_monthly,
                'actual_spending_formatted': format_money(total_recurring_monthly, user.currency),
                'date_range': 'Ongoing Monthly Commitments',
                'reason': f"You have {len(recurr_items)} active recurring services costing {format_money(total_recurring_monthly, user.currency)}/mo ({format_money(annual_total, user.currency)}/year).",
                'calculation': f"Committed Monthly ({format_money(total_recurring_monthly, user.currency)}) / Income ({format_money(inc_minor, user.currency)}) = {recurr_pct:.1f}%",
                'suggested_action': "Audit auto-renewing apps, streaming plans, or memberships to recover discretionary cashflow.",
                'potential_savings_minor': min_recurring,
                'confidence': 'High',
                'severity': 'WARNING' if recurr_pct > 20 else 'INFO',
                'supporting_data': {
                    'recurring_count': len(recurr_items),
                    'monthly_total_minor': total_recurring_monthly,
                    'annual_total_minor': annual_total
                }
            })

    # RULE 6: Overlapping Subscriptions in Same Category
    recurr_cat_map: Dict[int, List[RecurringPayment]] = defaultdict(list)
    for r in recurr_items:
        if r.category_id:
            recurr_cat_map[r.category_id].append(r)

    for c_id, r_list in recurr_cat_map.items():
        if len(r_list) >= 2:
            cat_obj = db.session.get(Category, c_id)
            c_name = cat_obj.name if cat_obj else 'Subscriptions'
            cat_recurr_total = sum(item.monthly_equivalent_minor_units for item in r_list)
            names_str = ", ".join(item.name for item in r_list)
            lowest_item_cost = min(item.monthly_equivalent_minor_units for item in r_list)

            detected_alerts.append({
                'alert_type': 'RECURRING_CATEGORY_OVERLAP',
                'title': f"Multiple Subscriptions in {c_name} ({len(r_list)} active)",
                'category_name': c_name,
                'category_id': c_id,
                'actual_spending_minor': cat_recurr_total,
                'actual_spending_formatted': format_money(cat_recurr_total, user.currency),
                'date_range': 'Monthly Commitments',
                'reason': f"You are paying for {len(r_list)} active services in {c_name} simultaneously ({names_str}).",
                'calculation': f"{len(r_list)} active services total {format_money(cat_recurr_total, user.currency)}/month",
                'suggested_action': f"Consider rotating between {c_name} services one at a time instead of running all active concurrently.",
                'potential_savings_minor': lowest_item_cost,
                'confidence': 'Medium',
                'severity': 'INFO',
                'supporting_data': {
                    'category_id': c_id,
                    'count': len(r_list),
                    'monthly_total_minor': cat_recurr_total
                }
            })

    # RULE 7: Repeated Purchases from Same Merchant
    merchant_counts: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'count': 0, 'total_minor': 0, 'txns': []})
    for t in expense_txns:
        m_name = (t.merchant.strip() if t.merchant else t.description.strip())
        if m_name and len(m_name) >= 3:
            merchant_counts[m_name]['count'] += 1
            merchant_counts[m_name]['total_minor'] += t.amount_minor_units
            merchant_counts[m_name]['txns'].append(t)

    for m_name, m_data in merchant_counts.items():
        min_merchant_spend = 120000 if user.currency == 'INR' else 2000
        if m_data['count'] >= 4 and m_data['total_minor'] >= min_merchant_spend:
            m_total = m_data['total_minor']
            m_count = m_data['count']
            m_avg = m_total // m_count
            m_savings = int(m_total * 0.20)
            sample_cat = m_data['txns'][0].category

            detected_alerts.append({
                'alert_type': 'REPEATED_MERCHANT',
                'title': f"Repeated Purchases at '{m_name}': {m_count} orders",
                'category_name': sample_cat.name if sample_cat else None,
                'category_id': sample_cat.id if sample_cat else None,
                'merchant': m_name,
                'actual_spending_minor': m_total,
                'actual_spending_formatted': format_money(m_total, user.currency),
                'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
                'reason': f"You ordered {m_count} times from '{m_name}' this month, spending {format_money(m_total, user.currency)}.",
                'calculation': f"{m_count} orders averaging {format_money(m_avg, user.currency)} per order",
                'suggested_action': f"Set a weekly ordering limit or batch orders from {m_name} to trim habitual spend.",
                'potential_savings_minor': m_savings,
                'confidence': 'Observed',
                'severity': 'INFO',
                'supporting_data': {
                    'merchant': m_name,
                    'count': m_count,
                    'total_minor': m_total
                }
            })

    # RULE 8: Potential Duplicate Transactions
    sorted_expenses = sorted(expense_txns, key=lambda x: (x.amount_minor_units, x.transaction_date))
    seen_duplicates = set()

    for i in range(len(sorted_expenses)):
        for j in range(i + 1, min(i + 4, len(sorted_expenses))):
            t1 = sorted_expenses[i]
            t2 = sorted_expenses[j]

            if t1.id in seen_duplicates or t2.id in seen_duplicates:
                continue

            if t1.amount_minor_units == t2.amount_minor_units and t1.amount_minor_units > 0:
                t1_desc = (t1.merchant or t1.description).strip().lower()
                t2_desc = (t2.merchant or t2.description).strip().lower()

                if t1_desc and (t1_desc == t2_desc or t1_desc in t2_desc or t2_desc in t1_desc):
                    date_diff = abs((t1.transaction_date - t2.transaction_date).days)
                    if date_diff <= 2:
                        seen_duplicates.add(t1.id)
                        seen_duplicates.add(t2.id)
                        dup_amt_fmt = format_money(t1.amount_minor_units, user.currency)
                        m_label = t1.merchant or t1.description

                        detected_alerts.append({
                            'alert_type': 'DUPLICATE_TRANSACTION',
                            'title': f"Potential Duplicate: 2 charges of {dup_amt_fmt} at '{m_label}'",
                            'category_name': t1.category.name if t1.category else None,
                            'category_id': t1.category_id,
                            'merchant': m_label,
                            'actual_spending_minor': t1.amount_minor_units * 2,
                            'actual_spending_formatted': format_money(t1.amount_minor_units * 2, user.currency),
                            'date_range': f"{t1.transaction_date} & {t2.transaction_date}",
                            'reason': f"Two matching charges of {dup_amt_fmt} logged within {date_diff} day(s) for '{m_label}'.",
                            'calculation': f"Matching amount ({dup_amt_fmt}) and description within 48 hours",
                            'suggested_action': "Verify bank or card statement to ensure you were not double-charged or recorded twice.",
                            'potential_savings_minor': t1.amount_minor_units,
                            'confidence': 'Medium',
                            'severity': 'WARNING',
                            'supporting_data': {
                                'transaction_id_1': t1.id,
                                'transaction_id_2': t2.id,
                                'amount_minor': t1.amount_minor_units
                            }
                        })

    # RULE 9: Unusual Statistical Outliers in Category
    for curr_cat in summary['category_breakdown']:
        cat_id = curr_cat['id']
        if not cat_id:
            continue
        all_txns_cat = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.category_id == cat_id,
            Transaction.transaction_type == 'EXPENSE'
        ).all()

        if len(all_txns_cat) >= 4:
            avg_amt = sum(t.amount_minor_units for t in all_txns_cat) / len(all_txns_cat)
            threshold = avg_amt * 2.5
            for t in all_txns_cat:
                if t.transaction_date >= start_date and t.transaction_date <= end_date and t.amount_minor_units > threshold:
                    ratio = t.amount_minor_units / avg_amt if avg_amt > 0 else 1.0
                    detected_alerts.append({
                        'alert_type': 'UNUSUAL_TRANSACTION',
                        'title': f"Unusual High Expense: {t.description}",
                        'category_name': curr_cat['name'],
                        'category_id': cat_id,
                        'actual_spending_minor': t.amount_minor_units,
                        'actual_spending_formatted': format_money(t.amount_minor_units, user.currency),
                        'date_range': t.transaction_date.isoformat(),
                        'reason': f"Payment of {format_money(t.amount_minor_units, user.currency)} at '{t.merchant or t.description}' is {ratio:.1f}x higher than your usual average of {format_money(int(avg_amt), user.currency)}.",
                        'calculation': f"Amount ({format_money(t.amount_minor_units, user.currency)}) is {ratio:.1f}× your category average ({format_money(int(avg_amt), user.currency)})",
                        'suggested_action': "Confirm this transaction was expected, split among group members, or corporate-reimbursable.",
                        'potential_savings_minor': 0,
                        'confidence': 'Observed',
                        'severity': 'INFO',
                        'supporting_data': {
                            'transaction_id': t.id,
                            'amount_minor': t.amount_minor_units,
                            'average_minor': int(avg_amt)
                        }
                    })
                    break

    # RULE 10: Uncategorized Transactions Blindspot
    if len(uncategorized_txns) >= 1 and uncat_minor >= (50000 if user.currency == 'INR' else 1000):
        detected_alerts.append({
            'alert_type': 'UNCATEGORIZED_TRANSACTIONS',
            'title': f"{len(uncategorized_txns)} Uncategorized Transactions ({format_money(uncat_minor, user.currency)})",
            'category_name': 'Uncategorized',
            'category_id': None,
            'actual_spending_minor': uncat_minor,
            'actual_spending_formatted': format_money(uncat_minor, user.currency),
            'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
            'reason': f"You have {len(uncategorized_txns)} recorded expenses without a designated category, obscuring 50/30/20 visibility.",
            'calculation': f"{len(uncategorized_txns)} transactions totaling {format_money(uncat_minor, user.currency)} missing categories",
            'suggested_action': "Assign categories in the Transactions Ledger to reveal full spending distribution.",
            'potential_savings_minor': 0,
            'confidence': 'High',
            'severity': 'INFO',
            'supporting_data': {
                'count': len(uncategorized_txns),
                'total_minor': uncat_minor
            }
        })

    # RULE 11: Savings Target Shortfall
    savings_gap = summary['savings']['gap_minor']
    if len(txns) >= 3 and savings_gap > 0 and summary['income']['minor'] > 0:
        gap_fmt = format_money(savings_gap, user.currency)
        detected_alerts.append({
            'alert_type': 'SAVINGS_GAP',
            'title': f"Savings Target Shortfall: {gap_fmt}",
            'category_name': 'Savings & Wealth',
            'category_id': None,
            'actual_spending_minor': summary['savings']['actual_minor'],
            'actual_spending_formatted': summary['savings']['actual_formatted'],
            'date_range': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
            'reason': f"You contributed {summary['savings']['actual_formatted']} toward savings this month against your target of {summary['savings']['target_formatted']}.",
            'calculation': f"Target ({summary['savings']['target_formatted']}) − Contributed ({summary['savings']['actual_formatted']}) = {gap_fmt} gap",
            'suggested_action': f"Transfer an extra {gap_fmt} into an emergency fund or mutual fund SIP to achieve your savings goal.",
            'potential_savings_minor': 0,
            'confidence': 'High',
            'severity': 'WARNING',
            'supporting_data': {
                'target_minor': summary['savings']['target_minor'],
                'actual_minor': summary['savings']['actual_minor'],
                'gap_minor': savings_gap
            }
        })

    # RULE 12: Lifestyle Inflation
    if prev_summary['income']['minor'] > 0 and summary['income']['minor'] > prev_summary['income']['minor']:
        income_growth_pct = ((summary['income']['minor'] - prev_summary['income']['minor']) / prev_summary['income']['minor']) * 100.0
        prev_wants = prev_summary['wants']['actual_minor']
        curr_wants = summary['wants']['actual_minor']
        if prev_wants > 0:
            wants_growth_pct = ((curr_wants - prev_wants) / prev_wants) * 100.0
            if wants_growth_pct > income_growth_pct + 15.0 and wants_growth_pct > 25.0:
                diff_wants = curr_wants - prev_wants
                detected_alerts.append({
                    'alert_type': 'LIFESTYLE_INFLATION',
                    'title': "Lifestyle Inflation Detected",
                    'category_name': 'Lifestyle & Wants',
                    'category_id': None,
                    'actual_spending_minor': curr_wants,
                    'actual_spending_formatted': summary['wants']['actual_formatted'],
                    'date_range': f"MoM ({prev_summary['period']['month']}/{prev_summary['period']['year']} → {month}/{year})",
                    'reason': f"Discretionary Wants spending expanded by {wants_growth_pct:.0f}%, which is outpacing income growth of {income_growth_pct:.0f}%.",
                    'calculation': f"Wants grew +{wants_growth_pct:.1f}% vs Income grew +{income_growth_pct:.1f}%",
                    'suggested_action': "Direct salary increments into automated recurring investments before elevating lifestyle expenses.",
                    'potential_savings_minor': int(diff_wants * 0.30),
                    'confidence': 'Medium',
                    'severity': 'WARNING',
                    'supporting_data': {
                        'income_growth_pct': round(income_growth_pct, 1),
                        'wants_growth_pct': round(wants_growth_pct, 1)
                    }
                })

    # 3. PERSISTENCE & USER ACTION RECONCILIATION
    # Synchronize detected alerts with database records
    db_alerts_map = {
        (a.alert_type, a.title): a
        for a in FinancialAlert.query.filter_by(user_id=user_id).all()
    }

    final_findings: List[Dict[str, Any]] = []

    for alert_data in detected_alerts:
        key = (alert_data['alert_type'], alert_data['title'])
        db_alert = db_alerts_map.get(key)

        if not db_alert:
            db_alert = FinancialAlert(
                user_id=user_id,
                alert_type=alert_data['alert_type'],
                title=alert_data['title'],
                description=alert_data['reason'],
                severity=alert_data['severity']
            )
            meta = {
                'category_name': alert_data.get('category_name'),
                'category_id': alert_data.get('category_id'),
                'merchant': alert_data.get('merchant'),
                'actual_spending_minor': alert_data['actual_spending_minor'],
                'calculation': alert_data['calculation'],
                'suggested_action': alert_data['suggested_action'],
                'potential_savings_minor': alert_data['potential_savings_minor'],
                'confidence': alert_data['confidence'],
                'date_range': alert_data['date_range'],
                'status': 'ACTIVE',
                'supporting_data': alert_data.get('supporting_data', {})
            }
            db_alert.supporting_data = meta
            db.session.add(db_alert)
            db.session.flush()
            db_alerts_map[key] = db_alert

        # Read stored user preferences / status
        stored_meta = db_alert.supporting_data or {}
        user_status = stored_meta.get('status', 'ACTIVE')
        if db_alert.is_dismissed and user_status == 'ACTIVE':
            user_status = 'DISMISSED'

        custom_target_minor = stored_meta.get('custom_target_minor')
        potential_savings_minor = alert_data['potential_savings_minor']
        if custom_target_minor is not None:
            # User set a custom target
            potential_savings_minor = max(0, alert_data['actual_spending_minor'] - custom_target_minor)

        finding_obj = {
            'id': db_alert.id,
            'user_id': user_id,
            'alert_type': db_alert.alert_type,
            'title': db_alert.title,
            'description': alert_data['reason'],
            'severity': db_alert.severity,
            'category_name': alert_data.get('category_name'),
            'category_id': alert_data.get('category_id'),
            'merchant': alert_data.get('merchant'),
            'actual_spending_minor': alert_data['actual_spending_minor'],
            'actual_spending_formatted': alert_data['actual_spending_formatted'],
            'date_range': alert_data['date_range'],
            'reason': alert_data['reason'],
            'calculation': alert_data['calculation'],
            'suggested_action': alert_data['suggested_action'],
            'potential_savings_minor': potential_savings_minor,
            'potential_savings_formatted': format_money(potential_savings_minor, user.currency),
            'potential_annual_savings_minor': potential_savings_minor * 12,
            'potential_annual_savings_formatted': format_money(potential_savings_minor * 12, user.currency),
            'confidence': alert_data['confidence'],
            'status': user_status,
            'is_dismissed': db_alert.is_dismissed,
            'custom_target_minor': custom_target_minor,
            'custom_target_formatted': format_money(custom_target_minor, user.currency) if custom_target_minor else None,
            'created_at': db_alert.created_at.isoformat() if db_alert.created_at else None,
            'dismissed_at': db_alert.dismissed_at.isoformat() if db_alert.dismissed_at else None,
            'supporting_data': alert_data.get('supporting_data', {})
        }
        final_findings.append(finding_obj)

    db.session.commit()

    # 4. RECONCILE DEDUPLICATED SAVINGS
    savings_summary = reconcile_potential_savings(final_findings, summary)

    # 5. RECURRING & SUBSCRIPTIONS ANALYSIS
    recurring_patterns = detect_recurring_transaction_patterns(user_id, lookback_days=120)
    confirmed_recurring_list = [r.to_dict() for r in recurr_items]
    for r_item in confirmed_recurring_list:
        r_item['formatted_amount'] = format_money(r_item['amount_minor_units'], user.currency)
        r_item['formatted_monthly'] = format_money(r_item['monthly_equivalent_minor_units'], user.currency)
        r_item['formatted_annual'] = format_money(r_item['annual_cost_minor_units'], user.currency)

    total_monthly_committed = sum(r['monthly_equivalent_minor_units'] for r in confirmed_recurring_list)
    income_committed_pct = (total_monthly_committed / summary['income']['minor'] * 100.0) if summary['income']['minor'] > 0 else 0.0

    # 6. SPENDING TREND ANALYSIS
    trends = get_spending_trends(user_id, year, month)

    # 7. BUDGET 50/30/20 ANALYZER CONTEXT
    preset_key = user.budget_preset or 'standard'
    active_preset = BUDGET_PRESETS.get(preset_key, BUDGET_PRESETS['standard'])

    # Contextual explanations for Needs overrun
    needs_explanation = "Needs are within healthy limits."
    needs_action = "Maintain disciplined essential living expenses."
    if summary['needs']['is_over_budget']:
        if user.rent_or_emi_minor_units > 0 or user.location_tier == 'METRO':
            needs_explanation = (
                f"Needs reached {summary['needs']['actual_pct']}% of income. "
                "In metropolitan regions or when supporting high rent/home EMIs, essential costs often exceed 50%."
            )
            needs_action = "Consider adopting the 'High Essential-Cost (60/20/20)' budget preset to align planning with reality."
        else:
            needs_explanation = f"Essential expenses exceeded your {summary['needs']['target_pct']}% allocation by {format_money(summary['needs']['variance_minor'], user.currency)}."
            needs_action = "Review utilities, grocery bills, and transport costs to identify potential efficiency gains."

    # Contextual explanation for Wants
    wants_explanation = "Lifestyle spending is well within budget targets."
    wants_action = "Continue enjoying lifestyle purchases within your target cap."
    if summary['wants']['is_over_budget']:
        wants_explanation = (
            f"Wants spending represents {summary['wants']['actual_pct']}% of income, exceeding your target by "
            f"{format_money(summary['wants']['variance_minor'], user.currency)}."
        )
        wants_action = "Set spending caps on top lifestyle categories (dining out, food delivery, shopping)."

    # Contextual explanation for Savings
    savings_explanation = "Savings target achieved! Strong financial foundation."
    savings_action = "Continue automated investments and SIP contributions."
    if not summary['savings']['is_met']:
        savings_explanation = (
            f"Savings contributions reached {summary['savings']['actual_pct']}% of income against your target of "
            f"{summary['savings']['target_pct']}%, leaving a shortfall of {format_money(summary['savings']['gap_minor'], user.currency)}."
        )
        savings_action = "Allocate monthly surplus directly into automated mutual fund SIPs or recurring deposits."

    # 8. DATA COMPLETENESS INDICATOR
    completeness_notes = []
    completeness_score = 100

    if is_ongoing_month:
        completeness_notes.append(f"Ongoing month: Day {days_elapsed} of {days_in_month}. Figures reflect month-to-date run-rates.")
        completeness_score -= 10
    else:
        completeness_notes.append("Complete historical month.")

    if len(txns) < 5:
        completeness_notes.append("Few transactions recorded this month. Add more transactions to enhance leak accuracy.")
        completeness_score -= 20

    if summary['income']['is_fallback_baseline']:
        completeness_notes.append("Using baseline income from profile settings. No explicit monthly income record logged.")
        completeness_score -= 10

    if len(uncategorized_txns) > 0:
        completeness_notes.append(f"{len(uncategorized_txns)} uncategorized transaction(s) detected. Categorize them to improve accuracy.")
        completeness_score -= min(20, len(uncategorized_txns) * 5)

    completeness_score = max(20, completeness_score)

    return {
        'period': {
            'year': year,
            'month': month,
            'label': date(year, month, 1).strftime('%B %Y'),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days_in_month': days_in_month,
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'is_ongoing_month': is_ongoing_month,
            'status_label': f"Ongoing (Day {days_elapsed} of {days_in_month})" if is_ongoing_month else "Complete Month"
        },
        'income': {
            'recognized_minor': summary['income']['minor'],
            'recognized_formatted': summary['income']['formatted'],
            'is_fallback_baseline': summary['income']['is_fallback_baseline'],
            'baseline_configured_minor': user.monthly_income_minor_units or 0,
            'baseline_configured_formatted': format_money(user.monthly_income_minor_units or 0, user.currency)
        },
        'spending': {
            'total_consumption_minor': summary['expenses']['minor'],
            'total_consumption_formatted': summary['expenses']['formatted'],
            'total_outflow_minor': summary['total_outflow']['minor'],
            'total_outflow_formatted': summary['total_outflow']['formatted'],
            'daily_burn_rate_minor': trends['current_month']['daily_burn_rate_minor'],
            'daily_burn_rate_formatted': trends['current_month']['daily_burn_rate_formatted'],
            'projected_month_end_minor': trends['current_month']['projected_month_end_minor'],
            'projected_month_end_formatted': trends['current_month']['projected_month_end_formatted'],
            'transaction_count': len(txns),
            'expense_count': len(expense_txns),
            'uncategorized_count': len(uncategorized_txns),
            'uncategorized_minor': uncat_minor,
            'uncategorized_formatted': format_money(uncat_minor, user.currency)
        },
        'distribution_50_30_20': {
            'preset': {
                'id': preset_key,
                'title': active_preset['title'],
                'subtitle': active_preset['subtitle']
            },
            'location_tier': user.location_tier,
            'needs': {
                **summary['needs'],
                'status': 'Over Target' if summary['needs']['is_over_budget'] else 'On Track',
                'explanation': needs_explanation,
                'recommended_action': needs_action
            },
            'wants': {
                **summary['wants'],
                'status': 'Over Target' if summary['wants']['is_over_budget'] else 'On Track',
                'explanation': wants_explanation,
                'recommended_action': wants_action
            },
            'savings': {
                **summary['savings'],
                'status': 'Target Met' if summary['savings']['is_met'] else 'Shortfall',
                'explanation': savings_explanation,
                'recommended_action': savings_action
            },
            'surplus': summary['surplus'],
            'savings_rate': summary['savings_rate'],
            'category_breakdown': summary['category_breakdown']
        },
        'findings': final_findings,
        'active_findings_count': len([f for f in final_findings if f['status'] == 'ACTIVE' and not f['is_dismissed']]),
        'potential_savings_summary': {
            'monthly_potential_minor': savings_summary['monthly_potential_minor'],
            'monthly_potential_formatted': format_money(savings_summary['monthly_potential_minor'], user.currency),
            'annual_potential_minor': savings_summary['annual_potential_minor'],
            'annual_potential_formatted': format_money(savings_summary['annual_potential_minor'], user.currency),
            'categories_affected': savings_summary['categories_affected'],
            'reconciliation_notes': savings_summary['reconciliation_notes']
        },
        'subscriptions_and_recurring': {
            'confirmed_items': confirmed_recurring_list,
            'detected_patterns': recurring_patterns,
            'total_monthly_committed_minor': total_monthly_committed,
            'total_monthly_committed_formatted': format_money(total_monthly_committed, user.currency),
            'total_annual_committed_minor': total_monthly_committed * 12,
            'total_annual_committed_formatted': format_money(total_monthly_committed * 12, user.currency),
            'income_committed_pct': round(income_committed_pct, 1)
        },
        'small_expense_analysis': small_summary,
        'trends': trends,
        'data_completeness': {
            'is_complete_month': not is_ongoing_month,
            'days_passed': days_elapsed,
            'days_total': days_in_month,
            'transaction_count': len(txns),
            'has_income': summary['income']['minor'] > 0,
            'uncategorized_count': len(uncategorized_txns),
            'completeness_score': completeness_score,
            'notes': completeness_notes
        }
    }


def apply_finding_action(user_id: int, alert_id: int, action: str, custom_target_minor: Optional[int] = None) -> Dict[str, Any]:
    """
    Applies user action to a leak finding:
    - 'dismiss': dismisses finding
    - 'not_relevant': marks finding as not relevant
    - 'accept_target': marks finding as target accepted
    - 'set_custom_target': saves user custom spending target
    - 'reset': restores finding to active state
    """
    alert = FinancialAlert.query.filter_by(id=alert_id, user_id=user_id).first()
    if not alert:
        return {'success': False, 'error': 'Finding not found.'}

    data = alert.supporting_data.copy() if alert.supporting_data else {}

    action_norm = (action or '').lower()

    if action_norm == 'dismiss':
        alert.is_dismissed = True
        alert.dismissed_at = datetime.utcnow()
        data['status'] = 'DISMISSED'

    elif action_norm == 'not_relevant':
        alert.is_dismissed = True
        alert.dismissed_at = datetime.utcnow()
        data['status'] = 'NOT_RELEVANT'

    elif action_norm == 'accept_target':
        alert.is_dismissed = False
        alert.dismissed_at = None
        data['status'] = 'TARGET_SET'
        # Keep suggested target
        if 'custom_target_minor' not in data and 'actual_spending_minor' in data and 'potential_savings_minor' in data:
            data['custom_target_minor'] = max(0, data['actual_spending_minor'] - data['potential_savings_minor'])

    elif action_norm == 'set_custom_target':
        alert.is_dismissed = False
        alert.dismissed_at = None
        data['status'] = 'TARGET_SET'
        if custom_target_minor is not None:
            data['custom_target_minor'] = max(0, int(custom_target_minor))

    elif action_norm == 'reset':
        alert.is_dismissed = False
        alert.dismissed_at = None
        data['status'] = 'ACTIVE'
        data.pop('custom_target_minor', None)

    else:
        return {'success': False, 'error': f'Unsupported action: {action}'}

    alert.supporting_data = data
    db.session.commit()

    return {
        'success': True,
        'message': f'Finding updated ({action_norm}).',
        'alert_id': alert.id,
        'status': data.get('status', 'ACTIVE'),
        'is_dismissed': alert.is_dismissed
    }


def get_finding_transaction_evidence(user_id: int, alert_id: int, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Returns the specific ledger transactions supporting a given leak alert.
    """
    user = db.session.get(User, user_id)
    if not user:
        return []

    alert = FinancialAlert.query.filter_by(id=alert_id, user_id=user_id).first()
    if not alert:
        return []

    data = alert.supporting_data or {}
    f_type = alert.alert_type

    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    start_date, end_date = get_month_date_range(year, month)

    txns: List[Transaction] = []

    if f_type == 'DUPLICATE_TRANSACTION':
        t1_id = data.get('supporting_data', {}).get('transaction_id_1') or data.get('transaction_id_1')
        t2_id = data.get('supporting_data', {}).get('transaction_id_2') or data.get('transaction_id_2')
        ids = [i for i in [t1_id, t2_id] if i]
        if ids:
            txns = Transaction.query.filter(Transaction.user_id == user_id, Transaction.id.in_(ids)).all()

    elif f_type == 'UNUSUAL_TRANSACTION':
        t_id = data.get('supporting_data', {}).get('transaction_id') or data.get('transaction_id')
        if t_id:
            txns = Transaction.query.filter(Transaction.user_id == user_id, Transaction.id == t_id).all()

    elif f_type == 'REPEATED_MERCHANT':
        m_name = data.get('merchant')
        if m_name:
            txns = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'EXPENSE',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                (Transaction.merchant.ilike(f"%{m_name}%")) | (Transaction.description.ilike(f"%{m_name}%"))
            ).order_by(Transaction.transaction_date.desc()).all()

    elif f_type in ('CATEGORY_OVERRUN', 'SPENDING_INCREASE'):
        c_id = data.get('category_id') or data.get('supporting_data', {}).get('category_id')
        if c_id:
            txns = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.category_id == c_id,
                Transaction.transaction_type == 'EXPENSE',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).order_by(Transaction.transaction_date.desc()).all()

    elif f_type == 'FREQUENT_SMALL_PURCHASES':
        threshold = data.get('supporting_data', {}).get('threshold_minor') or (50000 if user.currency == 'INR' else 1000)
        txns = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'EXPENSE',
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.amount_minor_units <= threshold
        ).order_by(Transaction.transaction_date.desc()).limit(20).all()

    elif f_type == 'UNCATEGORIZED_TRANSACTIONS':
        txns = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'EXPENSE',
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.category_id.is_(None)
        ).order_by(Transaction.transaction_date.desc()).all()

    elif f_type in ('HIGH_DISCRETIONARY_SPEND', 'BUDGET_OVERRUN'):
        # Show top Wants expenses
        txns = Transaction.query.join(Category, Transaction.category_id == Category.id, isouter=True).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'EXPENSE',
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Category.budget_group == 'WANTS'
        ).order_by(Transaction.amount_minor_units.desc()).limit(15).all()

    return [
        {
            'id': t.id,
            'date': t.transaction_date.isoformat(),
            'description': t.description,
            'merchant': t.merchant or '',
            'category_name': t.category.name if t.category else 'Uncategorized',
            'amount_minor': t.amount_minor_units,
            'amount_formatted': format_money(t.amount_minor_units, user.currency)
        }
        for t in txns
    ]

