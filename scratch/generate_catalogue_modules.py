# -*- coding: utf-8 -*-
"""
Full Catalogue Generator for MoneyLeak
Creates:
- app/services/catalogue/stocks.py
- app/services/catalogue/mutual_funds.py
- app/services/catalogue/gold.py
"""
import os
import sys
import json

root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.services.catalogue.schema import validate_catalogue_item

def make_stock(
    item_id, name, symbol, category, risk_level, risk_score,
    price, horizon, return_range, return_period,
    desc, purpose, benefits, limitations, tax_info=None
):
    # Calibrate risk score to match risk level definition
    if risk_level == 'High' and risk_score < 7:
        risk_score = 7
    elif risk_level == 'Medium' and risk_score > 6:
        risk_score = 6
    elif risk_level == 'Medium' and risk_score < 4:
        risk_score = 4
    elif risk_level == 'Low' and risk_score > 3:
        risk_score = 3

    if tax_info is None:
        tax_info = "LTCG @ 12.5% on gains exceeding Rs 1.25 Lakh per financial year; STCG @ 20%. Dividends taxed at personal income slab."
    
    item = {
        'id': item_id,
        'name': name,
        'symbol': symbol,
        'assetType': 'Stocks',
        'investmentCategory': category,
        'riskLevel': risk_level,
        'riskScore': risk_score,
        'riskDescription': desc,
        'investmentHorizon': horizon,
        'minimumInvestment': float(price),
        'expectedReturnRange': return_range,
        'returnPeriod': return_period,
        'liquidity': 'High (T+1 Settlement on NSE/BSE)',
        'capitalProtection': 'Market-Linked (No Capital Guarantee)',
        'marketRisk': 'Moderate to High' if risk_score <= 5 else 'High (Equity volatility applies)',
        'creditRisk': 'Nil (Direct equity ownership)',
        'interestRateRisk': 'Low',
        'expenseRatio': '0.00% (Direct Shareholding)',
        'currentPrice': f"Rs {price:,.2f}",
        'lastUpdated': 'October 2026',
        'dataSource': 'National Stock Exchange (NSE) / Corporate Filings',
        'investmentPurpose': purpose,
        'investmentBenefits': benefits,
        'investmentLimitations': limitations,
        'taxInformation': tax_info,
        'eligibilityRequirements': 'Resident individuals, HUFs, NRIs with KYC Demat and Trading account.',
        'disclaimer': 'IMPORTANT: Direct equity investment carries market risk. Stock prices fluctuate and capital is not guaranteed.'
    }
    errs = validate_catalogue_item(item)
    if errs:
        raise ValueError(f"Stock {item_id} validation failed: {errs}")
    return item

def make_fund(
    item_id, name, symbol, category, risk_level, risk_score,
    nav, horizon, return_range, return_period,
    expense_ratio, min_invest,
    desc, purpose, benefits, limitations, amc, sebi_category, tax_info=None
):
    if tax_info is None:
        if 'ELSS' in category:
            tax_info = "Section 80C tax deduction up to Rs 1.5 Lakh. 3-year statutory lock-in. LTCG taxed @ 12.5% on gains exceeding Rs 1.25 Lakh."
        elif any(k in category for k in ['Debt', 'Overnight', 'Liquid', 'Money Market']):
            tax_info = "Specified debt mutual fund capital gains taxed at personal income slab rate without indexation."
        else:
            tax_info = "Equity fund taxation: LTCG @ 12.5% on gains exceeding Rs 1.25 Lakh per financial year; STCG @ 20%."

    liq = 'Moderate (3-Year Statutory Lock-in)' if 'ELSS' in category else (
        'Instant (T+0 instant withdrawal up to Rs 50k)' if any(k in category for k in ['Overnight', 'Liquid']) else 'High (T+2 Settlement via AMC)'
    )
    cap = 'High (Low duration & sovereign credit backing; no guarantee)' if any(k in category for k in ['Overnight', 'Liquid', 'Debt']) else 'Market-Linked (No Capital Guarantee)'
    mkt = 'Very Low' if risk_score <= 2 else ('Moderate' if risk_score <= 5 else 'High (Equity market fluctuations)')
    crd = 'Negligible (Central Sovereign / TREPS)' if any(k in category for k in ['Overnight', 'Liquid']) else ('Low (AAA/Sovereign corporate debt)' if 'Debt' in category else 'Nil (Diversified equity basket)')

    item = {
        'id': item_id,
        'name': name,
        'symbol': symbol,
        'assetType': 'Mutual Funds',
        'investmentCategory': category,
        'riskLevel': risk_level,
        'riskScore': risk_score,
        'riskDescription': desc,
        'investmentHorizon': horizon,
        'minimumInvestment': float(min_invest),
        'expectedReturnRange': return_range,
        'returnPeriod': return_period,
        'liquidity': liq,
        'capitalProtection': cap,
        'marketRisk': mkt,
        'creditRisk': crd,
        'interestRateRisk': 'Negligible' if any(k in category for k in ['Overnight', 'Liquid']) else ('Moderate (Duration sensitivity to RBI repo rate)' if 'Debt' in category else 'Low'),
        'expenseRatio': expense_ratio,
        'currentPrice': f"Rs {nav:,.4f} (NAV)",
        'lastUpdated': 'October 2026',
        'dataSource': f'AMFI / {amc}',
        'investmentPurpose': purpose,
        'investmentBenefits': benefits,
        'investmentLimitations': limitations,
        'taxInformation': tax_info,
        'eligibilityRequirements': 'Resident individuals, HUFs, NRIs, and institutions with KYC.',
        'disclaimer': 'Mutual Fund investments are subject to market risks, read all scheme related documents carefully.'
    }
    errs = validate_catalogue_item(item)
    if errs:
        raise ValueError(f"Fund {item_id} validation failed: {errs}")
    return item

def make_gold(
    item_id, name, symbol, category, risk_level, risk_score,
    price, horizon, return_range, return_period,
    expense_ratio, min_invest,
    desc, purpose, benefits, limitations, data_source, tax_info=None
):
    if tax_info is None:
        if 'Sovereign' in category:
            tax_info = "Semi-annual 2.50% p.a. interest coupon taxed at investor's slab rate. Capital gains on maturity/redemption after 8 years are 100% EXEMPT from income tax."
        else:
            tax_info = "Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ 12.5% after 12 months; STCG taxed at income slab."

    liq = 'Moderate (Making charges & melting loss on resale)' if 'Jewellery' in name else ('High (T+1 Rolling Settlement on NSE/BSE)' if 'ETF' in category else 'High (T+2 via AMC)')
    cap = 'Sovereign Guarantee (100% GoI backed redemption value)' if 'Sovereign' in category else 'Moderate to High (Backed by physical audited bullion)'

    item = {
        'id': item_id,
        'name': name,
        'symbol': symbol,
        'assetType': 'Gold',
        'investmentCategory': category,
        'riskLevel': risk_level,
        'riskScore': risk_score,
        'riskDescription': desc,
        'investmentHorizon': horizon,
        'minimumInvestment': float(min_invest),
        'expectedReturnRange': return_range,
        'returnPeriod': return_period,
        'liquidity': liq,
        'capitalProtection': cap,
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'creditRisk': 'Nil (Full sovereign GoI backing)' if 'Sovereign' in category else 'Nil (Physical gold held in insured custodian vaults)',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'expenseRatio': expense_ratio,
        'currentPrice': f"Rs {price:,.2f}" if price > 100 else f"Rs {price:.2f}",
        'lastUpdated': 'October 2026',
        'dataSource': data_source,
        'investmentPurpose': purpose,
        'investmentBenefits': benefits,
        'investmentLimitations': limitations,
        'taxInformation': tax_info,
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, and import tariffs.'
    }
    errs = validate_catalogue_item(item)
    if errs:
        raise ValueError(f"Gold {item_id} validation failed: {errs}")
    return item

print("Core generator helper configured.")
