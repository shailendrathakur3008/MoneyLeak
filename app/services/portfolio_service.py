"""
Multi-Investment Portfolio Projection & Asset Allocation Engine for MoneyLeak.

Combines multiple eligible investments across the four approved categories:
1. Stocks & Equity
2. Equity Mutual Funds
3. SIP Investments (linked to Equity Mutual Funds as an investment method)
4. Gold

Calculates combined portfolio growth, year-by-year timeline, scenario analyses
(Conservative, Moderate, Optimistic), and asset allocation breakdown without
double-counting SIP investments.
"""
from typing import Dict, Any, List
from app.services.investment_calculator import calculate_compound_growth
from app.services.money import format_money, to_minor_units


def calculate_portfolio_projection(
    investments: List[Dict[str, Any]],
    duration_years: int = 10,
    currency: str = 'INR'
) -> Dict[str, Any]:
    """
    Compute aggregated multi-asset portfolio growth schedule and asset allocation.
    """
    if not investments:
        return {
            'total_invested': 0.0,
            'total_invested_formatted': format_money(0, currency),
            'future_value': 0.0,
            'future_value_formatted': format_money(0, currency),
            'estimated_returns': 0.0,
            'estimated_returns_formatted': format_money(0, currency),
            'gain_ratio_pct': 0.0,
            'investments_count': 0,
            'asset_allocation': {
                'STOCKS_EQUITY': {'label': 'Stocks & Equity', 'amount': 0.0, 'percentage': 0.0, 'formatted': format_money(0, currency)},
                'EQUITY_MUTUAL_FUNDS': {'label': 'Equity Mutual Funds', 'amount': 0.0, 'percentage': 0.0, 'formatted': format_money(0, currency)},
                'GOLD': {'label': 'Gold', 'amount': 0.0, 'percentage': 0.0, 'formatted': format_money(0, currency)}
            },
            'scenarios': {
                'conservative': {'future_value': 0.0, 'future_value_formatted': format_money(0, currency)},
                'moderate': {'future_value': 0.0, 'future_value_formatted': format_money(0, currency)},
                'optimistic': {'future_value': 0.0, 'future_value_formatted': format_money(0, currency)}
            },
            'schedule': [],
            'items': []
        }

    max_years = max(1, min(40, int(duration_years or 10)))

    items_calculated = []
    portfolio_total_invested = 0.0
    portfolio_fv_moderate = 0.0
    portfolio_fv_conservative = 0.0
    portfolio_fv_optimistic = 0.0

    # Asset exposure tracking (SIP maps cleanly to Equity Mutual Funds without double-counting)
    asset_exposure = {
        'STOCKS_EQUITY': 0.0,
        'EQUITY_MUTUAL_FUNDS': 0.0,
        'GOLD': 0.0
    }

    yearly_invested_totals = [0.0] * (max_years + 1)
    yearly_fv_totals_mod = [0.0] * (max_years + 1)
    yearly_fv_totals_cons = [0.0] * (max_years + 1)
    yearly_fv_totals_opt = [0.0] * (max_years + 1)

    for inv in investments:
        category = inv.get('category', 'EQUITY_MUTUAL_FUNDS')
        method = inv.get('method', 'LUMPSUM').upper()
        amount = float(inv.get('amount', 5000))
        rate_mod = float(inv.get('expected_return_pct', 12.0))
        rate_cons = max(1.0, rate_mod - 2.5)
        rate_opt = rate_mod + 2.5
        name = inv.get('name', 'Investment Item')
        inv_id = inv.get('id', '')
        underlying_id = inv.get('underlying_scheme_id')

        # Determine asset class: SIP is an investment method, linked directly to Equity Mutual Funds
        if category == 'SIP_INVESTMENTS' or method == 'SIP':
            effective_asset_class = 'EQUITY_MUTUAL_FUNDS'
        elif category in ['STOCKS_EQUITY', 'STOCKS']:
            effective_asset_class = 'STOCKS_EQUITY'
        elif category in ['GOLD', 'GOLD_ETFS']:
            effective_asset_class = 'GOLD'
        else:
            effective_asset_class = 'EQUITY_MUTUAL_FUNDS'

        # Compute growth across scenarios
        init_amt = amount if method == 'LUMPSUM' else 0.0
        period_amt = amount if method == 'SIP' else 0.0
        freq = 'MONTHLY' if method == 'SIP' else 'YEARLY'

        calc_mod = calculate_compound_growth(
            initial_amount=init_amt,
            periodic_contribution=period_amt,
            frequency=freq,
            annual_return_pct=rate_mod,
            duration_years=max_years,
            currency=currency
        )

        calc_cons = calculate_compound_growth(
            initial_amount=init_amt,
            periodic_contribution=period_amt,
            frequency=freq,
            annual_return_pct=rate_cons,
            duration_years=max_years,
            currency=currency
        )

        calc_opt = calculate_compound_growth(
            initial_amount=init_amt,
            periodic_contribution=period_amt,
            frequency=freq,
            annual_return_pct=rate_opt,
            duration_years=max_years,
            currency=currency
        )

        item_invested = calc_mod['summary']['total_invested']
        item_fv = calc_mod['summary']['future_value']
        portfolio_total_invested += item_invested
        portfolio_fv_moderate += item_fv
        portfolio_fv_conservative += calc_cons['summary']['future_value']
        portfolio_fv_optimistic += calc_opt['summary']['future_value']

        # Attribute to single effective asset class
        asset_exposure[effective_asset_class] += item_invested

        # Aggregate year-by-year schedule
        for idx, row in enumerate(calc_mod['schedule']):
            yr = row['year']
            inv_yr = row['invested_minor'] / 100.0
            fv_yr = row['future_value_minor'] / 100.0
            yearly_invested_totals[yr] += inv_yr
            yearly_fv_totals_mod[yr] += fv_yr

        for idx, row in enumerate(calc_cons['schedule']):
            yr = row['year']
            yearly_fv_totals_cons[yr] += (row['future_value_minor'] / 100.0)

        for idx, row in enumerate(calc_opt['schedule']):
            yr = row['year']
            yearly_fv_totals_opt[yr] += (row['future_value_minor'] / 100.0)

        items_calculated.append({
            'id': inv_id,
            'name': name,
            'category': category,
            'effective_asset_class': effective_asset_class,
            'underlying_scheme_id': underlying_id,
            'method': method,
            'amount': amount,
            'expected_return_pct': rate_mod,
            'total_invested': item_invested,
            'total_invested_formatted': format_money(to_minor_units(item_invested, currency), currency),
            'future_value': item_fv,
            'future_value_formatted': format_money(to_minor_units(item_fv, currency), currency),
            'returns': calc_mod['summary']['estimated_returns'],
            'returns_formatted': format_money(to_minor_units(calc_mod['summary']['estimated_returns'], currency), currency)
        })

    # Build year-by-year schedule
    combined_schedule = []
    for yr in range(1, max_years + 1):
        inv_cum = yearly_invested_totals[yr]
        fv_mod = yearly_fv_totals_mod[yr]
        ret_mod = max(0.0, fv_mod - inv_cum)
        fv_cons = yearly_fv_totals_cons[yr]
        fv_opt = yearly_fv_totals_opt[yr]

        combined_schedule.append({
            'year': yr,
            'invested': round(inv_cum, 2),
            'invested_formatted': format_money(to_minor_units(inv_cum, currency), currency),
            'future_value': round(fv_mod, 2),
            'future_value_formatted': format_money(to_minor_units(fv_mod, currency), currency),
            'returns': round(ret_mod, 2),
            'returns_formatted': format_money(to_minor_units(ret_mod, currency), currency),
            'conservative_fv': round(fv_cons, 2),
            'conservative_fv_formatted': format_money(to_minor_units(fv_cons, currency), currency),
            'optimistic_fv': round(fv_opt, 2),
            'optimistic_fv_formatted': format_money(to_minor_units(fv_opt, currency), currency)
        })

    # Asset allocation percentages
    allocation_result = {}
    labels = {
        'STOCKS_EQUITY': 'Stocks & Equity',
        'EQUITY_MUTUAL_FUNDS': 'Equity Mutual Funds',
        'GOLD': 'Gold'
    }

    for key in ['STOCKS_EQUITY', 'EQUITY_MUTUAL_FUNDS', 'GOLD']:
        amt = asset_exposure[key]
        pct = (amt / portfolio_total_invested * 100.0) if portfolio_total_invested > 0 else 0.0
        allocation_result[key] = {
            'label': labels[key],
            'amount': round(amt, 2),
            'percentage': round(pct, 1),
            'formatted': format_money(to_minor_units(amt, currency), currency)
        }

    total_gain = max(0.0, portfolio_fv_moderate - portfolio_total_invested)
    gain_ratio_pct = (total_gain / portfolio_total_invested * 100.0) if portfolio_total_invested > 0 else 0.0

    return {
        'total_invested': round(portfolio_total_invested, 2),
        'total_invested_formatted': format_money(to_minor_units(portfolio_total_invested, currency), currency),
        'future_value': round(portfolio_fv_moderate, 2),
        'future_value_formatted': format_money(to_minor_units(portfolio_fv_moderate, currency), currency),
        'estimated_returns': round(total_gain, 2),
        'estimated_returns_formatted': format_money(to_minor_units(total_gain, currency), currency),
        'gain_ratio_pct': round(gain_ratio_pct, 1),
        'investments_count': len(investments),
        'asset_allocation': allocation_result,
        'scenarios': {
            'conservative': {
                'future_value': round(portfolio_fv_conservative, 2),
                'future_value_formatted': format_money(to_minor_units(portfolio_fv_conservative, currency), currency),
                'gains': round(max(0.0, portfolio_fv_conservative - portfolio_total_invested), 2)
            },
            'moderate': {
                'future_value': round(portfolio_fv_moderate, 2),
                'future_value_formatted': format_money(to_minor_units(portfolio_fv_moderate, currency), currency),
                'gains': round(total_gain, 2)
            },
            'optimistic': {
                'future_value': round(portfolio_fv_optimistic, 2),
                'future_value_formatted': format_money(to_minor_units(portfolio_fv_optimistic, currency), currency),
                'gains': round(max(0.0, portfolio_fv_optimistic - portfolio_total_invested), 2)
            }
        },
        'schedule': combined_schedule,
        'items': items_calculated
    }
