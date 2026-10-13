"""
Investment Scheme Comparison Service for MoneyLeak.

Compares multiple Indian financial schemes side-by-side using identical
capital amounts, durations, historical CAGRs, and projected future values.
"""
from typing import List, Dict, Any
from app.services.scheme_data import get_scheme_by_id
from app.services.investment_calculator import calculate_compound_growth
from app.services.historical_engine import calculate_what_if_investment
from app.services.money import format_money, to_minor_units


def compare_schemes(
    scheme_ids: List[str],
    amount: float = 50000.0,
    duration_years: int = 5,
    method: str = 'LUMPSUM',
    currency: str = 'INR'
) -> Dict[str, Any]:
    """
    Compare 2 to 4 investment schemes side by side under identical terms.
    """
    if not scheme_ids:
        return {'count': 0, 'schemes': [], 'parameters': {}, 'comparison_metrics': []}

    schemes_data: List[Dict[str, Any]] = []

    for sid in scheme_ids[:4]:  # Limit to 4 schemes side-by-side
        scheme = get_scheme_by_id(sid)
        if not scheme:
            continue

        # Projected future value calculation
        expected_rate = scheme.get('expected_annual_return', 10.0)
        future_calc = calculate_compound_growth(
            initial_amount=amount if method == 'LUMPSUM' else 0,
            periodic_contribution=amount if method == 'SIP' else 0,
            frequency='MONTHLY' if method == 'SIP' else 'YEARLY',
            annual_return_pct=expected_rate,
            duration_years=duration_years,
            currency=currency
        )

        # Historical what-if calculation (if invested duration_years ago)
        try:
            hist_calc = calculate_what_if_investment(
                scheme_id=sid,
                amount=amount,
                duration_years=duration_years,
                method=method,
                currency=currency
            )
            hist_summary = hist_calc['summary']
            historical_val_formatted = hist_summary['current_value_formatted']
            historical_cagr_pct = hist_summary['annualized_return_pct']
            historical_profit_formatted = hist_summary['profit_loss_formatted']
            hist_profit_loss = hist_summary['profit_loss']
            hist_total_ret_pct = hist_summary['total_return_pct']
        except Exception:
            historical_val_formatted = "N/A"
            historical_cagr_pct = expected_rate
            historical_profit_formatted = "N/A"
            hist_profit_loss = 0.0
            hist_total_ret_pct = 0.0

        cagrs = scheme.get('historical_cagr', {})
        fv_minor = future_calc['summary']['future_value_minor']
        fv_float = fv_minor / 100.0

        future_proj = {
            'invested_formatted': future_calc['summary']['total_invested_formatted'],
            'future_value_formatted': future_calc['summary']['future_value_formatted'],
            'estimated_returns_formatted': future_calc['summary']['estimated_returns_formatted'],
            'future_value_minor': fv_minor,
            'future_value': fv_float
        }

        historical_what_if = {
            'current_value_formatted': historical_val_formatted,
            'profit_loss_formatted': historical_profit_formatted,
            'profit_loss': hist_profit_loss,
            'total_return_pct': hist_total_ret_pct,
            'annualized_return_pct': historical_cagr_pct
        }

        schemes_data.append({
            'id': scheme['id'],
            'name': scheme['name'],
            'short_name': scheme.get('short_name', scheme['name']),
            'category': scheme['category'],
            'category_label': scheme.get('category_label', scheme['category']),
            'subcategory': scheme.get('subcategory', ''),
            'provider': scheme['provider'],
            'risk_level': scheme['risk_level'],
            'risk_rating': scheme.get('risk_rating', 3),
            'min_investment': scheme.get('min_investment', 500),
            'min_investment_formatted': scheme.get('min_investment_formatted', format_money(to_minor_units(scheme.get('min_investment', 500), currency), currency)),
            'lock_in_years': scheme.get('lock_in_years', 0),
            'lock_in': scheme.get('lock_in', f"{scheme.get('lock_in_years', 0)} Years"),
            'expense_ratio': scheme['expense_ratio'],
            'current_rate_or_nav': scheme.get('current_rate_or_nav', ''),
            'expected_annual_return': expected_rate,
            'assumed_cagr': expected_rate,
            'cagr_1y': cagrs.get('1y'),
            'cagr_3y': cagrs.get('3y'),
            'cagr_5y': cagrs.get('5y') or expected_rate,
            'cagr_10y': cagrs.get('10y'),
            'historical_cagr': cagrs,
            'tax_treatment': scheme['tax_treatment'],
            'tax_benefit': scheme.get('tax_benefit', 'None'),
            'liquidity': scheme['liquidity'],
            'pros': scheme.get('advantages', []),
            'cons': scheme.get('disadvantages', []),
            'future_projection': future_proj,
            'historical_what_if': historical_what_if,
            'comparison_projection': future_proj,
            'comparison_historical': {
                'value_formatted': historical_val_formatted,
                'cagr_pct': historical_cagr_pct,
                'profit_formatted': historical_profit_formatted
            }
        })

    return {
        'count': len(schemes_data),
        'amount_formatted': format_money(to_minor_units(amount, currency), currency),
        'duration_years': duration_years,
        'method': method,
        'parameters': {
            'amount': amount,
            'duration_years': duration_years,
            'method': method,
            'currency': currency
        },
        'schemes': schemes_data
    }

