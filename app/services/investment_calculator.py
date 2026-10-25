"""
Educational Investment Calculator for MoneyLeak.

Implements mathematically accurate compound growth projections.
Supports Lump-Sum, Periodic Monthly SIP, Annual Step-Up SIP, and
selectable Compounding Frequency (Annual, Semi-Annual, Quarterly, Monthly).
Discloses all assumptions, risk factors, and educational purpose.
"""
from typing import Dict, Any, List, Optional
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
    compounding_frequency: str = 'MONTHLY',  # 'ANNUALLY', 'SEMI_ANNUALLY', 'QUARTERLY', 'MONTHLY'
    scheme_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compute mathematically correct compound growth schedule and future value.
    Supports selectable compounding frequencies:
    - ANNUALLY (m=1)
    - SEMI_ANNUALLY (m=2)
    - QUARTERLY (m=4, standard for Indian bank FDs and post office schemes)
    - MONTHLY (m=12, standard for mutual fund SIPs)
    """
    duration_years = max(1, min(50, int(duration_years)))
    annual_rate = max(0.0, float(annual_return_pct)) / 100.0
    step_up_rate = max(0.0, float(step_up_pct)) / 100.0

    # Determine compounding periods per year (m)
    comp_freq_upper = (compounding_frequency or 'MONTHLY').upper()
    if comp_freq_upper in ['ANNUALLY', 'ANNUAL', 'YEARLY']:
        m = 1
    elif comp_freq_upper in ['SEMI_ANNUALLY', 'SEMI-ANNUAL', 'HALF_YEARLY']:
        m = 2
    elif comp_freq_upper in ['QUARTERLY', 'QUARTER']:
        m = 4
    else:
        m = 12  # Monthly default

    # Effective monthly rate rm such that (1 + rm)^12 == (1 + annual_rate / m)^m
    if annual_rate == 0.0:
        monthly_rate = 0.0
    else:
        monthly_rate = (1.0 + annual_rate / m) ** (m / 12.0) - 1.0

    is_monthly_deposit = (frequency.upper() != 'YEARLY')

    current_balance = float(initial_amount)
    total_invested = float(initial_amount)
    current_periodic_deposit = float(periodic_contribution)
    schedule: List[Dict[str, Any]] = []

    for yr in range(1, duration_years + 1):
        # Apply annual step-up to periodic deposit after year 1
        if yr > 1 and step_up_rate > 0:
            current_periodic_deposit *= (1.0 + step_up_rate)

        for mo in range(1, 13):
            # If monthly deposit: occurs every month. If yearly deposit: occurs in month 1 of each year.
            deposit = current_periodic_deposit if (is_monthly_deposit or mo == 1) else 0.0

            if timing.upper() == 'BEGINNING':
                current_balance += deposit
                total_invested += deposit
                current_balance *= (1.0 + monthly_rate)
            else:
                current_balance *= (1.0 + monthly_rate)
                current_balance += deposit
                total_invested += deposit

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
                'assetType': s.get('assetType'),
                'category': s.get('category'),
                'riskLevel': s.get('riskLevel'),
                'riskScore': s.get('riskScore'),
                'capitalProtection': s.get('capitalProtection'),
                'taxInformation': s.get('taxInformation')
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
            'compounding_frequency': comp_freq_upper,
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
            "Projections are purely educational and illustrative mathematical estimates; they do not guarantee future performance.",
            "Market-linked investments (stocks, mutual funds, gold) fluctuate with market conditions and returns can be negative in shorter durations.",
            "For instruments with fixed contractual interest rates (e.g., FDs, PPF, SCSS), returns follow the applicable statutory or bank rate.",
            "Capital gains taxes (e.g. LTCG @ 12.5% for equities, slab rate for debt/FDs) and inflation are not subtracted in this baseline model.",
            "Past performance of indices or asset classes is not indicative of future returns."
        ]
    }
