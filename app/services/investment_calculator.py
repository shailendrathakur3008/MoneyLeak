"""
Educational Investment Calculator for MoneyLeak.

Implements mathematically accurate compound growth projections.
Supports Lump-Sum, Periodic SIP, and Step-Up SIP (annual contribution increase).
Discloses all assumptions, risk factors, and educational purpose.
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from app.services.money import format_money, to_minor_units
from app.services.scheme_data import get_scheme_by_id


def calculate_compound_growth(
    initial_amount: float,
    periodic_contribution: float,
    frequency: str = 'MONTHLY',  # 'MONTHLY' or 'YEARLY'
    annual_return_pct: float = 12.0,
    duration_years: int = 10,
    timing: str = 'BEGINNING',  # 'BEGINNING' (annuity due) or 'END' (ordinary annuity)
    currency: str = 'INR',
    step_up_pct: float = 0.0,   # Optional annual percentage increase in periodic contribution
    scheme_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compute mathematically correct compound growth schedule and future value.
    Supports optional Step-Up SIP where contribution increases annually by `step_up_pct`%.
    """
    duration_years = max(1, min(50, int(duration_years)))
    annual_rate = max(0.0, float(annual_return_pct)) / 100.0
    step_up_rate = max(0.0, float(step_up_pct)) / 100.0

    if frequency.upper() == 'YEARLY':
        periods_per_year = 1
    else:
        periods_per_year = 12  # Monthly default

    periodic_rate = annual_rate / periods_per_year

    current_balance = float(initial_amount)
    total_invested = float(initial_amount)
    current_periodic_deposit = float(periodic_contribution)
    schedule: List[Dict[str, Any]] = []

    # Yearly aggregation for charts
    for yr in range(1, duration_years + 1):
        # Apply step-up to periodic deposit after year 1
        if yr > 1 and step_up_rate > 0:
            current_periodic_deposit = current_periodic_deposit * (1.0 + step_up_rate)

        for _ in range(periods_per_year):
            if timing.upper() == 'BEGINNING':
                current_balance += current_periodic_deposit
                total_invested += current_periodic_deposit
                current_balance *= (1.0 + periodic_rate)
            else:
                current_balance *= (1.0 + periodic_rate)
                current_balance += current_periodic_deposit
                total_invested += current_periodic_deposit

        interest_earned = max(0.0, current_balance - total_invested)
        schedule.append({
            'year': yr,
            'periodic_deposit_year': round(current_periodic_deposit, 2),
            'invested_minor': to_minor_units(total_invested, currency),
            'returns_minor': to_minor_units(interest_earned, currency),
            'future_value_minor': to_minor_units(current_balance, currency),
            'invested_formatted': format_money(to_minor_units(total_invested, currency), currency),
            'returns_formatted': format_money(to_minor_units(interest_earned, currency), currency),
            'future_value_formatted': format_money(to_minor_units(current_balance, currency), currency)
        })

    final_fv_minor = to_minor_units(current_balance, currency)
    total_invested_minor = to_minor_units(total_invested, currency)
    wealth_gain_minor = max(0, final_fv_minor - total_invested_minor)
    total_gain_pct = (wealth_gain_minor / total_invested_minor * 100.0) if total_invested_minor > 0 else 0.0

    scheme_info = None
    if scheme_id:
        s = get_scheme_by_id(scheme_id)
        if s:
            scheme_info = {
                'id': s['id'],
                'name': s['name'],
                'category': s['category'],
                'risk_level': s['risk_level'],
                'tax_treatment': s['tax_treatment']
            }

    return {
        'inputs': {
            'initial_amount': initial_amount,
            'periodic_contribution': periodic_contribution,
            'frequency': frequency,
            'annual_return_pct': annual_return_pct,
            'duration_years': duration_years,
            'timing': timing,
            'currency': currency,
            'step_up_pct': step_up_pct,
            'scheme_id': scheme_id
        },
        'summary': {
            'total_invested': round(total_invested, 2),
            'estimated_returns': round(max(0.0, current_balance - total_invested), 2),
            'future_value': round(current_balance, 2),
            'total_invested_minor': total_invested_minor,
            'estimated_returns_minor': wealth_gain_minor,
            'future_value_minor': final_fv_minor,
            'total_gain_pct': round(total_gain_pct, 1),
            'gain_ratio_pct': round(total_gain_pct, 1),
            'total_invested_formatted': format_money(total_invested_minor, currency),
            'estimated_returns_formatted': format_money(wealth_gain_minor, currency),
            'future_value_formatted': format_money(final_fv_minor, currency),
        },
        'scheme': scheme_info,
        'schedule': schedule,
        'disclosures': [
            "Projections are purely educational and illustrative; they do not guarantee future performance.",
            "Market-linked returns fluctuate with market conditions and can be negative in shorter durations.",
            "Capital gains taxes (e.g. LTCG @ 12.5% for equities, slab rate for debt/FDs), inflation, and fund expense ratios are not subtracted in this baseline model.",
            "Past performance of indices or asset classes is not indicative of future returns."
        ]
    }
