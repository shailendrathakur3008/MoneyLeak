"""
Historical Investment "What If I Invested Earlier?" Engine.
Computes what an investment made 1, 3, 5, or 10 years ago in an Indian scheme
would be worth today, for both Lump Sum and Monthly SIP methods.
"""
from datetime import date
from typing import Dict, Any, List, Optional
from decimal import Decimal
from app.services.scheme_data import get_scheme_by_id
from app.services.money import format_money, to_minor_units


def calculate_what_if_investment(
    scheme_id: str,
    amount: float,
    duration_years: int = 5,
    method: str = 'LUMPSUM',  # 'LUMPSUM' or 'SIP'
    currency: str = 'INR'
) -> Dict[str, Any]:
    """
    Calculate what `amount` invested `duration_years` ago in `scheme_id` would be worth today.
    Uses verified historical CAGR performance of the specific Indian asset.
    """
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        raise ValueError(f"Scheme with ID '{scheme_id}' was not found.")

    duration_years = max(1, min(10, int(duration_years)))
    method = method.upper()

    # Determine historical CAGR for the chosen duration
    cagr_dict = scheme.get('historical_cagr', {})
    dur_key = f"{duration_years}y"

    if dur_key in cagr_dict:
        annual_rate = cagr_dict[dur_key] / 100.0
    elif '5y' in cagr_dict and duration_years >= 5:
        annual_rate = cagr_dict['5y'] / 100.0
    elif '3y' in cagr_dict and duration_years >= 3:
        annual_rate = cagr_dict['3y'] / 100.0
    elif '1y' in cagr_dict:
        annual_rate = cagr_dict['1y'] / 100.0
    else:
        annual_rate = scheme.get('expected_annual_return', 10.0) / 100.0

    timeline: List[Dict[str, Any]] = []

    if method == 'LUMPSUM':
        # Lump Sum compounding: V = P * (1 + r)^t
        total_invested = float(amount)
        current_val = total_invested * ((1.0 + annual_rate) ** duration_years)
        profit_loss = current_val - total_invested
        total_return_pct = (profit_loss / total_invested * 100.0) if total_invested > 0 else 0.0
        annualized_return = annual_rate * 100.0

        for yr in range(1, duration_years + 1):
            val_at_yr = total_invested * ((1.0 + annual_rate) ** yr)
            gain_at_yr = val_at_yr - total_invested
            timeline.append({
                'year': yr,
                'label': f"Year {yr}",
                'invested': round(total_invested, 2),
                'value': round(val_at_yr, 2),
                'profit': round(gain_at_yr, 2),
                'invested_minor': to_minor_units(total_invested, currency),
                'value_minor': to_minor_units(val_at_yr, currency),
                'gain_minor': to_minor_units(gain_at_yr, currency),
                'profit_minor': to_minor_units(gain_at_yr, currency),
                'invested_formatted': format_money(to_minor_units(total_invested, currency), currency),
                'value_formatted': format_money(to_minor_units(val_at_yr, currency), currency),
                'gain_formatted': format_money(to_minor_units(gain_at_yr, currency), currency),
                'profit_formatted': format_money(to_minor_units(gain_at_yr, currency), currency)
            })

    else:
        # Monthly SIP compounding
        # Periodic monthly rate = (1 + r)^(1/12) - 1
        monthly_rate = ((1.0 + annual_rate) ** (1.0 / 12.0)) - 1.0
        total_months = duration_years * 12
        total_invested = float(amount) * total_months

        running_val = 0.0
        running_invested = 0.0

        for yr in range(1, duration_years + 1):
            for _ in range(12):
                running_invested += float(amount)
                running_val = (running_val + float(amount)) * (1.0 + monthly_rate)

            gain_at_yr = running_val - running_invested
            timeline.append({
                'year': yr,
                'label': f"Year {yr}",
                'invested': round(running_invested, 2),
                'value': round(running_val, 2),
                'profit': round(gain_at_yr, 2),
                'invested_minor': to_minor_units(running_invested, currency),
                'value_minor': to_minor_units(running_val, currency),
                'gain_minor': to_minor_units(gain_at_yr, currency),
                'profit_minor': to_minor_units(gain_at_yr, currency),
                'invested_formatted': format_money(to_minor_units(running_invested, currency), currency),
                'value_formatted': format_money(to_minor_units(running_val, currency), currency),
                'gain_formatted': format_money(to_minor_units(gain_at_yr, currency), currency),
                'profit_formatted': format_money(to_minor_units(gain_at_yr, currency), currency)
            })

        current_val = running_val
        profit_loss = current_val - total_invested
        total_return_pct = (profit_loss / total_invested * 100.0) if total_invested > 0 else 0.0
        annualized_return = annual_rate * 100.0

    invested_minor = to_minor_units(total_invested, currency)
    current_val_minor = to_minor_units(current_val, currency)
    profit_loss_minor = to_minor_units(profit_loss, currency)

    cagrs = scheme.get('historical_cagr', {})
    is_pure_term = scheme['id'] in ['pure-term-insurance', 'hdfc-life-click-2-protect-term']

    return {
        'scheme': {
            'id': scheme['id'],
            'name': scheme['name'],
            'short_name': scheme.get('short_name', scheme['name']),
            'category': scheme['category'],
            'category_label': scheme.get('category_label', scheme['category']),
            'provider': scheme['provider'],
            'risk_level': scheme['risk_level'],
            'objective': scheme.get('objective', ''),
            'tax_treatment': scheme['tax_treatment'],
            'current_rate_or_nav': scheme.get('current_rate_or_nav', ''),
            'cagr_1y': cagrs.get('1y'),
            'cagr_3y': cagrs.get('3y'),
            'cagr_5y': cagrs.get('5y') or scheme.get('expected_annual_return'),
            'cagr_10y': cagrs.get('10y')
        },
        'inputs': {
            'amount': amount,
            'duration_years': duration_years,
            'method': method,
            'currency': currency,
            'historical_cagr_used': round(annual_rate * 100.0, 2)
        },
        'summary': {
            'original_investment': round(total_invested, 2),
            'current_value': round(current_val, 2),
            'profit_loss': round(profit_loss, 2),
            'invested_capital_minor': invested_minor,
            'current_value_minor': current_val_minor,
            'profit_loss_minor': profit_loss_minor,
            'total_return_pct': round(total_return_pct, 1),
            'annualized_return_pct': round(annualized_return, 2),
            'annualized_return_cagr': round(annualized_return, 2),
            'original_investment_formatted': format_money(invested_minor, currency),
            'invested_capital_formatted': format_money(invested_minor, currency),
            'current_value_formatted': format_money(current_val_minor, currency),
            'profit_loss_formatted': format_money(profit_loss_minor, currency),
            'is_profit': profit_loss >= 0,
            'note': 'Zero cash maturity value. Pure risk life cover only.' if is_pure_term else ''
        },
        'timeline': timeline,
        'tax_and_exit_notes': [
            f"Tax rule: {scheme['tax_treatment']}",
            f"Liquidity & lock-in: {scheme['liquidity']}",
            "Historical returns do not guarantee identical future compounding; actual NAVs fluctuate with macroeconomic cycles."
        ]
    }
