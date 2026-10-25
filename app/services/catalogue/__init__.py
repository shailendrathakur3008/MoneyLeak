"""
Centralized Indian Investment Catalogue Package for MoneyLeak.

Combines verified instruments across Low, Medium, and High risk levels
with all 27 required metadata fields according to SEBI/AMFI/RBI standards.
"""
from typing import Dict, Any, List
from app.services.catalogue.schema import (
    REQUIRED_SCHEMA_FIELDS,
    ASSET_TYPES,
    normalize_risk_level,
    score_to_risk_level,
    validate_catalogue_item
)
from app.services.catalogue.low_risk import LOW_RISK_SCHEMES
from app.services.catalogue.medium_risk import MEDIUM_RISK_SCHEMES
from app.services.catalogue.high_risk import HIGH_RISK_SCHEMES
from app.services.catalogue.stocks import STOCKS_CATALOGUE
from app.services.catalogue.mutual_funds import MUTUAL_FUNDS_CATALOGUE
from app.services.catalogue.gold import GOLD_CATALOGUE

# Additional legacy schemes preserved for backwards compatibility with existing user tests & portfolios
LEGACY_PRESERVED_SCHEMES: List[Dict[str, Any]] = [
    {
        'id': 'reliance-industries',
        'name': 'Reliance Industries Limited (NSE: RELIANCE)',
        'symbol': 'RELIANCE',
        'assetType': 'Stocks',
        'investmentCategory': 'Large-Cap Conglomerate',
        'riskLevel': 'Medium',
        'riskScore': 5,
        'riskDescription': 'Conglomerate spanning telecom (Jio), retail, and energy with high cash flows and massive clean energy capex.',
        'investmentHorizon': '> 5 Years',
        'minimumInvestment': 2870.0,
        'expectedReturnRange': '13.0% – 16.0% CAGR',
        'returnPeriod': '5Y Historical CAGR',
        'liquidity': 'High (T+1 settlement on NSE/BSE)',
        'capitalProtection': 'Market-Linked (No Guarantee)',
        'marketRisk': 'Moderate (Subject to market drawdowns)',
        'creditRisk': 'Nil (Highest credit rating)',
        'interestRateRisk': 'Low',
        'expenseRatio': '0.00% (Direct Equity)',
        'currentPrice': '₹2,870.00',
        'lastUpdated': 'October 2026',
        'dataSource': 'National Stock Exchange (NSE) / Corporate Filings',
        'investmentPurpose': 'Direct equity ownership in India’s largest market-cap conglomerate spanning telecom, retail, and energy.',
        'investmentBenefits': [
            'Market leader across Indian telecom, 5G, and retail',
            'Robust operating cash flows',
            'Consistent multi-decade wealth compounder'
        ],
        'investmentLimitations': [
            'Single-company concentration risk',
            'Large ongoing capex cycles in new clean energy',
            'Market price fluctuations apply'
        ],
        'taxInformation': 'LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%. Dividends taxed at income slab.',
        'eligibilityRequirements': 'KYC-compliant Demat and Trading account holders.',
        'disclaimer': 'IMPORTANT: Direct equity investment subject to market risks. Capital is not guaranteed.'
    },
    {
        'id': 'sbi-bluechip-fund',
        'name': 'SBI Bluechip Fund',
        'symbol': 'SBIBLUE',
        'assetType': 'Mutual Funds',
        'investmentCategory': 'Large-Cap Mutual Fund',
        'riskLevel': 'Medium',
        'riskScore': 5,
        'riskDescription': 'Actively managed large-cap fund investing in established bluechip leaders with strong balance sheets and market share.',
        'investmentHorizon': '> 5 Years',
        'minimumInvestment': 500.0,
        'expectedReturnRange': '12.0% – 14.5% CAGR',
        'returnPeriod': '5Y Historical CAGR',
        'liquidity': 'High (T+2 Settlement)',
        'capitalProtection': 'Market-Linked (No Guarantee)',
        'marketRisk': 'Moderate',
        'creditRisk': 'Nil (Top-tier bluechip corporate holdings)',
        'interestRateRisk': 'Low',
        'expenseRatio': '0.84% (Direct Plan)',
        'currentPrice': '₹84.10 (NAV)',
        'lastUpdated': 'October 2026',
        'dataSource': 'AMFI / SBI Mutual Fund',
        'investmentPurpose': 'Core long-term equity growth through India’s largest fund house investing in top 100 bluechip companies.',
        'investmentBenefits': [
            'Disciplined active stock selection across high-quality large-cap businesses',
            'Robust risk management dampening drawdowns during market corrections',
            'Consistent performance across multi-year market cycles'
        ],
        'investmentLimitations': [
            'Higher expense ratio than passive index funds',
            'Underperformance risk relative to benchmark during rapid momentum shifts',
            'Equity volatility applies'
        ],
        'taxInformation': 'LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'eligibilityRequirements': 'All KYC-verified investors.',
        'disclaimer': 'Mutual fund investments are subject to market risks, read scheme related documents carefully.'
    },
    {
        'id': 'mirae-asset-elss-tax-saver',
        'name': 'Mirae Asset ELSS Tax Saver Fund',
        'symbol': 'MIRELSS',
        'assetType': 'Mutual Funds',
        'investmentCategory': 'ELSS Tax Saving Mutual Fund',
        'riskLevel': 'Medium',
        'riskScore': 6,
        'riskDescription': 'Equity Linked Savings Scheme providing dual benefit of Section 80C statutory tax deduction and long-term equity compounding with a 3-year lock-in.',
        'investmentHorizon': '3–5 Years',
        'minimumInvestment': 500.0,
        'expectedReturnRange': '13.5% – 17.0% CAGR',
        'returnPeriod': '5Y Historical CAGR',
        'liquidity': 'Moderate (Mandatory 3-year statutory lock-in)',
        'capitalProtection': 'Market-Linked (No Guarantee)',
        'marketRisk': 'Moderate to High (Full equity market participation)',
        'creditRisk': 'Nil (Diversified equity portfolio)',
        'interestRateRisk': 'Low',
        'expenseRatio': '0.59% (Direct Plan)',
        'currentPrice': '₹48.90 (NAV)',
        'lastUpdated': 'October 2026',
        'dataSource': 'AMFI / Mirae Asset AMC',
        'investmentPurpose': 'Saving income tax under Section 80C while building long-term equity wealth with the shortest lock-in (3 years) among all tax-saving instruments.',
        'investmentBenefits': [
            'Qualifies for statutory tax deduction up to ₹1.5 Lakh per financial year under Section 80C',
            'Shortest lock-in period (3 years) compared to PPF (15 years) or Tax-Saving FDs (5 years)',
            'Disciplined compounding without the temptation to withdraw during market dips'
        ],
        'investmentLimitations': [
            'Mandatory 3-year statutory lock-in: funds cannot be liquidated under any circumstances during lock-in',
            'Every SIP installment is locked in for 3 full years from the date of respective allotment',
            'Equity market risk: returns fluctuate with the stock market'
        ],
        'taxInformation': 'Contribution deductible up to ₹1.5 Lakh under Section 80C. Capital gains on redemption: LTCG @ 12.5% on gains exceeding ₹1.25 Lakh.',
        'eligibilityRequirements': 'Resident individuals and HUFs with KYC.',
        'disclaimer': 'ELSS schemes carry statutory 3-year lock-in and market risk. Capital is not guaranteed.'
    },
    {
        'id': 'kotak-gold-fund',
        'name': 'Kotak Gold Fund',
        'symbol': 'KOTAKGOLD',
        'assetType': 'Gold',
        'investmentCategory': 'Gold Mutual Fund (Fund of Funds)',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'riskDescription': 'Fund of Funds investing in Kotak Gold ETF units, reflecting domestic physical gold bullion values with daily NAV.',
        'investmentHorizon': '3–5 Years',
        'minimumInvestment': 100.0,
        'expectedReturnRange': '9.0% – 11.5% CAGR',
        'returnPeriod': '5Y Historical CAGR',
        'liquidity': 'High (T+2 redemption via AMC)',
        'capitalProtection': 'Moderate to High (Underlying physical gold bullion)',
        'marketRisk': 'Moderate (International gold price movements)',
        'creditRisk': 'Nil (Backed by physical gold in vaults)',
        'interestRateRisk': 'Low',
        'expenseRatio': '0.14% (Direct Plan)',
        'currentPrice': '₹27.80 (NAV)',
        'lastUpdated': 'October 2026',
        'dataSource': 'AMFI / Kotak Mahindra AMC',
        'investmentPurpose': 'Hassle-free automated systematic gold savings via mutual fund mechanism with transparent daily NAV.',
        'investmentBenefits': [
            'Zero Demat account requirement',
            'Flexible systematic SIP options from ₹100',
            'Effective inflation and portfolio shock-absorber'
        ],
        'investmentLimitations': [
            'Subject to commodity market fluctuations and currency movements',
            'LTCG taxed at 12.5% (>12 months)'
        ],
        'taxInformation': 'LTCG @ 12.5% (> 12 months); STCG @ slab rate.',
        'eligibilityRequirements': 'Resident individuals and HUFs (Demat not required).',
        'disclaimer': 'Subject to market risks. Gold prices fluctuate based on international spot markets and currency rates.'
    }
]

# Master consolidated catalogue combining all verified categories
_master_dict: Dict[str, Dict[str, Any]] = {}

# 1. Base expanded catalogues
for _item in STOCKS_CATALOGUE:
    _master_dict[_item['id']] = _item
for _item in MUTUAL_FUNDS_CATALOGUE:
    _master_dict[_item['id']] = _item
for _item in GOLD_CATALOGUE:
    _master_dict[_item['id']] = _item

# 2. Curated risk tier instruments (preserves calibrated risk scores, defensive stocks, debt, and tests)
for _item in LOW_RISK_SCHEMES:
    _master_dict[_item['id']] = _item
for _item in MEDIUM_RISK_SCHEMES:
    _master_dict[_item['id']] = _item
for _item in HIGH_RISK_SCHEMES:
    _master_dict[_item['id']] = _item
for _item in LEGACY_PRESERVED_SCHEMES:
    _master_dict[_item['id']] = _item

ALL_CATALOGUE_ITEMS: List[Dict[str, Any]] = list(_master_dict.values())

# Validate at import time
_all_validation_errors = []
for _item in ALL_CATALOGUE_ITEMS:
    _errs = validate_catalogue_item(_item)
    if _errs:
        _all_validation_errors.append(f"{_item.get('id')}: {', '.join(_errs)}")

if _all_validation_errors:
    import warnings
    warnings.warn(f"Validation warnings in investment catalogue: {_all_validation_errors}")
