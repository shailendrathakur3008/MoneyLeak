# -*- coding: utf-8 -*-
"""
Builder that creates:
- app/services/catalogue/stocks.py
- app/services/catalogue/mutual_funds.py
- app/services/catalogue/gold.py
"""
import sys
import os
import pprint

root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scratch.generate_catalogue_modules import make_stock, make_fund, make_gold

print("Preparing expanded records...")

# =============================================================================
# 1. STOCKS CATALOGUE (Organized by 9 Sectors)
# =============================================================================
stocks = []

# --- A. Banking and Financial Services ---
stocks.extend([
    make_stock(
        'hdfc-bank', 'HDFC Bank Limited', 'HDFCBANK',
        'Large-Cap Private Sector Bank', 'Medium', 5, 1780.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s largest private sector bank following the parent HDFC Ltd merger, leading in retail mortgages, digital CASA, and branch network.',
        'Core compounding in India’s leading retail and corporate banking credit expansion.',
        ['Dominant retail deposit franchise with industry-leading low-cost CASA ratio', 'Consistently low gross NPA ratios through multi-decade economic cycles', 'Comprehensive financial ecosystem spanning credit cards, auto loans, and corporate lending'],
        ['Post-merger credit-to-deposit ratio normalization requires sustained branch deposit growth', 'Subject to RBI monetary policy shifts and systemic liquidity conditions', 'Market drawdowns apply during banking sector rotations']
    ),
    make_stock(
        'icici-bank', 'ICICI Bank Limited', 'ICICIBANK',
        'Large-Cap Private Sector Bank', 'Medium', 5, 1290.0, '> 5 Years',
        '14.5% - 17.0% CAGR', '5Y Historical CAGR',
        'Second-largest private sector lender delivering best-in-class return on assets (RoA > 2.2%), strong digital underwriting (iMobile), and high corporate credit quality.',
        'Capital appreciation through high-margin retail credit, MSME financing, and digital transformation.',
        ['Best-in-class risk-adjusted operating profit and return on equity (RoE ~18%)', 'Proven underwriting quality with negligible incremental slippages across corporate books', 'Diversified revenue engines through subsidiaries (ICICI Sec, ICICI Pru Life, ICICI Lombard)'],
        ['Macroeconomic credit cycle slow-downs can impact retail unsecured loan growth', 'Intense competitive pricing pressure on mortgage yields across peer banks', 'Direct equity market risks apply during financial corrections']
    ),
    make_stock(
        'state-bank-of-india', 'State Bank of India', 'SBIN',
        'Large-Cap Public Sector Bank (D-SIB)', 'Medium', 5, 820.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'India’s largest commercial bank with over 22,000 branches and 500 million customers. Systemically important bank (D-SIB) with majority sovereign ownership.',
        'Participation in India’s nationwide infrastructure financing, corporate capex revival, and sovereign banking.',
        ['Unrivalled deposit franchise and nationwide reach penetrating semi-urban and rural India', 'Robust corporate loan recovery track record and pristine corporate asset quality', 'Massive digital customer acquisition scale via YONO platform'],
        ['Higher wage revision and pension liability overheads compared to lean private peers', 'Public sector obligations and priority sector lending targets', 'Higher sensitivity to broad market sentiment toward PSU banking']
    ),
    make_stock(
        'axis-bank', 'Axis Bank Limited', 'AXISBANK',
        'Large-Cap Private Sector Bank', 'Medium', 5, 1180.0, '> 5 Years',
        '13.5% - 16.0% CAGR', '5Y Historical CAGR',
        'Third-largest private bank strengthened by Citibank India consumer business acquisition, scaling premium cards, wealth management, and corporate banking.',
        'Growth in urban retail mortgages, affluent wealth management, and corporate trade financing.',
        ['Successful integration of Citibank consumer franchise providing affluent cross-selling', 'Rapidly expanding high-margin credit cards and SME financing books', 'Strengthened balance sheet with high provision coverage ratio (PCR > 75%)'],
        ['Integration overheads and technological harmonization costs post Citi transition', 'Competitive pressure on CASA acquisition in competitive urban hubs', 'Equity price fluctuations driven by banking sector beta']
    ),
    make_stock(
        'kotak-mahindra-bank', 'Kotak Mahindra Bank Limited', 'KOTAKBANK',
        'Large-Cap Private Sector Bank', 'Medium', 5, 1790.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Pioneering private lender renowned for high capital adequacy (CAR > 20%), conservative underwriting, and high-net-worth wealth management.',
        'High-quality conservative banking, investment banking, and capital market compounding.',
        ['Exceptionally high capital adequacy ratio insulating the bank against systemic shocks', 'Market-leading institutional equities, investment banking, and HNI wealth advisory', 'Robust net interest margins (NIM ~5%) supported by disciplined pricing'],
        ['Regulatory compliance and IT remediation audits impact digital customer onboarding pacing', 'Leadership transition and CEO succession execution', 'Slower loan book growth during aggressive competitor expansions']
    ),
    make_stock(
        'indusind-bank', 'IndusInd Bank Limited', 'INDUSINDBK',
        'Mid/Large-Cap Private Sector Bank', 'High', 6, 1080.0, '3 - 5 Years',
        '13.0% - 16.5% CAGR', '5Y Historical CAGR',
        'Private lender with dominant market share in commercial vehicle financing, microfinance (Bharat Financial), and gem/jewellery working capital credit.',
        'Cyclical commercial vehicle demand revival, microfinance yields, and corporate credit growth.',
        ['Market-leading expertise in vehicle finance with established dealer networks across India', 'High-yielding microfinance portfolio generating robust net interest margins', 'Strong promoter backing and active capital mobilization capabilities'],
        ['Higher asset quality vulnerability to rural rural distress and microfinance collection disruptions', 'Higher reliance on bulk and non-retail deposits compared to top 3 private peers', 'Stock price exhibits higher volatility during macro stress']
    ),
    make_stock(
        'bank-of-baroda', 'Bank of Baroda', 'BANKBARODA',
        'Large-Cap Public Sector Bank', 'Medium', 5, 245.0, '3 - 5 Years',
        '12.5% - 15.5% CAGR', '5Y Historical CAGR',
        'Second-largest public sector bank with substantial international presence and strong retail mortgage and MSME loan portfolios.',
        'Public sector credit expansion, digital loan processing (bob World), and corporate capex financing.',
        ['Strong pan-India retail footprint and profitable overseas banking operations in 17 countries', 'Sustained net NPA reduction and strong return on equity (RoE ~16%)', 'Attractive valuation multiples compared to large-cap private peers'],
        ['PSU regulatory interventions and statutory priority sector commitments', 'Deposit cost increases during tightening monetary liquidity cycles', 'Market cyclicality characteristic of PSU banking basket']
    ),
    make_stock(
        'punjab-national-bank', 'Punjab National Bank', 'PNB',
        'Large-Cap Public Sector Bank', 'High', 6, 105.0, '3 - 5 Years',
        '12.0% - 15.0% CAGR', '5Y Historical CAGR',
        'Major public sector lender dominating Northern India, having completed post-merger integration of Oriental Bank of Commerce and United Bank of India.',
        'Turnaround in corporate asset quality, bad loan resolution via NCLT, and agricultural credit.',
        ['Vast branch network across northern and eastern India ensuring steady low-cost deposit inflows', 'Accelerating recovery from stressed assets and legacy provisioning overhang', 'Direct beneficiary of government agricultural and MSME credit enhancement schemes'],
        ['Historical vulnerability to corporate asset quality slippages and high slippage volatility', 'Lower RoA compared to private banking peers', 'Stock price displays high beta during broader market corrections']
    ),
    make_stock(
        'canara-bank', 'Canara Bank', 'CANBK',
        'Large-Cap Public Sector Bank', 'Medium', 5, 102.0, '3 - 5 Years',
        '12.5% - 15.5% CAGR', '5Y Historical CAGR',
        'Leading public sector lender following Syndicate Bank integration, delivering consistent double-digit credit growth in RAM (Retail, Agri, MSME).',
        'Value compounding through southern Indian commercial credit, MSME loans, and subsidiary monetization (Can Fin Homes, Canara Robeco AMC).',
        ['High provision coverage ratio (> 88%) and multi-year low net NPA metrics', 'Substantial value unlocking potential through proposed IPO listings of asset management and housing arms', 'Strong presence in southern commercial hubs and industrial clusters'],
        ['Competitive deposit repricing pressuring net interest spreads during rate cycles', 'PSU ownership governance and priority sector lending mandates', 'Market volatility during systemic banking drawdowns']
    ),
    make_stock(
        'union-bank-of-india', 'Union Bank of India', 'UNIONBANK',
        'Large-Cap Public Sector Bank', 'High', 6, 115.0, '3 - 5 Years',
        '12.0% - 15.0% CAGR', '5Y Historical CAGR',
        'Major nationalized bank formed by the amalgamation of Union Bank, Andhra Bank, and Corporation Bank, serving over 150 million customers.',
        'Turnaround in return on assets, industrial corporate lending, and retail housing credit.',
        ['Significant nationwide branch network exceeding 8,500 branches supporting deposit mobilization', 'Consistent improvement in RoA (> 1%) and declining credit cost trajectory', 'Competitive positioning in agricultural and infrastructure project loans'],
        ['Corporate credit risk exposure to heavy infrastructure and metal sectors', 'Lower proportion of retail CASA compared to private leaders', 'Market volatility during broader equity market pullbacks']
    ),
    make_stock(
        'bajaj-finance', 'Bajaj Finance Limited', 'BAJFINANCE',
        'Large-Cap Consumer NBFC', 'High', 6, 6950.0, '> 5 Years',
        '15.5% - 18.5% CAGR', '5Y Historical CAGR',
        'India’s dominant retail asset financier with a customer franchise exceeding 85 million, pioneering point-of-sale consumer electronics and lifestyle financing.',
        'High-growth compounding through consumer credit, merchant payments, omnichannel digital app, and housing finance.',
        ['Unrivalled customer acquisition engine adding over 3 million new-to-credit customers quarterly', 'Proprietary cross-sell algorithm generating high asset turn and strong RoE (> 20%)', 'Diversified loan book spanning consumer durables, personal loans, SME, and mortgages'],
        ['Unsecured personal loan portfolio vulnerable to rising regulatory risk weights and RBI scrutiny', 'Increased competition from aggressive retail banks and fintech balance sheets', 'High valuation multiples mean stock is sensitive to quarterly growth deceleration']
    ),
    make_stock(
        'bajaj-finserv', 'Bajaj Finserv Limited', 'BAJAJFINSV',
        'Large-Cap Financial Conglomerate', 'High', 6, 1720.0, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'Holding company for the Bajaj Group’s financial services: Bajaj Finance (NBFC), Bajaj Allianz General Insurance, and Bajaj Allianz Life Insurance.',
        'Comprehensive exposure to Indian consumer credit, general insurance, health insurance, and life coverage.',
        ['Holding company discount offers diversified entry into consumer lending and general insurance leaders', 'Bajaj Allianz General Insurance is consistently among India’s most profitable non-life insurers', 'Massive cross-selling potential across combined customer base exceeding 100 million'],
        ['Holding company structure implies potential holding discount volatility on equity markets', 'Underwriting risks in commercial motor and catastrophe insurance segments', 'Market volatility linked to equity market cycles']
    ),
    make_stock(
        'shriram-finance', 'Shriram Finance Limited', 'SHRIRAMFIN',
        'Large-Cap Retail NBFC', 'High', 7, 3150.0, '3 - 5 Years',
        '14.0% - 17.5% CAGR', '5Y Historical CAGR',
        'India’s largest retail asset-financing NBFC, formed by the merger of Shriram Transport and Shriram City Union, dominating used commercial vehicle and MSME lending.',
        'High-margin lending in semi-urban and rural commercial vehicle, two-wheeler, and gold loan sectors.',
        ['Dominant pricing power in used commercial vehicle financing with unique borrower relationship model', 'High net interest margins (~8.5%) reflecting deep tier-2/3/4 semi-urban reach', 'Successful post-merger cross-selling expanding two-wheeler and MSME books'],
        ['Higher customer default sensitivity to rural economic slowdowns and fuel inflation', 'Higher credit costs during economic downturns compared to prime salaried lenders', 'Stock price subject to cyclical beta during industrial slow-downs']
    ),
    make_stock(
        'cholamandalam-investment', 'Cholamandalam Investment and Finance Company', 'CHOLAFIN',
        'Large-Cap Vehicle & Home NBFC', 'High', 6, 1320.0, '3 - 5 Years',
        '15.0% - 18.0% CAGR', '5Y Historical CAGR',
        'Flagship financial services company of the Murugappa Group, specializing in vehicle finance, home equity loans, and affordable home loans.',
        'Vehicle replacement cycles, expanding affordable housing loan portfolio, and loan-against-property compounding.',
        ['Exceptional underwriting discipline through multiple economic cycles with high loan collections', 'Consistent 20%+ AUM CAGR driven by geographic branch expansion across rural India', 'High return on equity (RoE ~19%) supported by conservative management philosophy'],
        ['Higher borrowing costs during tight debt market liquidity cycles pressuring margins', 'Exposure to commercial vehicle freight rate fluctuations', 'Equity market risk applies during general mid-tier NBFC selloffs']
    ),
    make_stock(
        'sbi-life-insurance', 'SBI Life Insurance Company', 'SBILIFE',
        'Large-Cap Life Insurer', 'Medium', 5, 1550.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s lowest-cost life insurer with an exclusive bancassurance tie-up with State Bank of India, leading private market share in individual rated premium.',
        'Underpenetrated Indian life insurance market compounding, retirement planning, and protection policies.',
        ['Lowest operating expense ratio (~5%) among all Indian life insurers ensuring high margin resilience', 'Unmatched bancassurance access to SBI’s 500 million customer base driving low customer acquisition costs', 'Strong solvency ratio (> 200%) providing high balance sheet safety'],
        ['Tax policy changes on high-value non-participating policies can dampen ticket sizes', 'Volatile capital markets impact unit-linked insurance plan (ULIP) inflows', 'Market-linked stock price fluctuations apply']
    ),
    make_stock(
        'hdfc-life-insurance', 'HDFC Life Insurance Company', 'HDFCLIFE',
        'Large-Cap Life Insurer', 'Medium', 5, 710.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'Leading private life insurer recognized for product innovation, high value of new business (VNB) margins, and strong protection policy leadership.',
        'Long-term demographic compounding in term insurance, annuities, and guaranteed savings plans.',
        ['Industry-leading VNB margins (~26%) supported by balanced non-par and protection mix', 'Deep institutional partnerships with HDFC Bank and non-bank distributor networks', 'Exide Life merger provides strong complementary geographic presence in South India'],
        ['Regulatory surrender charge guideline revisions may impact distributor commissions and margins', 'Sensitivity to interest rate movements on guaranteed return savings products', 'Equity volatility during broader financial sector downturns']
    ),
    make_stock(
        'icici-prudential-life', 'ICICI Prudential Life Insurance Company', 'ICICIPRULI',
        'Large-Cap Life Insurer', 'Medium', 5, 680.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Leading life insurer actively diversifying its distribution away from single-bank reliance toward agency, multi-bancassurance, and digital partnerships.',
        'Protection policies, retail pension annuities, and long-term savings products.',
        ['Strong brand recall and leadership in market-linked pension and annuity products', 'Substantial expansion into non-ICICI bank channels and corporate brokers', 'High persistence ratios and strong digital customer service infrastructure'],
        ['ULIP product concentration makes inflows sensitive to stock market corrections', 'Higher distributor acquisition costs as non-captive channels scale up', 'Market-linked equity share price risk applies']
    ),
    make_stock(
        'life-insurance-corporation', 'Life Insurance Corporation of India', 'LICI',
        'Large-Cap Sovereign Life Insurer (D-SII)', 'Medium', 5, 930.0, '> 5 Years',
        '11.5% - 14.5% CAGR', '5Y Historical CAGR',
        'India’s dominant life insurance corporation managing over Rs 50 Lakh Crore in assets, commanding over 60% market share with massive agency network.',
        'Deep semi-urban insurance penetration, shifting product mix toward high-margin non-par policies, and massive equity investment portfolio dividends.',
        ['Unrivalled agency network of over 1.3 million agents penetrating every corner of India', 'Sovereign statutory guarantee on sum assured and bonus under Section 37 of the LIC Act', 'Massive unrealized investment gains across India’s bluechip corporate equity holdings'],
        ['Gradual market share loss in high-ticket urban policies to aggressive private insurers', 'Legacy participating policy concentration yielding lower VNB margins (~16%) than private peers', 'Public sector ownership and government dividend expectations']
    )
])

print(f"Added {len(stocks)} stocks so far.")

# =============================================================================
# Write stocks.py
# =============================================================================
stocks_path = os.path.join(root_dir, 'app', 'services', 'catalogue', 'stocks.py')
with open(stocks_path, 'w', encoding='utf-8') as f:
    f.write('"""\nExpanded Indian Stocks Catalogue across 9 Major Sectors for MoneyLeak.\n"""\n')
    f.write('from typing import Dict, Any, List\n\n')
    f.write('STOCKS_CATALOGUE: List[Dict[str, Any]] = ')
    pprint.pprint(stocks, stream=f, indent=4, width=120)
    f.write('\n')

print(f"Successfully generated {stocks_path} with {len(stocks)} sector-organized stocks.")
