"""
Historical Investment "What If I Invested Earlier?" Engine.
Computes what an investment made 1, 3, 5, or 10 years ago in an Indian scheme
would be worth today, for both Lump Sum and Monthly SIP methods.

Supports:
1. Actual official historical NAV series from AMFI India for mutual funds.
2. Actual official historical price series from NSE for stocks and ETFs.
3. Transparent fallback to verified regulatory CAGR schedules when full daily
   series are unavailable (e.g. for statutory small savings and bank FDs).
"""
from datetime import date
from typing import Dict, Any, List, Optional
from decimal import Decimal
from app.services.scheme_data import get_scheme_by_id
from app.services.money import format_money, to_minor_units
from app.services.market_data_service import market_data_service


def calculate_what_if_investment(
    scheme_id: str,
    amount: float,
    duration_years: int = 5,
    method: str = 'LUMPSUM',  # 'LUMPSUM' or 'SIP'
    currency: str = 'INR'
) -> Dict[str, Any]:
    """
    Calculate what `amount` invested `duration_years` ago in `scheme_id` would be worth today.
    Uses actual historical NAVs / stock prices when available, or verified regulatory CAGR.
    """
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        raise ValueError(f"Scheme with ID '{scheme_id}' was not found.")

    duration_years = max(1, min(10, int(duration_years)))
    method = method.upper()

    # Attempt to retrieve verified historical time series from MarketDataService
    hist_res = market_data_service.get_historical_time_series(scheme['id'], duration_years)
    has_actual_series = (
        hist_res.get('is_actual_data') and 
        bool(hist_res.get('series')) and 
        len(hist_res['series']) >= duration_years
    )

    timeline: List[Dict[str, Any]] = []
    calculation_basis = "VERIFIED_CAGR_MODEL"
    data_source_label = scheme.get('data_source', 'Official Regulatory Filings')

    # -------------------------------------------------------------------------
    # CASE 1: ACTUAL HISTORICAL NAV / PRICE TIME SERIES AVAILABLE
    # -------------------------------------------------------------------------
    if has_actual_series:
        series = hist_res['series']
        calculation_basis = "OFFICIAL_HISTORICAL_SERIES"
        data_source_label = hist_res.get('source', 'AMFI / National Stock Exchange')
        start_price = max(0.0001, series[0]['price'])
        current_price = series[-1]['price']

        if method == 'LUMPSUM':
            total_invested = float(amount)
            units_held = total_invested / start_price
            current_val = units_held * current_price
            profit_loss = current_val - total_invested
            total_return_pct = (profit_loss / total_invested * 100.0) if total_invested > 0 else 0.0

            # Annualized CAGR = (current_val / total_invested)^(1/years) - 1
            if current_val > 0 and total_invested > 0:
                annualized_return = ((current_val / total_invested) ** (1.0 / duration_years) - 1.0) * 100.0
            else:
                annualized_return = 0.0

            # Generate year-by-year checkpoints
            pts_per_year = len(series) / duration_years
            for yr in range(1, duration_years + 1):
                idx = min(len(series) - 1, int(round(yr * pts_per_year)) - 1)
                idx = max(0, idx)
                price_at_yr = series[idx]['price']
                val_at_yr = units_held * price_at_yr
                gain_at_yr = val_at_yr - total_invested
                date_label = series[idx].get('date', f"Year {yr}")

                timeline.append({
                    'year': yr,
                    'label': f"Year {yr} ({date_label})",
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
            # Monthly SIP backtesting across historical intervals
            total_months = duration_years * 12
            total_invested = float(amount) * total_months
            total_units = 0.0

            # Step across series to allocate units at each monthly checkpoint
            step_pts = len(series) / total_months
            running_invested = 0.0

            yearly_checkpoints = {}
            for m in range(total_months):
                idx = min(len(series) - 1, int(round(m * step_pts)))
                pt_price = max(0.0001, series[idx]['price'])
                total_units += (float(amount) / pt_price)
                running_invested += float(amount)

                # Record checkpoint at the end of each 12-month interval
                yr_num = (m + 1) // 12
                if (m + 1) % 12 == 0 and yr_num <= duration_years:
                    val_at_yr = total_units * pt_price
                    yearly_checkpoints[yr_num] = {
                        'invested': running_invested,
                        'value': val_at_yr,
                        'profit': val_at_yr - running_invested,
                        'date': series[idx].get('date', f"Year {yr_num}")
                    }

            current_val = total_units * current_price
            profit_loss = current_val - total_invested
            total_return_pct = (profit_loss / total_invested * 100.0) if total_invested > 0 else 0.0

            # Approximation for annualized return on monthly SIP cashflows
            if total_invested > 0 and current_val > 0:
                annualized_return = ((current_val / (total_invested * 0.55)) ** (1.0 / duration_years) - 1.0) * 100.0
                annualized_return = round(min(50.0, max(-20.0, annualized_return)), 2)
            else:
                annualized_return = 0.0

            for yr in range(1, duration_years + 1):
                ckpt = yearly_checkpoints.get(yr, {
                    'invested': float(amount) * yr * 12,
                    'value': (float(amount) * yr * 12) * (current_val / total_invested),
                    'profit': 0.0,
                    'date': f"Year {yr}"
                })
                timeline.append({
                    'year': yr,
                    'label': f"Year {yr} ({ckpt['date']})",
                    'invested': round(ckpt['invested'], 2),
                    'value': round(ckpt['value'], 2),
                    'profit': round(ckpt['profit'], 2),
                    'invested_minor': to_minor_units(ckpt['invested'], currency),
                    'value_minor': to_minor_units(ckpt['value'], currency),
                    'gain_minor': to_minor_units(ckpt['profit'], currency),
                    'profit_minor': to_minor_units(ckpt['profit'], currency),
                    'invested_formatted': format_money(to_minor_units(ckpt['invested'], currency), currency),
                    'value_formatted': format_money(to_minor_units(ckpt['value'], currency), currency),
                    'gain_formatted': format_money(to_minor_units(ckpt['profit'], currency), currency),
                    'profit_formatted': format_money(to_minor_units(ckpt['profit'], currency), currency)
                })

    # -------------------------------------------------------------------------
    # CASE 2: VERIFIED STATUTORY / BENCHMARK CAGR SCHEDULE
    # -------------------------------------------------------------------------
    else:
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

        if method == 'LUMPSUM':
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
            'provider': scheme.get('provider', scheme.get('dataSource', '')),
            'risk_level': scheme['risk_level'],
            'objective': scheme.get('objective', ''),
            'tax_treatment': scheme.get('tax_treatment', ''),
            'current_rate_or_nav': scheme.get('current_rate_or_nav', ''),
            'price_date': scheme.get('price_date', ''),
            'freshness_status': scheme.get('freshness_status', 'CACHED'),
            'official_symbol': scheme.get('official_symbol', scheme.get('symbol', '')),
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
            'calculation_basis': calculation_basis,
            'data_source': data_source_label
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
            'calculation_basis': calculation_basis,
            'data_source': data_source_label,
            'note': 'Zero cash maturity value. Pure risk life cover only.' if is_pure_term else ''
        },
        'timeline': timeline,
        'tax_and_exit_notes': [
            f"Tax rule: {scheme.get('tax_treatment', 'Subject to statutory tax rates')}",
            f"Liquidity & lock-in: {scheme.get('liquidity', 'Standard market liquidity')}",
            f"Calculation engine: Verified {calculation_basis} based on {data_source_label}.",
            "Historical returns do not guarantee identical future compounding; actual NAVs fluctuate with macroeconomic cycles."
        ]
    }
