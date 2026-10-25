"""
Central 50/30/20 Budgeting Engine and Accounting Logic for MoneyLeak.

This engine serves as the single source of truth for all financial figures.
The dashboard, reports, alerts, and simulator invoke these functions directly.
"""
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from calendar import monthrange
from sqlalchemy import extract, func

from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.income import IncomeRecord
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.goal import GoalContribution
from app.services.money import format_money, from_minor_units

# Default 50/30/20 Distribution
DEFAULT_NEEDS_PCT = 50.0
DEFAULT_WANTS_PCT = 30.0
DEFAULT_SAVINGS_PCT = 20.0

DEFAULT_SYSTEM_CATEGORIES = [
    # NEEDS (EXPENSE)
    {'name': 'Housing & Rent', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'home', 'desc': 'Rent, maintenance, home insurance'},
    {'name': 'Essential Groceries', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'shopping-cart', 'desc': 'Supermarket staples, vegetables, milk'},
    {'name': 'Utilities (Power, Water, Gas)', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'zap', 'desc': 'Electricity, piped gas, water bill'},
    {'name': 'Essential Commute & Fuel', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'navigation', 'desc': 'Metro, bus pass, vehicle fuel'},
    {'name': 'Healthcare & Pharmacy', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'activity', 'desc': 'Prescriptions, doctor visits, health cover'},
    {'name': 'Basic Internet & Mobile', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'wifi', 'desc': 'Broadband, cellular recharge'},
    {'name': 'Minimum Loan EMIs', 'group': 'NEEDS', 'type': 'DEBT_REPAYMENT', 'icon': 'credit-card', 'desc': 'Contractual loan repayments'},
    # WANTS (EXPENSE)
    {'name': 'Dining Out & Cafes', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'coffee', 'desc': 'Restaurants, coffee shops, bakeries'},
    {'name': 'Food Delivery Apps', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'shopping-bag', 'desc': 'Zomato, Swiggy, takeout orders'},
    {'name': 'Entertainment & Outings', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'film', 'desc': 'Movies, concerts, clubbing'},
    {'name': 'Shopping & Lifestyle', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'package', 'desc': 'Clothes, accessories, impulse purchases'},
    {'name': 'Subscriptions & Streaming', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'tv', 'desc': 'Netflix, Spotify, Prime, SaaS'},
    {'name': 'Vacation & Leisure Travel', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'compass', 'desc': 'Flights, hotels, weekend getaways'},
    {'name': 'Gadgets & Upgrades', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'smartphone', 'desc': 'Electronics, gaming, optional tech'},
    # SAVINGS / INVESTMENTS (SAVINGS_CONTRIBUTION)
    {'name': 'Mutual Funds & Stocks', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'trending-up', 'desc': 'Systematic investment plans (SIP)'},
    {'name': 'Emergency Fund', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'shield', 'desc': '3-6 months liquid safety net'},
    {'name': 'Fixed Deposit / Savings Acc', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'archive', 'desc': 'High-yield recurring/fixed deposit'},
    {'name': 'Additional Debt Prepayment', 'group': 'SAVINGS', 'type': 'DEBT_REPAYMENT', 'icon': 'check-circle', 'desc': 'Extra principal repayment'},
    {'name': 'Retirement & NPS', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'umbrella', 'desc': 'Long term pension & wealth builders'},
    {'name': 'Gold & Precious Metals', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'award', 'desc': 'Gold ETFs and sovereign gold bonds'},
    # INCOME
    {'name': 'Salary', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'briefcase', 'desc': 'Monthly paycheck and employment wages'},
    {'name': 'Freelance & Consulting', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'laptop', 'desc': 'Freelance clients and consulting income'},
    {'name': 'Business Income', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'trending-up', 'desc': 'Business operations and company revenue'},
    {'name': 'Investment Dividends', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'pie-chart', 'desc': 'Dividends, capital gains, and bond yield'},
    # TRANSFER
    {'name': 'Account Transfer', 'group': 'SAVINGS', 'type': 'TRANSFER', 'icon': 'repeat', 'desc': 'Inter-account or wallet transfer'},
    # REFUND
    {'name': 'Refund & Cashbacks', 'group': 'NEEDS', 'type': 'REFUND', 'icon': 'corner-down-left', 'desc': 'Merchant refunds and corporate expense claims'},
]

# Student Specific Suggested Categories
STUDENT_DEFAULT_CATEGORIES = [
    {'name': 'Education Fees', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'book-open', 'desc': 'Tuition fees, semester charges, exam fees'},
    {'name': 'Books and Stationery', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'book', 'desc': 'Textbooks, notebooks, study material'},
    {'name': 'Food', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'utensils', 'desc': 'Hostel mess, canteen, daily meals'},
    {'name': 'Transport', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'bus', 'desc': 'Bus pass, metro, campus commute'},
    {'name': 'Accommodation', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'home', 'desc': 'Hostel rent, PG, student housing'},
    {'name': 'Shopping', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'shopping-bag', 'desc': 'Apparel, shoes, personal items'},
    {'name': 'Entertainment', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'film', 'desc': 'Movies, gaming, outings, campus events'},
    {'name': 'Subscriptions', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'tv', 'desc': 'Streaming, student Spotify, cloud tools'},
    {'name': 'Part-Time Income', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'briefcase', 'desc': 'Tutoring, internships, campus jobs'},
    {'name': 'Scholarship Income', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'award', 'desc': 'Academic merit grants, stipends'},
    {'name': 'Family Allowance', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'gift', 'desc': 'Pocket money, parent allowance'},
    {'name': 'Savings', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'shield', 'desc': 'Emergency cushion, student deposit'},
    {'name': 'Investments', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'trending-up', 'desc': 'Micro-SIPs, index funds, gold'},
]

# Salaried Employee Suggested Categories
SALARIED_DEFAULT_CATEGORIES = [
    {'name': 'Salary', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'briefcase', 'desc': 'Monthly salary and employer paycheck'},
    {'name': 'Bonuses', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'award', 'desc': 'Annual bonus and performance incentives'},
    {'name': 'Other Income', 'group': 'SAVINGS', 'type': 'INCOME', 'icon': 'plus-circle', 'desc': 'Dividends, freelance, consulting'},
    {'name': 'Rent', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'home', 'desc': 'Apartment rent, maintenance, home EMI'},
    {'name': 'Groceries', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'shopping-cart', 'desc': 'Supermarket, vegetables, household staples'},
    {'name': 'Utilities', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'zap', 'desc': 'Power, piped gas, water bill, broadband'},
    {'name': 'Transport', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'navigation', 'desc': 'Vehicle fuel, cab rides, metro pass'},
    {'name': 'Insurance', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'shield-check', 'desc': 'Life cover, medical and motor insurance'},
    {'name': 'Healthcare', 'group': 'NEEDS', 'type': 'EXPENSE', 'icon': 'activity', 'desc': 'Doctor checkups, pharmacy, diagnostics'},
    {'name': 'Subscriptions', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'tv', 'desc': 'OTT streaming, gym, digital services'},
    {'name': 'Shopping', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'shopping-bag', 'desc': 'Clothing, accessories, electronics'},
    {'name': 'Entertainment', 'group': 'WANTS', 'type': 'EXPENSE', 'icon': 'film', 'desc': 'Dining out, weekend trips, recreation'},
    {'name': 'Savings', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'piggy-bank', 'desc': 'Emergency fund, recurring deposits'},
    {'name': 'Investments', 'group': 'SAVINGS', 'type': 'SAVINGS_CONTRIBUTION', 'icon': 'trending-up', 'desc': 'Mutual funds, SIPs, stocks, gold'},
]


def seed_default_categories(user: User):
    """Seed baseline categories for a user if they do not exist."""
    existing_names = {c.name.strip().lower() for c in Category.query.filter_by(user_id=user.id).all()}

    order = 1
    for item in DEFAULT_SYSTEM_CATEGORIES:
        if item['name'].strip().lower() in existing_names:
            continue
        cat = Category(
            user_id=user.id,
            name=item['name'],
            budget_group=item['group'],
            transaction_type=item.get('type', 'EXPENSE'),
            description=item['desc'],
            icon=item['icon'],
            display_order=order,
            is_active=True,
            is_archived=False
        )
        db.session.add(cat)
        order += 1
    db.session.commit()


def seed_categories_for_user_type(user: User, user_type: str, selected_names: List[str] = None):
    """
    Seed or activate recommended categories based on employment status (Student vs Salaried).
    Avoids duplicate categories if they already exist, respecting existing user categories.
    """
    source_list = STUDENT_DEFAULT_CATEGORIES if user_type == 'student' else SALARIED_DEFAULT_CATEGORIES
    existing_cats = {c.name.strip().lower(): c for c in Category.query.filter_by(user_id=user.id).all()}
    
    # Filter by selected_names if user customized them in onboarding Step 4
    selected_set = {s.strip().lower() for s in selected_names} if selected_names else None

    order = len(existing_cats) + 1
    for item in source_list:
        name_lower = item['name'].strip().lower()
        if selected_set is not None and name_lower not in selected_set:
            continue
        
        if name_lower in existing_cats:
            # Re-activate if archived or inactive
            existing = existing_cats[name_lower]
            existing.is_active = True
            existing.is_archived = False
        else:
            cat = Category(
                user_id=user.id,
                name=item['name'],
                budget_group=item['group'],
                transaction_type=item.get('type', 'EXPENSE'),
                description=item['desc'],
                icon=item['icon'],
                display_order=order,
                is_active=True,
                is_archived=False
            )
            db.session.add(cat)
            existing_cats[name_lower] = cat
            order += 1
            
    db.session.commit()


def get_user_budget_distribution(user_id: int) -> Dict[str, float]:
    """Return user's customized budget percentages or default 50/30/20."""
    budget = Budget.query.filter_by(user_id=user_id).order_by(Budget.created_at.desc()).first()
    if budget:
        return {
            'needs': float(budget.needs_percentage),
            'wants': float(budget.wants_percentage),
            'savings': float(budget.savings_percentage)
        }
    return {
        'needs': DEFAULT_NEEDS_PCT,
        'wants': DEFAULT_WANTS_PCT,
        'savings': DEFAULT_SAVINGS_PCT
    }


def get_month_date_range(year: int, month: int):
    """Return (start_date, end_date) for a given year and month."""
    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    return start_date, end_date


def calculate_budget_summary(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculate comprehensive budget analytics for a user in the given month.
    All figures in minor units unless explicitly indicated.
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

    # 1. Recognized Income
    # Sum IncomeRecord in period
    incomes = IncomeRecord.query.filter(
        IncomeRecord.user_id == user_id,
        IncomeRecord.received_date >= start_date,
        IncomeRecord.received_date <= end_date
    ).all()

    recorded_income_minor = sum(inc.amount_minor_units for inc in incomes)
    # If no specific income records entered for this period, fallback to user's configured baseline monthly income
    recognized_income_minor = recorded_income_minor if recorded_income_minor > 0 else (user.monthly_income_minor_units or 0)

    # 2. Transactions query for period
    txns = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).all()

    # 3. Aggregation by Accounting Rules
    needs_actual_minor = 0
    wants_actual_minor = 0
    savings_actual_minor = 0
    refunds_minor = 0
    transfers_minor = 0
    consumption_expenses_minor = 0

    category_spending_map: Dict[int, Dict[str, Any]] = {}

    for txn in txns:
        t_type = txn.transaction_type.upper()
        amt = txn.amount_minor_units
        cat = txn.category
        group = cat.budget_group.upper() if cat else 'WANTS'

        # Record per-category spending for breakdown
        cat_id = txn.category_id or 0
        cat_name = cat.name if cat else 'Uncategorized'
        cat_icon = cat.icon if cat else 'tag'

        if cat_id not in category_spending_map:
            category_spending_map[cat_id] = {
                'id': cat_id,
                'name': cat_name,
                'group': group,
                'icon': cat_icon,
                'total_minor': 0,
                'tx_count': 0
            }

        if t_type == 'EXPENSE':
            category_spending_map[cat_id]['total_minor'] += amt
            category_spending_map[cat_id]['tx_count'] += 1
            consumption_expenses_minor += amt
            if group == 'NEEDS':
                needs_actual_minor += amt
            elif group == 'WANTS':
                wants_actual_minor += amt
            elif group == 'SAVINGS':
                savings_actual_minor += amt

        elif t_type == 'REFUND':
            # Refunds reduce category outflow and total consumption
            category_spending_map[cat_id]['total_minor'] -= amt
            refunds_minor += amt
            consumption_expenses_minor -= amt
            if group == 'NEEDS':
                needs_actual_minor = max(0, needs_actual_minor - amt)
            elif group == 'WANTS':
                wants_actual_minor = max(0, wants_actual_minor - amt)
            elif group == 'SAVINGS':
                savings_actual_minor = max(0, savings_actual_minor - amt)

        elif t_type == 'SAVINGS_CONTRIBUTION':
            # Direct savings contribution (not treated as consumption expense)
            category_spending_map[cat_id]['total_minor'] += amt
            category_spending_map[cat_id]['tx_count'] += 1
            savings_actual_minor += amt

        elif t_type == 'DEBT_REPAYMENT':
            # Extra debt repayment classified as savings/balance-sheet improvement
            category_spending_map[cat_id]['total_minor'] += amt
            category_spending_map[cat_id]['tx_count'] += 1
            if group == 'NEEDS':
                # Minimum required EMI counts in Needs
                needs_actual_minor += amt
                consumption_expenses_minor += amt
            else:
                # Additional prepayments count towards savings
                savings_actual_minor += amt

        elif t_type == 'TRANSFER':
            # Pure transfer between own accounts: neutral cash
            transfers_minor += amt

    # Also account for goal contributions logged during this period that are not already in transactions
    goal_contribs = GoalContribution.query.filter(
        GoalContribution.user_id == user_id,
        GoalContribution.contribution_date >= start_date,
        GoalContribution.contribution_date <= end_date
    ).all()
    goal_contrib_sum = sum(gc.amount_minor_units for gc in goal_contribs)
    # If the user logged goal contributions, ensure they are reflected in actual savings if not duplicate
    if goal_contrib_sum > 0 and savings_actual_minor < goal_contrib_sum:
        savings_actual_minor = max(savings_actual_minor, goal_contrib_sum)

    # 4. Applicable Monthly Budget & 50/30/20 Targets
    from app.services.persistent_budget_service import get_or_create_monthly_budget
    mb = get_or_create_monthly_budget(user_id, year, month)

    # Resolve applicable budget:
    # 1. Month-specific MonthlyBudget record
    # 2. User master persistent monthly_budget_minor_units
    # 3. Baseline monthly income if no budget yet set
    if mb and mb.budget_amount_minor_units > 0:
        applicable_budget_minor = mb.budget_amount_minor_units
    elif user.monthly_budget_minor_units and user.monthly_budget_minor_units > 0:
        applicable_budget_minor = user.monthly_budget_minor_units
    else:
        applicable_budget_minor = recognized_income_minor

    budget_base_minor = applicable_budget_minor if applicable_budget_minor > 0 else recognized_income_minor

    distribution = get_user_budget_distribution(user_id)
    needs_pct = distribution['needs']
    wants_pct = distribution['wants']
    savings_pct = distribution['savings']

    needs_target_minor = int((budget_base_minor * needs_pct) / 100.0)
    wants_target_minor = int((budget_base_minor * wants_pct) / 100.0)
    savings_target_minor = int((budget_base_minor * savings_pct) / 100.0)

    # 5. Variances & Gaps
    needs_variance_minor = needs_actual_minor - needs_target_minor
    wants_variance_minor = wants_actual_minor - wants_target_minor
    savings_gap_minor = max(0, savings_target_minor - savings_actual_minor)

    # Total recognized outflow (consumption + actual savings)
    total_outflow_minor = consumption_expenses_minor + savings_actual_minor
    monthly_surplus_minor = recognized_income_minor - total_outflow_minor
    budget_remaining_minor = max(0, budget_base_minor - total_outflow_minor)
    budget_variance_minor = total_outflow_minor - budget_base_minor

    # Remaining allocations
    needs_remaining_minor = max(0, needs_target_minor - needs_actual_minor)
    wants_remaining_minor = max(0, wants_target_minor - wants_actual_minor)

    # Percentages
    needs_actual_pct = (needs_actual_minor / budget_base_minor * 100.0) if budget_base_minor > 0 else 0.0
    wants_actual_pct = (wants_actual_minor / budget_base_minor * 100.0) if budget_base_minor > 0 else 0.0
    savings_rate = (savings_actual_minor / budget_base_minor * 100.0) if budget_base_minor > 0 else 0.0
    outflow_pct_of_budget = (total_outflow_minor / budget_base_minor * 100.0) if budget_base_minor > 0 else 0.0

    # Sorted Category Spending List
    category_breakdown = sorted(
        [v for v in category_spending_map.values() if v['total_minor'] > 0],
        key=lambda x: x['total_minor'],
        reverse=True
    )
    for c in category_breakdown:
        c['share_of_income_pct'] = round((c['total_minor'] / budget_base_minor * 100.0) if budget_base_minor > 0 else 0.0, 1)
        c['formatted_amount'] = format_money(c['total_minor'], user.currency)

    currency = user.currency

    return {
        'period': {'year': year, 'month': month, 'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()},
        'currency': currency,
        # Persistent Monthly Budget Allocation
        'budget': {
            'minor': budget_base_minor,
            'formatted': format_money(budget_base_minor, currency),
            'remaining_minor': budget_remaining_minor,
            'remaining_formatted': format_money(budget_remaining_minor, currency),
            'variance_minor': budget_variance_minor,
            'is_over_budget': budget_variance_minor > 0,
            'outflow_pct': round(outflow_pct_of_budget, 1),
            'is_manually_set': getattr(mb, 'is_manually_set', False) if mb else False,
            'confirmation_status': getattr(mb, 'confirmation_status', 'pending') if mb else 'pending',
            'source_month': getattr(mb, 'source_month', None) if mb else None
        },
        # Income
        'income': {
            'minor': recognized_income_minor,
            'formatted': format_money(recognized_income_minor, currency),
            'is_fallback_baseline': recorded_income_minor == 0 and recognized_income_minor > 0
        },
        # Expenses & Outflows
        'expenses': {
            'minor': consumption_expenses_minor,
            'formatted': format_money(consumption_expenses_minor, currency)
        },
        'total_outflow': {
            'minor': total_outflow_minor,
            'formatted': format_money(total_outflow_minor, currency)
        },
        # Surplus & Savings
        'surplus': {
            'minor': monthly_surplus_minor,
            'formatted': format_money(monthly_surplus_minor, currency),
            'is_positive': monthly_surplus_minor >= 0
        },
        'savings_rate': round(savings_rate, 1),
        'actual_savings': {
            'minor': savings_actual_minor,
            'formatted': format_money(savings_actual_minor, currency)
        },
        # 50/30/20 Breakdown
        'distribution_targets': {
            'needs_pct': needs_pct,
            'wants_pct': wants_pct,
            'savings_pct': savings_pct
        },
        'needs': {
            'target_minor': needs_target_minor,
            'actual_minor': needs_actual_minor,
            'remaining_minor': needs_remaining_minor,
            'variance_minor': needs_variance_minor,
            'target_pct': needs_pct,
            'actual_pct': round(needs_actual_pct, 1),
            'is_over_budget': needs_variance_minor > 0,
            'target_formatted': format_money(needs_target_minor, currency),
            'actual_formatted': format_money(needs_actual_minor, currency),
            'remaining_formatted': format_money(needs_remaining_minor, currency)
        },
        'wants': {
            'target_minor': wants_target_minor,
            'actual_minor': wants_actual_minor,
            'remaining_minor': wants_remaining_minor,
            'variance_minor': wants_variance_minor,
            'target_pct': wants_pct,
            'actual_pct': round(wants_actual_pct, 1),
            'is_over_budget': wants_variance_minor > 0,
            'target_formatted': format_money(wants_target_minor, currency),
            'actual_formatted': format_money(wants_actual_minor, currency),
            'remaining_formatted': format_money(wants_remaining_minor, currency)
        },
        'savings': {
            'target_minor': savings_target_minor,
            'actual_minor': savings_actual_minor,
            'gap_minor': savings_gap_minor,
            'target_pct': savings_pct,
            'actual_pct': round(savings_rate, 1),
            'is_met': savings_actual_minor >= savings_target_minor,
            'target_formatted': format_money(savings_target_minor, currency),
            'actual_formatted': format_money(savings_actual_minor, currency),
            'gap_formatted': format_money(savings_gap_minor, currency)
        },
        'category_breakdown': category_breakdown,
        'transaction_count': len(txns)
    }
