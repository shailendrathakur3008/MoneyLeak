"""
Centralized Risk and Investment Instrument Schema for MoneyLeak.

Defines the 27 standard schema fields and normalization utilities
according to Indian financial markets and regulatory classifications.
"""
from typing import Dict, Any, List, Optional

REQUIRED_SCHEMA_FIELDS = [
    'id',
    'name',
    'symbol',
    'assetType',
    'investmentCategory',
    'riskLevel',
    'riskScore',
    'riskDescription',
    'investmentHorizon',
    'minimumInvestment',
    'expectedReturnRange',
    'returnPeriod',
    'liquidity',
    'capitalProtection',
    'marketRisk',
    'creditRisk',
    'interestRateRisk',
    'expenseRatio',
    'currentPrice',
    'lastUpdated',
    'dataSource',
    'investmentPurpose',
    'investmentBenefits',
    'investmentLimitations',
    'taxInformation',
    'eligibilityRequirements',
    'disclaimer'
]

ASSET_TYPES = [
    'Stocks',
    'Mutual Funds',
    'ETFs',
    'Fixed Deposits',
    'Government Securities',
    'Small Savings Schemes',
    'Gold',
    'Other Supported Investments'
]

def normalize_risk_level(raw_risk: Optional[str]) -> str:
    """Normalize any user/system risk input to standard 'Low', 'Medium', or 'High'."""
    if not raw_risk or raw_risk.strip().upper() in ['ALL', 'ANY', 'NONE', '']:
        return 'ALL'
    r = raw_risk.strip().lower()
    if r in ['low', 'conservative', 'very low', 'low risk']:
        return 'Low'
    if r in ['medium', 'moderate', 'balanced', 'medium risk']:
        return 'Medium'
    if r in ['high', 'very high', 'aggressive', 'high risk']:
        return 'High'
    return 'ALL'

def score_to_risk_level(score: int) -> str:
    """Map numeric risk score (1-10) to UI grouping."""
    if score <= 3:
        return 'Low'
    elif score <= 6:
        return 'Medium'
    else:
        return 'High'

def validate_catalogue_item(item: Dict[str, Any]) -> List[str]:
    """Validate that an investment catalogue entry contains all mandatory fields."""
    errors = []
    for f in REQUIRED_SCHEMA_FIELDS:
        if f not in item:
            # Allow currentNAV instead of currentPrice if applicable
            if f == 'currentPrice' and 'currentNAV' in item:
                continue
            errors.append(f"Missing field: {f}")
    if item.get('riskLevel') not in ['Low', 'Medium', 'High']:
        errors.append(f"Invalid riskLevel: {item.get('riskLevel')}")
    score = item.get('riskScore')
    if not isinstance(score, (int, float)) or not (1 <= score <= 10):
        errors.append(f"Invalid riskScore: {score}. Must be between 1 and 10.")
    return errors
