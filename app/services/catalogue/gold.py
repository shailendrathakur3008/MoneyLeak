"""
Expanded Gold Investment Catalogue across 4 Categories for MoneyLeak.
Covering Physical Gold (Bullion, Coins, Jewellery), Gold ETFs, Gold Mutual Funds,
and Sovereign Gold Bonds (SGBs) with verified terms and sovereign guarantee.
"""
from typing import Dict, Any, List

GOLD_CATALOGUE: List[Dict[str, Any]] = [   {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 7,850.00',
        'dataSource': 'India Bullion and Jewellers Association (IBJA) Spot Fixing',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 11.5% CAGR',
        'expenseRatio': '0.00% (Annual Custody / Locker extra)',
        'id': 'physical-gold-24k',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Tangible asset free from counterparty default, institutional bankruptcy, or cyber '
                                  'failure',
                                  'Recognized worldwide as an universal store of purchasing power and currency crisis '
                                  'hedge',
                                  'Direct ownership with freedom to hold in personal bank lockers or private vaults'],
        'investmentCategory': 'Physical Gold Bullion (99.9% Purity)',
        'investmentHorizon': '> 5 Years',
        'investmentLimitations': [   '3% Goods and Services Tax (GST) applies on purchase and is not recoverable upon '
                                     'retail resale',
                                     'Carries annual storage and security costs (bank locker rent or safe insurance)',
                                     'Generates no ongoing passive cash flow or dividend yield; returns are strictly '
                                     'capital appreciation'],
        'investmentPurpose': 'Tangible wealth preservation, emergency financial collateral, and multi-generational '
                             'store of value.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 7850.0,
        'name': 'Physical Gold 24K Bullion / Minted Bars',
        'returnPeriod': '5Y Historical Spot CAGR',
        'riskDescription': 'Investment-grade 99.9% pure 24-karat gold bullion bars, backed by London Bullion Market '
                           'Association (LBMA) accredited refineries or BIS Hallmarking.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'GOLD-24K-BAR',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 7,980.00',
        'dataSource': 'MMTC-PAMP / India Government Mint',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 11.5% CAGR',
        'expenseRatio': '2.0% - 4.0% (Minting Premium / Packaging)',
        'id': 'physical-gold-24k-coins',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Certified tamper-proof assay packaging guarantees 99.9% purity without melting '
                                  'tests',
                                  'Available in convenient fractional weights: 1g, 2g, 5g, 8g, and 10g',
                                  'High resale liquidity across all licensed jewellers and bullion dealers across '
                                  'India'],
        'investmentCategory': 'Physical Gold Coins (99.9% Purity)',
        'investmentHorizon': '> 5 Years',
        'investmentLimitations': [   'Minting and packaging premium of 2% to 5% above raw spot bullion prices',
                                     'Mandatory 3% GST added at the time of purchase',
                                     'Jewellers may deduct assay packaging fees during buyback if the blister pack is '
                                     'opened'],
        'investmentPurpose': 'Convenient fractional physical gold accumulation for auspicious occasions, gifts, and '
                             'emergency reserves.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 7980.0,
        'name': 'Physical Gold 24K Minted Assay Coins',
        'returnPeriod': '5Y Historical Spot CAGR',
        'riskDescription': 'Government-minted or accredited refinery 24-karat (999 fineness) gold coins sealed in '
                           'tamper-evident certicard assay packaging with certified serial numbers.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'GOLD-24K-COIN',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 8,250.00',
        'dataSource': 'Bureau of Indian Standards (BIS) / Retail Jewellers Benchmark',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '8.0% - 10.5% CAGR',
        'expenseRatio': '8.0% - 25.0% (Making Charges & Wastage)',
        'id': 'physical-gold-22k-jewellery',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Mandatory Bureau of Indian Standards (BIS) Hallmark with unique 6-digit HUID '
                                  'ensures 91.6% purity',
                                  'Dual utility: provides cultural, wedding, and aesthetic use while preserving '
                                  'underlying metal value',
                                  'Accepted as pledge collateral for immediate low-interest bank gold loans across all '
                                  'Indian lenders'],
        'investmentCategory': 'Physical Gold Jewellery (91.6% Purity)',
        'investmentHorizon': '> 7 Years',
        'investmentLimitations': [   'Substantial making charges and craftsmanship wastage (8% to 25%+) permanently '
                                     'lost upon resale',
                                     'Mandatory 3% GST on both gold value and making charges is irrecoverable',
                                     'Lower net investment efficiency compared to financial gold (ETFs/SGBs) due to '
                                     'melting and purity deductions'],
        'investmentPurpose': 'Dual-purpose cultural and lifestyle wear combined with intergenerational gold wealth '
                             'transfer.',
        'lastUpdated': 'October 2026',
        'liquidity': 'Moderate (Making charges & melting loss on resale)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 8250.0,
        'name': 'Physical Gold 22K Hallmark Jewellery',
        'returnPeriod': 'Long-Term Net Realized CAGR',
        'riskDescription': 'BIS 916 Hallmarked 22-karat traditional Indian gold jewellery, combining aesthetic '
                           'cultural utility with long-term family wealth storage.',
        'riskLevel': 'Medium',
        'riskScore': 5,
        'symbol': 'GOLD-22K-JEWEL',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 68.50',
        'dataSource': 'National Stock Exchange (NSE) / Nippon Life India AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 12.0% CAGR',
        'expenseRatio': '0.79%',
        'id': 'nippon-gold-bees-etf',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Backing: 100% backed by physical 99.5% pure gold bullion held in secure, '
                                  'independently audited bank vaults',
                                  'Extreme liquidity: highest daily trading volume among all Indian Gold ETFs on NSE '
                                  'and BSE',
                                  'Zero making charges, zero locker fees, zero risk of theft, and live intraday '
                                  'pricing'],
        'investmentCategory': 'Gold ETF (Exchange Traded Fund)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Requires an active Demat and Trading account with a SEBI-registered stockbroker',
                                     'Subject to an annual total expense ratio (0.79%) deducted continuously from fund '
                                     'NAV',
                                     'LTCG taxed at 12.5% for holdings over 12 months; STCG taxed at investor slab '
                                     'rate'],
        'investmentPurpose': 'High-liquidity exchange-traded electronic gold allocation for portfolio hedging and '
                             'tactical trading.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+1 Rolling Settlement on NSE/BSE)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 68.5,
        'name': 'Nippon India ETF Gold BeES',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'India’s oldest and most liquid Gold ETF, tracking the domestic spot price of 0.01 gram of '
                           '99.5% pure physical gold bullion with tight exchange bid-ask spreads.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'GOLDBEES',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 66.80',
        'dataSource': 'National Stock Exchange (NSE) / HDFC AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 12.0% CAGR',
        'expenseRatio': '0.54%',
        'id': 'hdfc-gold-etf',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Competitive low expense ratio (0.54%) minimizing long-term compounding friction',
                                  'Portfolio holds 99.5% pure physical gold bars stored in insured custodian vaults '
                                  'with regular AMFI audits',
                                  'Tradeable in single-unit increments (~0.01g gold) during regular stock market '
                                  'hours'],
        'investmentCategory': 'Gold ETF (Exchange Traded Fund)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Demands Demat account and brokerage transaction fees for execution',
                                     'Minor tracking difference between domestic spot gold prices and ETF NAV due to '
                                     'cash drag',
                                     'Gold generates zero income yields; return depends entirely on commodity market '
                                     'price movements'],
        'investmentPurpose': 'Low-cost exchange-traded gold accumulation backed by HDFC AMC’s institutional asset '
                             'management infrastructure.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+1 Rolling Settlement on NSE/BSE)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 66.8,
        'name': 'HDFC Gold ETF',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Institutional-grade Gold ETF managed by HDFC AMC, providing cost-effective exposure to '
                           'domestic physical gold prices with low tracking error.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'HDFCMFGETF',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 67.20',
        'dataSource': 'National Stock Exchange (NSE) / SBI Funds Management',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 12.0% CAGR',
        'expenseRatio': '0.52%',
        'id': 'sbi-gold-etf',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Backed by SBI AMC, India’s largest asset manager by assets under management',
                                  'Low expense ratio (0.52%) providing cost-efficient exposure to domestic spot '
                                  'bullion',
                                  'Eliminates purity verification worries, storage costs, and security risks of '
                                  'physical metal'],
        'investmentCategory': 'Gold ETF (Exchange Traded Fund)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Requires Demat account; buy/sell orders execute at prevailing market prices '
                                     'which may deviate slightly from NAV',
                                     'Taxation: LTCG @ 12.5% after 1 year; STCG taxed at income slab rates under '
                                     'Finance Act 2024',
                                     'Returns are market-linked without contractual guarantees'],
        'investmentPurpose': 'Safe, institutional-scale electronic gold investment backed by the sovereign-backed '
                             'parentage of State Bank of India.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+1 Rolling Settlement on NSE/BSE)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 67.2,
        'name': 'SBI Gold ETF',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Flagship gold exchange-traded fund from India’s largest public-sector asset manager, SBI '
                           'Funds Management, offering high security and low tracking error.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'SETFGOLD',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 67.10',
        'dataSource': 'National Stock Exchange (NSE) / ICICI Prudential AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 12.0% CAGR',
        'expenseRatio': '0.50%',
        'id': 'icici-pru-gold-etf',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Ultra-competitive expense ratio (0.50%) ensuring maximum retention of physical gold '
                                  'appreciation',
                                  'Robust market maker presence ensuring tight bid-ask spreads for retail and HNI '
                                  'investors on NSE',
                                  'Independent third-party vault audits published semi-annually ensuring total '
                                  'physical backing'],
        'investmentCategory': 'Gold ETF (Exchange Traded Fund)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Must be held in Demat form; stockbroker brokerage and exchange turnover charges '
                                     'apply on trades',
                                     'Subject to domestic gold price volatility driven by import tariffs and global '
                                     'macroeconomic factors',
                                     'No dividend or interest payments'],
        'investmentPurpose': 'Cost-efficient systematic portfolio diversifier protecting against equity market '
                             'selloffs and rupee depreciation.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+1 Rolling Settlement on NSE/BSE)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 67.1,
        'name': 'ICICI Prudential Gold ETF',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Highly efficient Gold ETF from ICICI Prudential AMC, featuring one of the lowest expense '
                           'ratios among major Indian fund houses and strong institutional liquidity.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'ICICIGOLD',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 66.90',
        'dataSource': 'National Stock Exchange (NSE) / Kotak Mahindra AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 12.0% CAGR',
        'expenseRatio': '0.55%',
        'id': 'kotak-gold-etf',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Longstanding 17+ year operational track record with reliable tracking efficiency',
                                  'Directly convertible into physical gold bars for qualified wholesale institutional '
                                  'basket sizes',
                                  'Complete insulation from making charges, adulteration, and theft risks'],
        'investmentCategory': 'Gold ETF (Exchange Traded Fund)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Requires Demat account; retail redemptions executed via secondary stock exchange '
                                     'trades',
                                     'Capital is market-linked; gold prices can undergo extended cyclical '
                                     'consolidation phases',
                                     'Capital gains tax applies as per prevailing mutual fund regulations'],
        'investmentPurpose': 'Time-tested electronic bullion proxy for conservative capital preservation and asset '
                             'allocation.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+1 Rolling Settlement on NSE/BSE)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 66.9,
        'name': 'Kotak Gold ETF',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Established gold exchange-traded fund by Kotak Mahindra AMC, tracking domestic spot '
                           'physical gold prices with proven operational consistency since 2007.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'KOTAKGOLD',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 67.40',
        'dataSource': 'National Stock Exchange (NSE) / UTI AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.5% - 12.0% CAGR',
        'expenseRatio': '0.53%',
        'id': 'uti-gold-etf',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Managed by UTI AMC, the pioneer of the Indian mutual fund industry',
                                  'Strict adherence to SEBI purity guidelines with 99.5% pure physical gold custodian '
                                  'vaults',
                                  'Convenient fractional trading on both NSE and BSE'],
        'investmentCategory': 'Gold ETF (Exchange Traded Fund)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Requires Demat and Trading account setup',
                                     'Subject to domestic gold price fluctuations influenced by customs duties and '
                                     'USD/INR exchange rates',
                                     'Does not produce recurring income'],
        'investmentPurpose': 'Long-term defensive asset allocation in institutional gold bullion.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+1 Rolling Settlement on NSE/BSE)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 67.4,
        'name': 'UTI Gold ETF',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'UTI Mutual Fund’s dedicated gold exchange-traded scheme, offering pristine physical '
                           'bullion custody and transparent exchange execution.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'GOLDSHARE',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 27.80',
        'dataSource': 'AMFI / Kotak Mahindra Mutual Fund',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.0% - 11.5% CAGR',
        'expenseRatio': '0.14% (Direct Plan)',
        'id': 'kotak-gold-fund',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Zero Demat account requirement: invest via regular mutual fund apps, Net Banking, '
                                  'or UPI auto-debit',
                                  'Ultra-flexible Systematic Investment Plan (SIP) starting from just Rs 100 per month',
                                  'Professional custody eliminates security, storage, locker charges, and hallmark '
                                  'verification concerns'],
        'investmentCategory': 'Gold Mutual Fund (Fund of Funds)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Dual expense structure: underlying ETF expense (0.55%) plus fund-of-funds direct '
                                     'expense (0.14%)',
                                     'Exit load of 1.00% if redeemed within 15 days of allotment',
                                     'Redemption takes T+2 business days to credit directly into investor’s bank '
                                     'account'],
        'investmentPurpose': 'Automated systematic monthly gold accumulation via bank auto-debit for weddings and '
                             'long-term portfolio diversification.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 100.0,
        'name': 'Kotak Gold Fund - Direct Plan - Growth',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Open-ended fund of funds investing directly into Kotak Gold ETF units, enabling '
                           'hassle-free automated monthly SIPs into gold without needing a Demat account.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'KOTAKGOLDFUND',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 24.30',
        'dataSource': 'AMFI / SBI Mutual Fund',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.0% - 11.5% CAGR',
        'expenseRatio': '0.15% (Direct Plan)',
        'id': 'sbi-gold-fund',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'No Demat account required; purchases and redemptions handled directly through the '
                                  'AMC',
                                  'Rupee-cost averaging: automatic monthly SIP mitigates market timing risk and price '
                                  'volatility',
                                  'Backed by the physical gold bullion holdings of SBI Gold ETF'],
        'investmentCategory': 'Gold Mutual Fund (Fund of Funds)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Dual expense ratio (FoF direct plan 0.15% + underlying ETF 0.52%)',
                                     'Exit load of 1.00% applies if redeemed within 15 days of investment',
                                     'Taxation aligns with specified debt/gold mutual funds under Finance Act 2024'],
        'investmentPurpose': 'Disciplined systematic rupee-cost averaging into gold for long-term family wealth and '
                             'inflation protection.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 500.0,
        'name': 'SBI Gold Fund - Direct Plan - Growth',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Open-ended scheme from SBI Mutual Fund investing primarily in units of SBI Gold ETF, '
                           'providing convenient paperless gold accumulation with daily AMFI NAVs.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'SBIGOLDFUND',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 25.10',
        'dataSource': 'AMFI / HDFC AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.0% - 11.5% CAGR',
        'expenseRatio': '0.16% (Direct Plan)',
        'id': 'hdfc-gold-fund',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Accessible entry point with monthly SIPs starting from just Rs 100',
                                  'Daily NAV transparency declared by AMFI every evening based on domestic spot '
                                  'bullion closing',
                                  'Completely paperless, eliminating physical jewelry making charges and storage '
                                  'worries'],
        'investmentCategory': 'Gold Mutual Fund (Fund of Funds)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Underlying ETF expense ratio plus FoF management fee applies',
                                     'Exit load of 1% if redeemed within 15 days of investment',
                                     'Subject to commodity price volatility and currency fluctuations'],
        'investmentPurpose': 'Cost-effective systematic gold accumulation with micro-SIPs starting at Rs 100.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 100.0,
        'name': 'HDFC Gold Fund - Direct Plan - Growth',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Fund of funds investing in HDFC Gold ETF, designed for investors seeking seamless digital '
                           'gold accumulation without exchange brokerage or Demat maintenance costs.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'HDFCGOLDFUND',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 26.50',
        'dataSource': 'AMFI / Nippon Life India AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.0% - 11.5% CAGR',
        'expenseRatio': '0.17% (Direct Plan)',
        'id': 'nippon-gold-savings-fund',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Channelizes capital into Nippon India ETF Gold BeES, India’s most liquid gold ETF',
                                  'Enables automated SIP and STP (Systematic Transfer Plan) features without Demat '
                                  'hassle',
                                  'Redemption proceeds credited straight into registered savings bank account via '
                                  'direct credit / NEFT'],
        'investmentCategory': 'Gold Mutual Fund (Fund of Funds)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   'Total cost includes FoF direct expense (0.17%) and underlying ETF expense '
                                     '(0.79%)',
                                     'Exit load of 1% for redemptions within 15 days of allotment',
                                     'Returns are market-linked without capital or return guarantee'],
        'investmentPurpose': 'Convenient systematic accumulation of units representing physical gold bullion held in '
                             'insured vaults.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 100.0,
        'name': 'Nippon India Gold Savings Fund - Direct Plan - Growth',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Mutual fund scheme investing in units of Nippon India ETF Gold BeES, combining the high '
                           'liquidity of India’s largest gold ETF with the convenience of mutual fund SIPs.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'NIPPGOLDSAV',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Moderate to High (Backed by physical audited bullion)',
        'creditRisk': 'Nil (Physical gold held in insured custodian vaults)',
        'currentPrice': 'Rs 26.20',
        'dataSource': 'AMFI / ICICI Prudential AMC',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '9.0% - 11.5% CAGR',
        'expenseRatio': '0.15% (Direct Plan)',
        'id': 'icici-pru-regular-gold-savings',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Demat-free mutual fund structure with automated bank SIPs from Rs 100',
                                  'Invests in ICICI Prudential Gold ETF with tight operational tracking and high vault '
                                  'safety',
                                  'Ideal vehicle for accumulating wedding or educational gold reserves over 5-10 year '
                                  'horizons'],
        'investmentCategory': 'Gold Mutual Fund (Fund of Funds)',
        'investmentHorizon': '3 - 5 Years',
        'investmentLimitations': [   '1.00% exit load if redeemed within 15 days',
                                     'Combined expense ratio includes FoF direct fee plus ETF management fee',
                                     'Subject to global gold price cycle and USD/INR exchange rate movements'],
        'investmentPurpose': 'Systematic hedging tool for long-term goal planning and wealth preservation.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 100.0,
        'name': 'ICICI Prudential Regular Gold Savings Fund - Direct Plan - Growth',
        'returnPeriod': '5Y Historical CAGR',
        'riskDescription': 'Open-ended fund of funds by ICICI Prudential AMC investing in ICICI Prudential Gold ETF '
                           'units, delivering disciplined electronic gold accumulation.',
        'riskLevel': 'Medium',
        'riskScore': 4,
        'symbol': 'ICICIGOLDSAV',
        'taxInformation': 'Budget 2024 revision: Physical gold, gold ETFs, and gold mutual funds qualify for LTCG @ '
                          '12.5% after 12 months; STCG taxed at income slab.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Sovereign Guarantee (100% GoI backed redemption value)',
        'creditRisk': 'Nil (Full sovereign GoI backing)',
        'currentPrice': 'Rs 7,650.00',
        'dataSource': 'Reserve Bank of India (RBI) / Government of India',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '12.0% - 14.5% Total Return (2.5% Coupon + Spot)',
        'expenseRatio': '0.00% (Zero Management Expense)',
        'id': 'sovereign-gold-bonds',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Sovereign Guarantee: 100% backed by the Government of India with zero credit or '
                                  'default risk',
                                  '2.50% p.a. fixed cash coupon paid semi-annually directly into investor’s bank '
                                  'account on initial issue price',
                                  '100% TAX-FREE Capital Gains: complete exemption from capital gains tax upon '
                                  'redemption at 8-year maturity',
                                  'Zero expense ratio, zero storage costs, and zero making charges or purity '
                                  'deductions'],
        'investmentCategory': 'Government Sovereign Gold Bond',
        'investmentHorizon': '5 - 8 Years',
        'investmentLimitations': [   'Fresh primary RBI tranches depend on Government issuance calendars; existing '
                                     'series trade on secondary markets',
                                     'Secondary market liquidity on NSE/BSE can exhibit bid-ask spreads or trade at '
                                     'modest premiums/discounts to spot',
                                     'Fixed 8-year maturity tenure with early official RBI redemption window open only '
                                     'from year 5'],
        'investmentPurpose': 'The gold standard of long-term gold investing: fixed sovereign cash coupons combined '
                             'with tax-free spot gold capital appreciation.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 7650.0,
        'name': 'Sovereign Gold Bonds (SGB Secondary Market Series)',
        'returnPeriod': 'RBI 8-Year Sovereign Maturity',
        'riskDescription': 'Government of India sovereign-guaranteed gold securities issued by the Reserve Bank of '
                           'India, paying 2.50% p.a. fixed interest and providing 100% tax-free capital gains on '
                           '8-year maturity.',
        'riskLevel': 'Low',
        'riskScore': 3,
        'symbol': 'SGB-SERIES',
        'taxInformation': "Semi-annual 2.50% p.a. interest coupon taxed at investor's slab rate. Capital gains on "
                          'maturity/redemption after 8 years are 100% EXEMPT from income tax.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Sovereign Guarantee (100% GoI backed redemption value)',
        'creditRisk': 'Nil (Full sovereign GoI backing)',
        'currentPrice': 'Rs 7,680.00',
        'dataSource': 'Reserve Bank of India (RBI) / NSE Secondary',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '12.0% - 14.5% Total Return',
        'expenseRatio': '0.00%',
        'id': 'sovereign-gold-bond-2028-series',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Definite maturity date (October 2028): ideal for planned medium-term financial '
                                  'goals',
                                  '2.50% annual interest credited semi-annually based on original nominal value (Rs '
                                  '5,051/g)',
                                  'Full tax exemption on capital gains if held until official RBI redemption in '
                                  'October 2028',
                                  'Full sovereign backing by the Government of India'],
        'investmentCategory': 'Government Sovereign Gold Bond',
        'investmentHorizon': '2 - 3 Years (Maturity Oct 2028)',
        'investmentLimitations': [   'Traded on the NSE/BSE secondary market; execution price depends on live seller '
                                     'asking quotes',
                                     'Requires Demat account for secondary market purchase and trading settlement',
                                     'Interest coupons are taxable at individual personal income slab rates'],
        'investmentPurpose': 'Medium-term sovereign gold holding with guaranteed semi-annual interest and tax-free '
                             'maturity in October 2028.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 7680.0,
        'name': 'Sovereign Gold Bond 2020-21 Series VI (Traded: SGB28OCT)',
        'returnPeriod': 'Maturity October 2028',
        'riskDescription': 'Existing secondary market Sovereign Gold Bond maturing in October 2028 (~2 years '
                           'remaining), paying 2.50% annual coupon and redeemed at official RBI IBJA benchmark rate.',
        'riskLevel': 'Low',
        'riskScore': 3,
        'symbol': 'SGB28OCT',
        'taxInformation': "Semi-annual 2.50% p.a. interest coupon taxed at investor's slab rate. Capital gains on "
                          'maturity/redemption after 8 years are 100% EXEMPT from income tax.'},
    {   'assetType': 'Gold',
        'capitalProtection': 'Sovereign Guarantee (100% GoI backed redemption value)',
        'creditRisk': 'Nil (Full sovereign GoI backing)',
        'currentPrice': 'Rs 7,620.00',
        'dataSource': 'Reserve Bank of India (RBI) / NSE Secondary',
        'disclaimer': 'Gold prices fluctuate based on international spot commodity prices, currency exchange rates, '
                      'and import tariffs.',
        'eligibilityRequirements': 'Resident individuals, HUFs, trusts, and institutions with KYC.',
        'expectedReturnRange': '12.0% - 14.5% Total Return',
        'expenseRatio': '0.00%',
        'id': 'sovereign-gold-bond-2032-series',
        'interestRateRisk': 'Low (Historically negative correlation with real bond yields)',
        'investmentBenefits': [   'Extended sovereign compounding until February 2032 with 100% tax-free capital '
                                  'redemption',
                                  'Semi-annual 2.50% annual coupon providing predictable cash flows throughout the '
                                  'tenure',
                                  'Eliminates all storage, insurance, locker, and assay costs associated with physical '
                                  'metal',
                                  'Backed by the sovereign balance sheet of the Republic of India'],
        'investmentCategory': 'Government Sovereign Gold Bond',
        'investmentHorizon': '> 5 Years (Maturity Feb 2032)',
        'investmentLimitations': [   'Long holding period: maturity in February 2032 (RBI early redemption window '
                                     'opens February 2029)',
                                     'Secondary exchange volumes fluctuate; larger lot orders may require limit '
                                     'pricing',
                                     'Underlying gold price fluctuates based on global spot market cycles'],
        'investmentPurpose': 'Long-term sovereign wealth compounding capturing 6+ years of tax-free gold appreciation '
                             'and cash coupons.',
        'lastUpdated': 'October 2026',
        'liquidity': 'High (T+2 via AMC)',
        'marketRisk': 'Moderate (International spot gold bullion and USD/INR exchange movements)',
        'minimumInvestment': 7620.0,
        'name': 'Sovereign Gold Bond 2023-24 Series IV (Traded: SGB32FEB)',
        'returnPeriod': 'Maturity February 2032',
        'riskDescription': 'Longer-dated Sovereign Gold Bond maturing in February 2032, issued under the 2023-24 '
                           'Series IV tranche with 2.50% p.a. interest coupon and sovereign redemption guarantee.',
        'riskLevel': 'Low',
        'riskScore': 3,
        'symbol': 'SGB32FEB',
        'taxInformation': "Semi-annual 2.50% p.a. interest coupon taxed at investor's slab rate. Capital gains on "
                          'maturity/redemption after 8 years are 100% EXEMPT from income tax.'}]

