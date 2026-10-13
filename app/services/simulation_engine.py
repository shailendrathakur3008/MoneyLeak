"""
Savings Simulator Engine for MoneyLeak.

Performs deterministic what-if analysis on baseline monthly figures.
Ensures simulated adjustments never mutate actual transaction records.
Prevents proposed reductions from creating negative category expenses.
"""
from typing import Dict, Any, List, Optional
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.services.budget_engine import calculate_budget_summary
from app.services.money import format_money


def run_simulation(
    user_id: int,
    reductions_by_category_minor: Dict[int, int],
    year: Optional[int] = None,
    month: Optional[int] = None
) -> Dict[str, Any]:
    """
    Simulate impact of proposed category-level expense trims against baseline.
    `reductions_by_category_minor` maps category_id to proposed reduction amount in minor units.
    """
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found")

    baseline = calculate_budget_summary(user_id, year, month)
    currency = user.currency

    # Build category comparison list
    total_proposed_reduction_minor = 0
    simulated_category_breakdown = []

    # Map baseline categories
    baseline_cat_map = {c['id']: c for c in baseline['category_breakdown']}

    for cat_item in baseline['category_breakdown']:
        cat_id = cat_item['id']
        orig_amount = cat_item['total_minor']
        # Requested reduction
        requested_trim = int(reductions_by_category_minor.get(cat_id, 0))
        # Prevent reductions greater than original spending (no negative spending)
        effective_trim = max(0, min(requested_trim, orig_amount))
        revised_amount = orig_amount - effective_trim

        total_proposed_reduction_minor += effective_trim

        simulated_category_breakdown.append({
            'id': cat_id,
            'name': cat_item['name'],
            'group': cat_item['group'],
            'original_minor': orig_amount,
            'reduction_minor': effective_trim,
            'revised_minor': revised_amount,
            'original_formatted': format_money(orig_amount, currency),
            'reduction_formatted': format_money(effective_trim, currency),
            'revised_formatted': format_money(revised_amount, currency)
        })

    # Calculations
    orig_income_minor = baseline['income']['minor']
    orig_expenses_minor = baseline['expenses']['minor']
    orig_surplus_minor = baseline['surplus']['minor']
    orig_savings_minor = baseline['actual_savings']['minor']

    revised_expenses_minor = max(0, orig_expenses_minor - total_proposed_reduction_minor)
    revised_surplus_minor = orig_surplus_minor + total_proposed_reduction_minor
    revised_potential_savings_minor = orig_savings_minor + total_proposed_reduction_minor

    annualized_additional_savings_minor = total_proposed_reduction_minor * 12

    # Revised savings rate if full surplus channeled to savings
    revised_savings_rate = (
        (revised_potential_savings_minor / orig_income_minor * 100.0)
        if orig_income_minor > 0 else 0.0
    )

    return {
        'currency': currency,
        'baseline': {
            'income_minor': orig_income_minor,
            'expenses_minor': orig_expenses_minor,
            'surplus_minor': orig_surplus_minor,
            'actual_savings_minor': orig_savings_minor,
            'savings_rate': baseline['savings_rate'],
            'income_formatted': format_money(orig_income_minor, currency),
            'expenses_formatted': format_money(orig_expenses_minor, currency),
            'surplus_formatted': format_money(orig_surplus_minor, currency),
            'savings_formatted': format_money(orig_savings_minor, currency)
        },
        'proposed': {
            'total_reduction_minor': total_proposed_reduction_minor,
            'revised_expenses_minor': revised_expenses_minor,
            'revised_surplus_minor': revised_surplus_minor,
            'annualized_savings_minor': annualized_additional_savings_minor,
            'revised_savings_rate': round(revised_savings_rate, 1),
            'total_reduction_formatted': format_money(total_proposed_reduction_minor, currency),
            'revised_expenses_formatted': format_money(revised_expenses_minor, currency),
            'revised_surplus_formatted': format_money(revised_surplus_minor, currency),
            'annualized_savings_formatted': format_money(annualized_additional_savings_minor, currency)
        },
        'categories': simulated_category_breakdown
    }
