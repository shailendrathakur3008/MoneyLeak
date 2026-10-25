"""
Personalized Investment Recommendation Engine for MoneyLeak.

Recommends vetted, verified Indian investments across four approved categories:
1. Stocks & Equity
2. Equity Mutual Funds
3. SIP Investments
4. Gold

Strictly excludes government savings (PPF, NSC), bonds, debt funds, fixed deposits,
real estate / REITs, retirement products (NPS), Sovereign Gold Bonds, and commodity derivatives.
"""
from typing import Dict, Any, List, Optional
from app.services.scheme_data import get_all_schemes, get_scheme_by_id


def get_personalized_recommendations(
    amount: float = 10000.0,
    frequency: str = 'MONTHLY',
    duration_years: int = 5,
    risk_tolerance: str = 'High',
    objective: str = 'wealth_accumulation',
    preferred_category: str = 'ALL',
    liquidity: str = 'HIGH'
) -> List[Dict[str, Any]]:
    """
    Generate transparent, objective investment recommendations matching the user's
    configured parameters, horizons, risk profile, and liquidity requirements.
    Never guarantees future returns or fabricates live market prices.
    """
    all_schemes = get_all_schemes()
    candidates = []

    freq_upper = (frequency or 'MONTHLY').upper()
    risk_upper = (risk_tolerance or 'HIGH').upper()
    obj_lower = (objective or 'wealth_accumulation').lower()
    cat_filter = (preferred_category or 'ALL').upper()
    dur_years = max(1, int(duration_years or 5))

    for s in all_schemes:
        cat = s['category']

        # Category filter if specified
        if cat_filter != 'ALL':
            if cat_filter == 'SIP' or cat_filter == 'SIP_INVESTMENTS':
                if cat != 'SIP_INVESTMENTS':
                    continue
            elif cat != cat_filter:
                continue

        # If user explicitly requested Monthly frequency and preferred SIP
        is_sip = (cat == 'SIP_INVESTMENTS' or s.get('subcategory', '').endswith('SIP'))
        if freq_upper == 'MONTHLY' and cat_filter == 'ALL':
            # Boost SIP options or equity mutual funds that support SIP
            pass

        # Liquidity check
        lock_in = s.get('lock_in_years', 0)
        if liquidity.upper() == 'HIGH' and lock_in > 0:
            # Skip locked-in products if user strictly demands high/instant liquidity
            if obj_lower != 'tax_saving':
                continue

        # Score matching
        score = 50.0
        reasons = []

        # 1. Objective alignment
        if obj_lower == 'tax_saving':
            if 'tax-saving' in s.get('best_for_tags', []) or 'ELSS' in s.get('subcategory', ''):
                score += 40.0
                reasons.append("Eligible for Section 80C statutory tax deduction with 3-year equity lock-in.")
            else:
                score -= 30.0

        elif obj_lower == 'inflation_hedge':
            if cat == 'GOLD':
                score += 45.0
                reasons.append("Strategic hedge against inflation and currency depreciation with zero storage overhead.")
            else:
                score += 5.0

        elif obj_lower == 'dividends':
            if 'dividend' in s.get('subcategory', '').lower() or 'dividend' in s.get('best_for_tags', []):
                score += 40.0
                reasons.append("Consistent cashflow generation via shareholder dividends and low beta stability.")
            elif cat == 'STOCKS_EQUITY':
                score += 15.0

        elif obj_lower == 'high_growth':
            if 'small-cap' in s.get('subcategory', '').lower() or 'growth' in s.get('subcategory', '').lower():
                score += 40.0
                reasons.append("High capital growth potential targeted at emerging market leaders.")
            elif s.get('risk_level') in ['High', 'Very High']:
                score += 20.0

        elif obj_lower == 'wealth_accumulation':
            if 'index' in s.get('subcategory', '').lower() or 'flexi-cap' in s.get('subcategory', '').lower() or 'bluechip' in s.get('subcategory', '').lower():
                score += 35.0
                reasons.append("Proven multi-cycle compounder suitable for disciplined long-term wealth building.")
            else:
                score += 15.0

        # 2. Risk tolerance alignment
        scheme_risk = s.get('risk_level', 'High').upper()
        if risk_upper in ['VERY HIGH', 'HIGH']:
            if scheme_risk in ['VERY HIGH', 'HIGH']:
                score += 20.0
                reasons.append(f"Aligned with {risk_tolerance.capitalize()} risk tolerance for maximum equity compounding.")
            elif scheme_risk in ['MODERATE', 'MEDIUM']:
                score += 10.0
        elif risk_upper in ['MODERATE', 'MEDIUM']:
            if scheme_risk in ['MODERATE', 'MEDIUM']:
                score += 25.0
                reasons.append("Balanced risk-return profile cushioning against severe drawdowns.")
            elif scheme_risk in ['HIGH', 'VERY HIGH']:
                score += 5.0
            elif scheme_risk == 'LOW':
                score += 15.0
        elif risk_upper == 'LOW':
            if scheme_risk == 'LOW':
                score += 35.0
                reasons.append("Sovereign or high-grade defensive profile aligned with conservative capital preservation.")
            elif cat == 'GOLD' or scheme_risk in ['MODERATE', 'MEDIUM']:
                score += 20.0
                reasons.append("Lower asset volatility suitable for conservative capital growth.")
            else:
                score -= 15.0

        # 3. Horizon suitability
        if dur_years >= 5:
            score += 15.0
            reasons.append(f"Optimal investment horizon of {dur_years} years allows compounding to smooth out short-term market cycles.")
        elif dur_years >= 3:
            score += 10.0
        else:
            if scheme_risk == 'VERY HIGH':
                score -= 10.0

        # 4. Expense Ratio / Fee efficiency
        exp_ratio = s.get('expense_ratio', '')
        if '0.0' in exp_ratio or '0.1' in exp_ratio or '0.2' in exp_ratio:
            score += 10.0
            reasons.append("Ultra-low expense ratio preserving long-term net compounding gains.")

        # 5. Method suitability
        if freq_upper == 'MONTHLY' and (cat == 'SIP_INVESTMENTS' or s.get('min_sip', 0) > 0):
            score += 15.0

        # Primary reason summary
        primary_reason = " ".join(reasons[:2]) if reasons else "Consistent historical track record across market cycles."

        item = dict(s)
        item['match_score'] = round(score, 1)
        item['recommendation_reason'] = primary_reason
        item['reasons_list'] = reasons
        candidates.append(item)

    # Sort descending by match score
    candidates.sort(key=lambda x: x['match_score'], reverse=True)
    return candidates[:8]
