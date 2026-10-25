"""
Curated Indian Financial Market Investment Schemes Database for MoneyLeak.

Comprehensive, validated catalogue covering Low, Medium, and High Risk instruments
across Stocks, Mutual Funds, ETFs, Fixed Deposits, Government Securities, Small Savings,
and Gold, in compliance with SEBI, AMFI, and RBI regulatory standards.
"""
import re
from typing import Dict, Any, List, Optional
from app.services.catalogue import (
    ALL_CATALOGUE_ITEMS,
    REQUIRED_SCHEMA_FIELDS,
    ASSET_TYPES,
    normalize_risk_level,
    score_to_risk_level
)

# -----------------------------------------------------------------------------
# INVESTMENT CATEGORIES & ASSET TYPES
# -----------------------------------------------------------------------------

SCHEME_CATEGORIES: Dict[str, Dict[str, Any]] = {
    'ALL': {
        'id': 'ALL',
        'name': 'All Investments',
        'icon': 'chart-no-axes-combined',
        'description': 'Complete supported catalogue across all asset classes and risk spectrums.',
        'regulator': 'SEBI / AMFI / RBI / GoI'
    },
    'STOCKS': {
        'id': 'STOCKS',
        'name': 'Stocks',
        'icon': 'chart-candlestick',
        'description': 'Direct equity shares listed on NSE/BSE across defensive, blue-chip, mid-cap, and emerging companies.',
        'regulator': 'SEBI / NSE / BSE'
    },
    'MUTUAL_FUNDS': {
        'id': 'MUTUAL_FUNDS',
        'name': 'Mutual Funds',
        'icon': 'chart-pie',
        'description': 'Professionally managed pooled schemes: Debt, Liquid, Index, Large-Cap, Flexi-Cap, Mid-Cap, Small-Cap, and Hybrid funds.',
        'regulator': 'SEBI / AMFI'
    },
    'ETFS': {
        'id': 'ETFS',
        'name': 'ETFs',
        'icon': 'layers',
        'description': 'Exchange Traded Funds tracking broad market indices, G-Secs, and specific sectors on NSE/BSE.',
        'regulator': 'SEBI / NSE / BSE'
    },
    'FIXED_DEPOSITS': {
        'id': 'FIXED_DEPOSITS',
        'name': 'Fixed Deposits',
        'icon': 'landmark',
        'description': 'Bank and post office term deposits with guaranteed contractual interest and DICGC statutory protection.',
        'regulator': 'RBI / DICGC'
    },
    'GOVT_SECURITIES': {
        'id': 'GOVT_SECURITIES',
        'name': 'Government Securities',
        'icon': 'shield-check',
        'description': 'Sovereign-backed Treasury Bills, Dated G-Secs, and RBI Retail Direct instruments with zero credit default risk.',
        'regulator': 'RBI / Government of India'
    },
    'SMALL_SAVINGS': {
        'id': 'SMALL_SAVINGS',
        'name': 'Small Savings Schemes',
        'icon': 'piggy-bank',
        'description': 'Government statutory savings: PPF, NSC, Post Office MIS, Sukanya Samriddhi (SSY), and Senior Citizens (SCSS).',
        'regulator': 'Ministry of Finance / India Post'
    },
    'GOLD': {
        'id': 'GOLD',
        'name': 'Gold',
        'icon': 'coins',
        'description': 'Strategic safe-haven hedge against inflation and currency depreciation via Gold ETFs and Gold Mutual Funds.',
        'regulator': 'SEBI / AMFI'
    },
    'OTHER': {
        'id': 'OTHER',
        'name': 'Other Supported Investments',
        'icon': 'briefcase',
        'description': 'Target-maturity debt funds, corporate bond funds, and diversified emerging market opportunities.',
        'regulator': 'SEBI / RBI'
    },
    # Backward compatibility aliases
    'STOCKS_EQUITY': {
        'id': 'STOCKS_EQUITY',
        'name': 'Stocks',
        'icon': 'chart-candlestick',
        'description': 'Direct equity shares listed on NSE/BSE.',
        'regulator': 'SEBI / NSE / BSE'
    },
    'EQUITY_MUTUAL_FUNDS': {
        'id': 'EQUITY_MUTUAL_FUNDS',
        'name': 'Mutual Funds',
        'icon': 'chart-pie',
        'description': 'SEBI/AMFI regulated mutual funds.',
        'regulator': 'SEBI / AMFI'
    },
    'SIP_INVESTMENTS': {
        'id': 'SIP_INVESTMENTS',
        'name': 'SIP Investments',
        'icon': 'calendar-clock',
        'description': 'Systematic regular investment planning in eligible mutual funds.',
        'regulator': 'SEBI / AMFI'
    }
}

SCHEMES_DATABASE: List[Dict[str, Any]] = ALL_CATALOGUE_ITEMS

SCHEME_ALIASES: Dict[str, str] = {
    'sip-uti-nifty-50': 'uti-nifty-50-index',
    'sip-parag-parikh-flexi-cap': 'parag-parikh-flexi-cap',
    'sip-sbi-bluechip': 'sbi-bluechip-fund',
    'sip-motilal-midcap': 'motilal-oswal-midcap',
    'sip-nippon-small-cap': 'nippon-india-small-cap',
    'sip-mirae-elss': 'mirae-asset-elss-tax-saver',
    'sbi-nifty-50-index': 'uti-nifty-50-index',
    'nippon-nifty-bees': 'nippon-nifty-50-bees-etf',
    'gold-bees': 'nippon-gold-bees-etf',
    'zomato': 'zomato-eternal-limited',
    'paytm': 'one97-paytm',
    'nykaa': 'fsn-ecommerce-nykaa',
    'policybazaar': 'pb-fintech-policybazaar',
    'eternal': 'zomato-eternal-limited'
}

# -----------------------------------------------------------------------------
# ENRICHMENT & METADATA HARMONIZATION
# -----------------------------------------------------------------------------

def _extract_numeric_return(return_str: str) -> float:
    """Extract a representative annual percentage rate from return range text."""
    if not return_str:
        return 8.0
    matches = re.findall(r'([0-9]+\.?[0-9]*)%', return_str)
    if not matches:
        return 8.0
    floats = [float(m) for m in matches]
    return round(sum(floats) / len(floats), 2)


def _enrich_scheme(s: Dict[str, Any]) -> Dict[str, Any]:
    """
    Augment raw catalogue item with both camelCase (27-field schema)
    and legacy snake_case attributes for complete backward compatibility.
    """
    item = dict(s)
    
    # 1. Base identity & naming
    item['ticker'] = item.get('symbol', '')
    item['provider'] = item.get('dataSource', 'Official Indian Financial Exchange / Authority')
    item['company_name'] = item.get('name', '').split('(')[0].strip()

    # 2. Risk fields
    risk_level = item.get('riskLevel') or 'Medium'
    item['risk_level'] = risk_level
    score = item.get('riskScore', 5)
    item['risk_rating'] = min(5, max(1, round(score / 2.0)))
    item['risk_score'] = score

    # 3. Category & Asset Type mapping
    asset_type = item.get('assetType', 'Other Supported Investments')
    item['asset_type'] = asset_type
    
    # Map to internal category code
    if asset_type == 'Stocks':
        item['category'] = 'STOCKS_EQUITY'
        item['category_code'] = 'STOCKS'
    elif asset_type == 'Mutual Funds':
        item['category'] = 'EQUITY_MUTUAL_FUNDS'
        item['category_code'] = 'MUTUAL_FUNDS'
    elif asset_type == 'ETFs':
        item['category'] = 'ETFS'
        item['category_code'] = 'ETFS'
    elif asset_type == 'Fixed Deposits':
        item['category'] = 'FIXED_DEPOSITS'
        item['category_code'] = 'FIXED_DEPOSITS'
    elif asset_type == 'Government Securities':
        item['category'] = 'GOVT_SECURITIES'
        item['category_code'] = 'GOVT_SECURITIES'
    elif asset_type == 'Small Savings Schemes':
        item['category'] = 'SMALL_SAVINGS'
        item['category_code'] = 'SMALL_SAVINGS'
    elif asset_type == 'Gold':
        item['category'] = 'GOLD'
        item['category_code'] = 'GOLD'
    else:
        item['category'] = 'OTHER'
        item['category_code'] = 'OTHER'

    item['subcategory'] = item.get('investmentCategory', asset_type)
    item['category_label'] = asset_type

    # 4. Investment amounts & SIP
    min_inv = float(item.get('minimumInvestment', 500.0))
    item['min_investment'] = min_inv
    item['min_investment_inr'] = min_inv
    item['min_investment_formatted'] = f"₹{int(min_inv):,}" if min_inv.is_integer() else f"₹{min_inv:,.2f}"
    
    # Determine SIP eligibility
    supports_sip = (
        asset_type in ['Mutual Funds', 'Small Savings Schemes'] 
        or 'Recurring' in item.get('name', '') 
        or item.get('id') in ['public-provident-fund', 'sukanya-samriddhi-account', 'post-office-recurring-deposit']
    )
    item['supports_sip'] = supports_sip
    item['min_sip'] = min(min_inv, 500.0) if supports_sip else min_inv
    item['sip_availability'] = f"Available from ₹{int(item['min_sip']):,}/mo" if supports_sip else "Lump Sum / One-Time"

    # 5. Returns & Historical CAGR
    num_return = _extract_numeric_return(item.get('expectedReturnRange', ''))
    item['expected_annual_return'] = num_return
    item['current_interest_rate'] = num_return
    
    # Populate historical CAGR estimates for calculation models
    if 'historical_cagr' not in item or not item['historical_cagr']:
        item['historical_cagr'] = {
            '1y': round(num_return * 0.95, 2),
            '3y': round(num_return * 0.98, 2),
            '5y': round(num_return, 2),
            '10y': round(num_return * 1.02, 2)
        }
    cagrs = item['historical_cagr']
    item['cagr_1y'] = cagrs.get('1y', num_return)
    item['cagr_3y'] = cagrs.get('3y', num_return)
    item['cagr_5y'] = cagrs.get('5y', num_return)
    item['cagr_10y'] = cagrs.get('10y', num_return)

    # 6. Expense Ratio parsing
    raw_exp = str(item.get('expenseRatio', ''))
    item['expense_ratio'] = raw_exp
    exp_matches = re.findall(r'([0-9]+\.?[0-9]*)%', raw_exp)
    if exp_matches and 'Direct Equity' not in raw_exp:
        item['expense_ratio_pct'] = float(exp_matches[0])
    else:
        item['expense_ratio_pct'] = 0.0 if asset_type in ['Stocks', 'Fixed Deposits', 'Small Savings Schemes', 'Government Securities'] else None

    # 7. Price / NAV display
    curr_price = item.get('currentPrice') or item.get('currentNAV') or 'Market Determined'
    item['currentPrice'] = curr_price
    item['currentNAV'] = curr_price
    item['current_rate_or_nav'] = curr_price

    # 8. Supported durations normalization
    horizon = item.get('investmentHorizon', '3–5 Years')
    dur_list = []
    if '< 1 Year' in horizon:
        dur_list.extend(['UP_TO_1Y', '1_TO_3Y'])
    if '1–3 Years' in horizon or '1-3' in horizon:
        dur_list.extend(['1_TO_3Y', '3_TO_5Y'])
    if '3–5 Years' in horizon or '3-5' in horizon:
        dur_list.extend(['3_TO_5Y', '5_TO_10Y', 'MORE_THAN_5Y'])
    if '> 5 Years' in horizon or '5+' in horizon:
        dur_list.extend(['3_TO_5Y', '5_TO_10Y', 'MORE_THAN_10Y', 'MORE_THAN_5Y'])
    if not dur_list:
        dur_list = ['1_TO_3Y', '3_TO_5Y', '5_TO_10Y', 'MORE_THAN_5Y']
    item['supported_durations'] = list(dict.fromkeys(dur_list))

    # 9. Supported Goals
    goals = []
    if risk_level == 'Low':
        goals.append('Capital Preservation')
        if 'Monthly' in item.get('name', '') or 'SCSS' in item.get('id', '') or 'Dividend' in item.get('investmentCategory', ''):
            goals.append('Regular Income')
        if horizon == '< 1 Year':
            goals.append('Short-Term Savings')
        if 'PPF' in item.get('symbol', '') or 'SCSS' in item.get('symbol', '') or 'NSC' in item.get('symbol', ''):
            goals.append('Tax Planning')
            goals.append('Retirement Planning')
        if 'SSY' in item.get('symbol', '') or 'Sukanya' in item.get('name', ''):
            goals.append('Education Planning')
            goals.append('Tax Planning')
        if asset_type in ['Stocks', 'Mutual Funds', 'ETFs']:
            goals.append('Long-Term Wealth Creation')
    elif risk_level == 'Medium':
        goals.extend(['Long-Term Wealth Creation', 'Retirement Planning'])
        if 'Hybrid' in item.get('name', '') or 'Corporate Bond' in item.get('name', ''):
            goals.append('Regular Income')
        if 'Tax' in item.get('name', '') or 'ELSS' in item.get('name', ''):
            goals.append('Tax Planning')
        if asset_type == 'Gold':
            goals.append('Capital Preservation')
    else: # High Risk
        goals.extend(['Long-Term Wealth Creation', 'Retirement Planning'])
        if 'Tax' in item.get('name', ''):
            goals.append('Tax Planning')
    item['supported_goals'] = list(set(goals))

    # 10. Tags & Search Tokens
    tags = [
        risk_level.lower(),
        asset_type.lower(),
        item.get('investmentCategory', '').lower(),
        item.get('symbol', '').lower()
    ]
    tags.extend([g.lower().replace(' ', '-') for g in goals])
    item['tags'] = tags
    item['best_for_tags'] = tags

    # 11. Legacy compatibility aliases for templates & engine
    item['objective'] = item.get('investmentPurpose', '')
    item['advantages'] = item.get('investmentBenefits', [])
    item['disadvantages'] = item.get('investmentLimitations', [])
    item['tax_treatment'] = item.get('taxInformation', '')
    item['tax_benefit'] = 'Section 80C' if '80C' in item.get('taxInformation', '') else 'None'
    item['eligibility'] = item.get('eligibilityRequirements', '')
    item['data_source'] = item.get('dataSource', '')
    item['last_updated'] = item.get('lastUpdated', 'October 2026')
    item['how_it_works'] = item.get('riskDescription', '')

    # Lock-in parsing
    if '15-year' in item.get('liquidity', '') or 'PPF' in item.get('symbol', ''):
        item['lock_in_years'] = 15
    elif '3-year' in item.get('liquidity', '') or 'ELSS' in item.get('subcategory', ''):
        item['lock_in_years'] = 3
    elif '5-year' in item.get('liquidity', '') or 'NSC' in item.get('symbol', ''):
        item['lock_in_years'] = 5
    elif '21 years' in item.get('liquidity', '') or 'SSY' in item.get('symbol', ''):
        item['lock_in_years'] = 21
    else:
        item['lock_in_years'] = 0

    # Enrich with live or verified market data, official NAVs, and evidence-based risk
    try:
        from app.services.market_data_service import market_data_service
        item = market_data_service.enrich_scheme(item)
    except Exception as e:
        # Graceful fallback: maintain base schema
        item['freshness_status'] = 'CACHED'
        item['is_fallback'] = True

    return item


# -----------------------------------------------------------------------------
# RETRIEVAL API
# -----------------------------------------------------------------------------

def get_all_schemes() -> List[Dict[str, Any]]:
    """Return all investment instruments deduplicated and fully enriched."""
    seen_ids = set()
    deduped = []
    for s in SCHEMES_DATABASE:
        resolved = SCHEME_ALIASES.get(s['id'], s['id'])
        if resolved not in seen_ids:
            seen_ids.add(resolved)
            deduped.append(s)
    return [_enrich_scheme(s) for s in deduped]


def get_scheme_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an investment instrument by its unique identifier, legacy alias, official symbol, or AMFI code."""
    if not scheme_id:
        return None
    clean_id = str(scheme_id).strip()
    resolved_id = SCHEME_ALIASES.get(clean_id, clean_id)
    
    # Direct match on ID or symbol
    for s in SCHEMES_DATABASE:
        if s['id'] == resolved_id or s['id'] == clean_id or s.get('symbol') == clean_id:
            return _enrich_scheme(s)

    # Check verified instrument mappings (AMFI code or exchange symbol)
    try:
        from app.services.market_data_service import VERIFIED_INSTRUMENTS
        for vid, vmeta in VERIFIED_INSTRUMENTS.items():
            if (clean_id == vmeta.get('amfi_code') or 
                clean_id == vmeta.get('exchange_symbol') or 
                clean_id == vmeta.get('symbol')):
                for s in SCHEMES_DATABASE:
                    if s['id'] == vid:
                        return _enrich_scheme(s)
    except Exception:
        pass

    return None


def get_schemes_by_ids(scheme_ids: List[str]) -> List[Dict[str, Any]]:
    """Retrieve multiple schemes for side-by-side comparison."""
    results = []
    for sid in scheme_ids:
        s = get_scheme_by_id(sid)
        if s:
            results.append(s)
    return results


# -----------------------------------------------------------------------------
# FILTERING ENGINE
# -----------------------------------------------------------------------------

def filter_schemes(
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    duration: Optional[str] = None,
    min_investment: Optional[float] = None,
    max_expense_ratio: Optional[float] = None,
    tag: Optional[str] = None,
    query: Optional[str] = None,
    sort_by: Optional[str] = None,
    return_period: Optional[str] = None,
    max_min_investment: Optional[float] = None,
    goal: Optional[str] = None,
    asset_type: Optional[str] = None,
    amount: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Multi-criteria investment filtering with risk normalization,
    flexible asset matching, sorting, and sensible fallback suggestions.
    """
    all_schemes = get_all_schemes()
    results = list(all_schemes)

    # 1. Normalize Risk Level Filter
    normalized_risk = normalize_risk_level(risk_level)
    if normalized_risk != 'ALL':
        results = [
            s for s in results 
            if s.get('riskLevel') == normalized_risk 
            or score_to_risk_level(s.get('riskScore', 5)) == normalized_risk
        ]

    # 2. Asset Type / Category Filter
    active_type = asset_type or category
    if active_type and active_type.upper() not in ['ALL', 'ANY', '']:
        target_type = active_type.strip().upper()
        
        def matches_asset_type(s: Dict[str, Any]) -> bool:
            stype = s.get('assetType', '').upper()
            scat = s.get('category', '').upper()
            scode = s.get('category_code', '').upper()
            
            if target_type in ['STOCKS', 'STOCK', 'STOCKS_EQUITY', 'DIRECT_EQUITY']:
                return stype == 'STOCKS' or scat == 'STOCKS_EQUITY'
            if target_type in ['MUTUAL_FUNDS', 'MUTUAL FUNDS', 'EQUITY_MUTUAL_FUNDS', 'MF']:
                return stype == 'MUTUAL FUNDS' or scat == 'EQUITY_MUTUAL_FUNDS'
            if target_type in ['ETFS', 'ETF']:
                return stype == 'ETFS'
            if target_type in ['FIXED_DEPOSITS', 'FIXED DEPOSITS', 'FD']:
                return stype == 'FIXED DEPOSITS'
            if target_type in ['GOVT_SECURITIES', 'GOVERNMENT SECURITIES', 'G-SEC', 'GSEC']:
                return stype == 'GOVERNMENT SECURITIES'
            if target_type in ['SMALL_SAVINGS', 'SMALL SAVINGS SCHEMES', 'POST_OFFICE']:
                return stype == 'SMALL SAVINGS SCHEMES'
            if target_type in ['GOLD', 'GOLD_SILVER']:
                return stype == 'GOLD'
            if target_type in ['OTHER', 'OTHER_INVESTMENTS', 'CORPORATE_BONDS']:
                return stype in ['OTHER SUPPORTED INVESTMENTS', 'OTHER']
            if target_type in ['SIP', 'SIP_INVESTMENTS']:
                return s.get('supports_sip', False)
            
            return (
                target_type == stype.replace(' ', '_')
                or target_type in stype
                or target_type == scat
                or target_type == scode
            )

        results = [s for s in results if matches_asset_type(s)]

    # 3. Investment Duration Filter
    if duration and duration.upper() not in ['ALL', 'ANY', '']:
        dur_target = duration.strip().upper()
        dur_map = {
            'LESS THAN 1 YEAR': 'UP_TO_1Y',
            '< 1 YEAR': 'UP_TO_1Y',
            'UP_TO_1Y': 'UP_TO_1Y',
            '1–3 YEARS': '1_TO_3Y',
            '1-3 YEARS': '1_TO_3Y',
            '1_TO_3Y': '1_TO_3Y',
            '3–5 YEARS': '3_TO_5Y',
            '3-5 YEARS': '3_TO_5Y',
            '3_TO_5Y': '3_TO_5Y',
            'MORE THAN 5 YEARS': 'MORE_THAN_5Y',
            '> 5 YEARS': 'MORE_THAN_5Y',
            'MORE_THAN_5Y': 'MORE_THAN_5Y',
            '5_TO_10Y': '5_TO_10Y',
            'MORE_THAN_10Y': 'MORE_THAN_10Y'
        }
        mapped_dur = dur_map.get(dur_target, dur_target)
        results = [
            s for s in results
            if mapped_dur in s.get('supported_durations', [])
            or (mapped_dur == 'MORE_THAN_5Y' and any(d in ['MORE_THAN_5Y', '5_TO_10Y', 'MORE_THAN_10Y'] for d in s.get('supported_durations', [])))
        ]

    # 4. Investment Goal Filter
    if goal and goal.upper() not in ['ALL', 'ANY', '']:
        goal_target = goal.strip().lower()
        results = [
            s for s in results
            if any(goal_target in g.lower() for g in s.get('supported_goals', []))
            or any(goal_target in t.lower() for t in s.get('best_for_tags', []))
        ]

    # 5. Investment Amount Threshold
    inv_amount = amount if amount is not None else (min_investment if min_investment is not None else max_min_investment)
    if inv_amount is not None and float(inv_amount) > 0:
        threshold = float(inv_amount)
        results = [s for s in results if s.get('minimumInvestment', 0) <= threshold]

    # 6. Max Expense Ratio (Applicable to Mutual Funds & ETFs)
    if max_expense_ratio is not None and max_expense_ratio > 0:
        max_ter = float(max_expense_ratio)
        results = [
            s for s in results
            if s.get('expense_ratio_pct') is None
            or s.get('expense_ratio_pct') <= max_ter
        ]

    # 7. Search Query
    if query and query.strip():
        q = query.strip().lower()
        results = [
            s for s in results
            if q in s.get('name', '').lower()
            or q in s.get('symbol', '').lower()
            or q in s.get('ticker', '').lower()
            or q in s.get('company_name', '').lower()
            or q in s.get('provider', '').lower()
            or q in s.get('investmentCategory', '').lower()
            or q in s.get('assetType', '').lower()
            or any(q in t.lower() for t in s.get('tags', []))
        ]

    # 8. Tag Filter
    if tag and tag.upper() not in ['ALL', 'ANY', '']:
        raw_tag = tag.lower().strip()
        tag_variants = {raw_tag, raw_tag.replace('_', '-'), raw_tag.replace('-', '_')}
        results = [
            s for s in results
            if any(t.lower() in tag_variants for t in s.get('tags', []))
        ]

    # 9. Sensible Fallback if 0 Results Produced by Strict Filters
    # If the user selected a risk level and narrow filters returned 0 matches,
    # show alternatives matching that risk level so the user never gets a blank dead screen.
    is_fallback = False
    if not results and normalized_risk != 'ALL':
        fallback_candidates = [
            s for s in all_schemes
            if s.get('riskLevel') == normalized_risk
            or score_to_risk_level(s.get('riskScore', 5)) == normalized_risk
        ]
        # If there was a search query, prioritize query matches in fallback
        if query and query.strip():
            q = query.strip().lower()
            query_fallbacks = [
                s for s in fallback_candidates
                if q in s.get('name', '').lower() or q in s.get('symbol', '').lower()
            ]
            if query_fallbacks:
                fallback_candidates = query_fallbacks
        
        if fallback_candidates:
            results = fallback_candidates
            is_fallback = True
            for r in results:
                r['is_fallback'] = True

    # 10. Sorting
    period = (return_period or '5y').lower()
    cagr_key = f'cagr_{period}'

    if sort_by == 'name_asc':
        results.sort(key=lambda x: x.get('name', '').lower())
    elif sort_by == 'name_desc':
        results.sort(key=lambda x: x.get('name', '').lower(), reverse=True)
    elif sort_by == 'risk_asc':
        results.sort(key=lambda x: x.get('riskScore', 5))
    elif sort_by == 'risk_desc':
        results.sort(key=lambda x: x.get('riskScore', 5), reverse=True)
    elif sort_by == 'min_inv_asc':
        results.sort(key=lambda x: x.get('minimumInvestment', 0))
    elif sort_by == 'min_inv_desc':
        results.sort(key=lambda x: x.get('minimumInvestment', 0), reverse=True)
    elif sort_by == 'return_desc':
        results.sort(key=lambda x: (x.get(cagr_key) is not None, x.get(cagr_key) or 0.0), reverse=True)
    elif sort_by == 'expense_asc':
        results.sort(key=lambda x: (x.get('expense_ratio_pct') is None, x.get('expense_ratio_pct') if x.get('expense_ratio_pct') is not None else 999.0))
    elif sort_by == 'liquidity':
        results.sort(key=lambda x: 'Instant' in x.get('liquidity', '') or 'High' in x.get('liquidity', ''), reverse=True)
    else:
        # Default relevance: Low risk first if Low selected, etc.
        pass

    return results
