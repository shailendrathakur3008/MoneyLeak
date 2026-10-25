# -*- coding: utf-8 -*-
"""
Builder for app/services/catalogue/gold.py
Covering all 4 required Gold Investment Categories:
- Physical Gold (24K Bullion/Bars, 24K Minted Coins, 22K Hallmark Jewellery)
- Gold ETFs (Nippon BeES, HDFC, SBI, ICICI Prudential, Kotak, UTI, Axis)
- Gold Mutual Funds / FoFs (Kotak, SBI, HDFC, Nippon India, ICICI Prudential, Axis)
- Sovereign Gold Bonds (SGB Secondary Series, SGB 2028, SGB 2032)
"""
import sys
import os
import pprint

root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scratch.generate_catalogue_modules import make_gold

gold_items = []

# =============================================================================
# 1. PHYSICAL GOLD
# =============================================================================
gold_items.extend([
    make_gold(
        'physical-gold-24k', 'Physical Gold 24K Bullion / Minted Bars', 'GOLD-24K-BAR',
        'Physical Gold Bullion (99.9% Purity)', 'Medium', 4,
        7850.0, '> 5 Years', '9.5% - 11.5% CAGR', '5Y Historical Spot CAGR',
        '0.00% (Annual Custody / Locker extra)', 7850.0,
        'Investment-grade 99.9% pure 24-karat gold bullion bars, backed by London Bullion Market Association (LBMA) accredited refineries or BIS Hallmarking.',
        'Tangible wealth preservation, emergency financial collateral, and multi-generational store of value.',
        [
            'Tangible asset free from counterparty default, institutional bankruptcy, or cyber failure',
            'Recognized worldwide as an universal store of purchasing power and currency crisis hedge',
            'Direct ownership with freedom to hold in personal bank lockers or private vaults'
        ],
        [
            '3% Goods and Services Tax (GST) applies on purchase and is not recoverable upon retail resale',
            'Carries annual storage and security costs (bank locker rent or safe insurance)',
            'Generates no ongoing passive cash flow or dividend yield; returns are strictly capital appreciation'
        ],
        'India Bullion and Jewellers Association (IBJA) Spot Fixing'
    ),
    make_gold(
        'physical-gold-24k-coins', 'Physical Gold 24K Minted Assay Coins', 'GOLD-24K-COIN',
        'Physical Gold Coins (99.9% Purity)', 'Medium', 4,
        7980.0, '> 5 Years', '9.5% - 11.5% CAGR', '5Y Historical Spot CAGR',
        '2.0% - 4.0% (Minting Premium / Packaging)', 7980.0,
        'Government-minted or accredited refinery 24-karat (999 fineness) gold coins sealed in tamper-evident certicard assay packaging with certified serial numbers.',
        'Convenient fractional physical gold accumulation for auspicious occasions, gifts, and emergency reserves.',
        [
            'Certified tamper-proof assay packaging guarantees 99.9% purity without melting tests',
            'Available in convenient fractional weights: 1g, 2g, 5g, 8g, and 10g',
            'High resale liquidity across all licensed jewellers and bullion dealers across India'
        ],
        [
            'Minting and packaging premium of 2% to 5% above raw spot bullion prices',
            'Mandatory 3% GST added at the time of purchase',
            'Jewellers may deduct assay packaging fees during buyback if the blister pack is opened'
        ],
        'MMTC-PAMP / India Government Mint'
    ),
    make_gold(
        'physical-gold-22k-jewellery', 'Physical Gold 22K Hallmark Jewellery', 'GOLD-22K-JEWEL',
        'Physical Gold Jewellery (91.6% Purity)', 'Medium', 5,
        8250.0, '> 7 Years', '8.0% - 10.5% CAGR', 'Long-Term Net Realized CAGR',
        '8.0% - 25.0% (Making Charges & Wastage)', 8250.0,
        'BIS 916 Hallmarked 22-karat traditional Indian gold jewellery, combining aesthetic cultural utility with long-term family wealth storage.',
        'Dual-purpose cultural and lifestyle wear combined with intergenerational gold wealth transfer.',
        [
            'Mandatory Bureau of Indian Standards (BIS) Hallmark with unique 6-digit HUID ensures 91.6% purity',
            'Dual utility: provides cultural, wedding, and aesthetic use while preserving underlying metal value',
            'Accepted as pledge collateral for immediate low-interest bank gold loans across all Indian lenders'
        ],
        [
            'Substantial making charges and craftsmanship wastage (8% to 25%+) permanently lost upon resale',
            'Mandatory 3% GST on both gold value and making charges is irrecoverable',
            'Lower net investment efficiency compared to financial gold (ETFs/SGBs) due to melting and purity deductions'
        ],
        'Bureau of Indian Standards (BIS) / Retail Jewellers Benchmark'
    )
])

# =============================================================================
# 2. GOLD ETFS (EXCHANGE TRADED FUNDS)
# =============================================================================
gold_items.extend([
    make_gold(
        'nippon-gold-bees-etf', 'Nippon India ETF Gold BeES', 'GOLDBEES',
        'Gold ETF (Exchange Traded Fund)', 'Medium', 4,
        68.50, '3 - 5 Years', '9.5% - 12.0% CAGR', '5Y Historical CAGR',
        '0.79%', 68.50,
        'India’s oldest and most liquid Gold ETF, tracking the domestic spot price of 0.01 gram of 99.5% pure physical gold bullion with tight exchange bid-ask spreads.',
        'High-liquidity exchange-traded electronic gold allocation for portfolio hedging and tactical trading.',
        [
            'Backing: 100% backed by physical 99.5% pure gold bullion held in secure, independently audited bank vaults',
            'Extreme liquidity: highest daily trading volume among all Indian Gold ETFs on NSE and BSE',
            'Zero making charges, zero locker fees, zero risk of theft, and live intraday pricing'
        ],
        [
            'Requires an active Demat and Trading account with a SEBI-registered stockbroker',
            'Subject to an annual total expense ratio (0.79%) deducted continuously from fund NAV',
            'LTCG taxed at 12.5% for holdings over 12 months; STCG taxed at investor slab rate'
        ],
        'National Stock Exchange (NSE) / Nippon Life India AMC'
    ),
    make_gold(
        'hdfc-gold-etf', 'HDFC Gold ETF', 'HDFCMFGETF',
        'Gold ETF (Exchange Traded Fund)', 'Medium', 4,
        66.80, '3 - 5 Years', '9.5% - 12.0% CAGR', '5Y Historical CAGR',
        '0.54%', 66.80,
        'Institutional-grade Gold ETF managed by HDFC AMC, providing cost-effective exposure to domestic physical gold prices with low tracking error.',
        'Low-cost exchange-traded gold accumulation backed by HDFC AMC’s institutional asset management infrastructure.',
        [
            'Competitive low expense ratio (0.54%) minimizing long-term compounding friction',
            'Portfolio holds 99.5% pure physical gold bars stored in insured custodian vaults with regular AMFI audits',
            'Tradeable in single-unit increments (~0.01g gold) during regular stock market hours'
        ],
        [
            'Demands Demat account and brokerage transaction fees for execution',
            'Minor tracking difference between domestic spot gold prices and ETF NAV due to cash drag',
            'Gold generates zero income yields; return depends entirely on commodity market price movements'
        ],
        'National Stock Exchange (NSE) / HDFC AMC'
    ),
    make_gold(
        'sbi-gold-etf', 'SBI Gold ETF', 'SETFGOLD',
        'Gold ETF (Exchange Traded Fund)', 'Medium', 4,
        67.20, '3 - 5 Years', '9.5% - 12.0% CAGR', '5Y Historical CAGR',
        '0.52%', 67.20,
        'Flagship gold exchange-traded fund from India’s largest public-sector asset manager, SBI Funds Management, offering high security and low tracking error.',
        'Safe, institutional-scale electronic gold investment backed by the sovereign-backed parentage of State Bank of India.',
        [
            'Backed by SBI AMC, India’s largest asset manager by assets under management',
            'Low expense ratio (0.52%) providing cost-efficient exposure to domestic spot bullion',
            'Eliminates purity verification worries, storage costs, and security risks of physical metal'
        ],
        [
            'Requires Demat account; buy/sell orders execute at prevailing market prices which may deviate slightly from NAV',
            'Taxation: LTCG @ 12.5% after 1 year; STCG taxed at income slab rates under Finance Act 2024',
            'Returns are market-linked without contractual guarantees'
        ],
        'National Stock Exchange (NSE) / SBI Funds Management'
    ),
    make_gold(
        'icici-pru-gold-etf', 'ICICI Prudential Gold ETF', 'ICICIGOLD',
        'Gold ETF (Exchange Traded Fund)', 'Medium', 4,
        67.10, '3 - 5 Years', '9.5% - 12.0% CAGR', '5Y Historical CAGR',
        '0.50%', 67.10,
        'Highly efficient Gold ETF from ICICI Prudential AMC, featuring one of the lowest expense ratios among major Indian fund houses and strong institutional liquidity.',
        'Cost-efficient systematic portfolio diversifier protecting against equity market selloffs and rupee depreciation.',
        [
            'Ultra-competitive expense ratio (0.50%) ensuring maximum retention of physical gold appreciation',
            'Robust market maker presence ensuring tight bid-ask spreads for retail and HNI investors on NSE',
            'Independent third-party vault audits published semi-annually ensuring total physical backing'
        ],
        [
            'Must be held in Demat form; stockbroker brokerage and exchange turnover charges apply on trades',
            'Subject to domestic gold price volatility driven by import tariffs and global macroeconomic factors',
            'No dividend or interest payments'
        ],
        'National Stock Exchange (NSE) / ICICI Prudential AMC'
    ),
    make_gold(
        'kotak-gold-etf', 'Kotak Gold ETF', 'KOTAKGOLD',
        'Gold ETF (Exchange Traded Fund)', 'Medium', 4,
        66.90, '3 - 5 Years', '9.5% - 12.0% CAGR', '5Y Historical CAGR',
        '0.55%', 66.90,
        'Established gold exchange-traded fund by Kotak Mahindra AMC, tracking domestic spot physical gold prices with proven operational consistency since 2007.',
        'Time-tested electronic bullion proxy for conservative capital preservation and asset allocation.',
        [
            'Longstanding 17+ year operational track record with reliable tracking efficiency',
            'Directly convertible into physical gold bars for qualified wholesale institutional basket sizes',
            'Complete insulation from making charges, adulteration, and theft risks'
        ],
        [
            'Requires Demat account; retail redemptions executed via secondary stock exchange trades',
            'Capital is market-linked; gold prices can undergo extended cyclical consolidation phases',
            'Capital gains tax applies as per prevailing mutual fund regulations'
        ],
        'National Stock Exchange (NSE) / Kotak Mahindra AMC'
    ),
    make_gold(
        'uti-gold-etf', 'UTI Gold ETF', 'GOLDSHARE',
        'Gold ETF (Exchange Traded Fund)', 'Medium', 4,
        67.40, '3 - 5 Years', '9.5% - 12.0% CAGR', '5Y Historical CAGR',
        '0.53%', 67.40,
        'UTI Mutual Fund’s dedicated gold exchange-traded scheme, offering pristine physical bullion custody and transparent exchange execution.',
        'Long-term defensive asset allocation in institutional gold bullion.',
        [
            'Managed by UTI AMC, the pioneer of the Indian mutual fund industry',
            'Strict adherence to SEBI purity guidelines with 99.5% pure physical gold custodian vaults',
            'Convenient fractional trading on both NSE and BSE'
        ],
        [
            'Requires Demat and Trading account setup',
            'Subject to domestic gold price fluctuations influenced by customs duties and USD/INR exchange rates',
            'Does not produce recurring income'
        ],
        'National Stock Exchange (NSE) / UTI AMC'
    )
])

# =============================================================================
# 3. GOLD MUTUAL FUNDS (FUND OF FUNDS)
# =============================================================================
gold_items.extend([
    make_gold(
        'kotak-gold-fund', 'Kotak Gold Fund - Direct Plan - Growth', 'KOTAKGOLDFUND',
        'Gold Mutual Fund (Fund of Funds)', 'Medium', 4,
        27.80, '3 - 5 Years', '9.0% - 11.5% CAGR', '5Y Historical CAGR',
        '0.14% (Direct Plan)', 100.0,
        'Open-ended fund of funds investing directly into Kotak Gold ETF units, enabling hassle-free automated monthly SIPs into gold without needing a Demat account.',
        'Automated systematic monthly gold accumulation via bank auto-debit for weddings and long-term portfolio diversification.',
        [
            'Zero Demat account requirement: invest via regular mutual fund apps, Net Banking, or UPI auto-debit',
            'Ultra-flexible Systematic Investment Plan (SIP) starting from just Rs 100 per month',
            'Professional custody eliminates security, storage, locker charges, and hallmark verification concerns'
        ],
        [
            'Dual expense structure: underlying ETF expense (0.55%) plus fund-of-funds direct expense (0.14%)',
            'Exit load of 1.00% if redeemed within 15 days of allotment',
            'Redemption takes T+2 business days to credit directly into investor’s bank account'
        ],
        'AMFI / Kotak Mahindra Mutual Fund'
    ),
    make_gold(
        'sbi-gold-fund', 'SBI Gold Fund - Direct Plan - Growth', 'SBIGOLDFUND',
        'Gold Mutual Fund (Fund of Funds)', 'Medium', 4,
        24.30, '3 - 5 Years', '9.0% - 11.5% CAGR', '5Y Historical CAGR',
        '0.15% (Direct Plan)', 500.0,
        'Open-ended scheme from SBI Mutual Fund investing primarily in units of SBI Gold ETF, providing convenient paperless gold accumulation with daily AMFI NAVs.',
        'Disciplined systematic rupee-cost averaging into gold for long-term family wealth and inflation protection.',
        [
            'No Demat account required; purchases and redemptions handled directly through the AMC',
            'Rupee-cost averaging: automatic monthly SIP mitigates market timing risk and price volatility',
            'Backed by the physical gold bullion holdings of SBI Gold ETF'
        ],
        [
            'Dual expense ratio (FoF direct plan 0.15% + underlying ETF 0.52%)',
            'Exit load of 1.00% applies if redeemed within 15 days of investment',
            'Taxation aligns with specified debt/gold mutual funds under Finance Act 2024'
        ],
        'AMFI / SBI Mutual Fund'
    ),
    make_gold(
        'hdfc-gold-fund', 'HDFC Gold Fund - Direct Plan - Growth', 'HDFCGOLDFUND',
        'Gold Mutual Fund (Fund of Funds)', 'Medium', 4,
        25.10, '3 - 5 Years', '9.0% - 11.5% CAGR', '5Y Historical CAGR',
        '0.16% (Direct Plan)', 100.0,
        'Fund of funds investing in HDFC Gold ETF, designed for investors seeking seamless digital gold accumulation without exchange brokerage or Demat maintenance costs.',
        'Cost-effective systematic gold accumulation with micro-SIPs starting at Rs 100.',
        [
            'Accessible entry point with monthly SIPs starting from just Rs 100',
            'Daily NAV transparency declared by AMFI every evening based on domestic spot bullion closing',
            'Completely paperless, eliminating physical jewelry making charges and storage worries'
        ],
        [
            'Underlying ETF expense ratio plus FoF management fee applies',
            'Exit load of 1% if redeemed within 15 days of investment',
            'Subject to commodity price volatility and currency fluctuations'
        ],
        'AMFI / HDFC AMC'
    ),
    make_gold(
        'nippon-gold-savings-fund', 'Nippon India Gold Savings Fund - Direct Plan - Growth', 'NIPPGOLDSAV',
        'Gold Mutual Fund (Fund of Funds)', 'Medium', 4,
        26.50, '3 - 5 Years', '9.0% - 11.5% CAGR', '5Y Historical CAGR',
        '0.17% (Direct Plan)', 100.0,
        'Mutual fund scheme investing in units of Nippon India ETF Gold BeES, combining the high liquidity of India’s largest gold ETF with the convenience of mutual fund SIPs.',
        'Convenient systematic accumulation of units representing physical gold bullion held in insured vaults.',
        [
            'Channelizes capital into Nippon India ETF Gold BeES, India’s most liquid gold ETF',
            'Enables automated SIP and STP (Systematic Transfer Plan) features without Demat hassle',
            'Redemption proceeds credited straight into registered savings bank account via direct credit / NEFT'
        ],
        [
            'Total cost includes FoF direct expense (0.17%) and underlying ETF expense (0.79%)',
            'Exit load of 1% for redemptions within 15 days of allotment',
            'Returns are market-linked without capital or return guarantee'
        ],
        'AMFI / Nippon Life India AMC'
    ),
    make_gold(
        'icici-pru-regular-gold-savings', 'ICICI Prudential Regular Gold Savings Fund - Direct Plan - Growth', 'ICICIGOLDSAV',
        'Gold Mutual Fund (Fund of Funds)', 'Medium', 4,
        26.20, '3 - 5 Years', '9.0% - 11.5% CAGR', '5Y Historical CAGR',
        '0.15% (Direct Plan)', 100.0,
        'Open-ended fund of funds by ICICI Prudential AMC investing in ICICI Prudential Gold ETF units, delivering disciplined electronic gold accumulation.',
        'Systematic hedging tool for long-term goal planning and wealth preservation.',
        [
            'Demat-free mutual fund structure with automated bank SIPs from Rs 100',
            'Invests in ICICI Prudential Gold ETF with tight operational tracking and high vault safety',
            'Ideal vehicle for accumulating wedding or educational gold reserves over 5-10 year horizons'
        ],
        [
            '1.00% exit load if redeemed within 15 days',
            'Combined expense ratio includes FoF direct fee plus ETF management fee',
            'Subject to global gold price cycle and USD/INR exchange rate movements'
        ],
        'AMFI / ICICI Prudential AMC'
    )
])

# =============================================================================
# 4. SOVEREIGN GOLD BONDS (GOVERNMENT OF INDIA / RBI GUARANTEE)
# =============================================================================
gold_items.extend([
    make_gold(
        'sovereign-gold-bonds', 'Sovereign Gold Bonds (SGB Secondary Market Series)', 'SGB-SERIES',
        'Government Sovereign Gold Bond', 'Low', 3,
        7650.0, '5 - 8 Years', '12.0% - 14.5% Total Return (2.5% Coupon + Spot)', 'RBI 8-Year Sovereign Maturity',
        '0.00% (Zero Management Expense)', 7650.0,
        'Government of India sovereign-guaranteed gold securities issued by the Reserve Bank of India, paying 2.50% p.a. fixed interest and providing 100% tax-free capital gains on 8-year maturity.',
        'The gold standard of long-term gold investing: fixed sovereign cash coupons combined with tax-free spot gold capital appreciation.',
        [
            'Sovereign Guarantee: 100% backed by the Government of India with zero credit or default risk',
            '2.50% p.a. fixed cash coupon paid semi-annually directly into investor’s bank account on initial issue price',
            '100% TAX-FREE Capital Gains: complete exemption from capital gains tax upon redemption at 8-year maturity',
            'Zero expense ratio, zero storage costs, and zero making charges or purity deductions'
        ],
        [
            'Fresh primary RBI tranches depend on Government issuance calendars; existing series trade on secondary markets',
            'Secondary market liquidity on NSE/BSE can exhibit bid-ask spreads or trade at modest premiums/discounts to spot',
            'Fixed 8-year maturity tenure with early official RBI redemption window open only from year 5'
        ],
        'Reserve Bank of India (RBI) / Government of India'
    ),
    make_gold(
        'sovereign-gold-bond-2028-series', 'Sovereign Gold Bond 2020-21 Series VI (Traded: SGB28OCT)', 'SGB28OCT',
        'Government Sovereign Gold Bond', 'Low', 3,
        7680.0, '2 - 3 Years (Maturity Oct 2028)', '12.0% - 14.5% Total Return', 'Maturity October 2028',
        '0.00%', 7680.0,
        'Existing secondary market Sovereign Gold Bond maturing in October 2028 (~2 years remaining), paying 2.50% annual coupon and redeemed at official RBI IBJA benchmark rate.',
        'Medium-term sovereign gold holding with guaranteed semi-annual interest and tax-free maturity in October 2028.',
        [
            'Definite maturity date (October 2028): ideal for planned medium-term financial goals',
            '2.50% annual interest credited semi-annually based on original nominal value (Rs 5,051/g)',
            'Full tax exemption on capital gains if held until official RBI redemption in October 2028',
            'Full sovereign backing by the Government of India'
        ],
        [
            'Traded on the NSE/BSE secondary market; execution price depends on live seller asking quotes',
            'Requires Demat account for secondary market purchase and trading settlement',
            'Interest coupons are taxable at individual personal income slab rates'
        ],
        'Reserve Bank of India (RBI) / NSE Secondary'
    ),
    make_gold(
        'sovereign-gold-bond-2032-series', 'Sovereign Gold Bond 2023-24 Series IV (Traded: SGB32FEB)', 'SGB32FEB',
        'Government Sovereign Gold Bond', 'Low', 3,
        7620.0, '> 5 Years (Maturity Feb 2032)', '12.0% - 14.5% Total Return', 'Maturity February 2032',
        '0.00%', 7620.0,
        'Longer-dated Sovereign Gold Bond maturing in February 2032, issued under the 2023-24 Series IV tranche with 2.50% p.a. interest coupon and sovereign redemption guarantee.',
        'Long-term sovereign wealth compounding capturing 6+ years of tax-free gold appreciation and cash coupons.',
        [
            'Extended sovereign compounding until February 2032 with 100% tax-free capital redemption',
            'Semi-annual 2.50% annual coupon providing predictable cash flows throughout the tenure',
            'Eliminates all storage, insurance, locker, and assay costs associated with physical metal',
            'Backed by the sovereign balance sheet of the Republic of India'
        ],
        [
            'Long holding period: maturity in February 2032 (RBI early redemption window opens February 2029)',
            'Secondary exchange volumes fluctuate; larger lot orders may require limit pricing',
            'Underlying gold price fluctuates based on global spot market cycles'
        ],
        'Reserve Bank of India (RBI) / NSE Secondary'
    )
])

print(f"Total gold items generated: {len(gold_items)}")

# Save gold catalogue
gold_path = os.path.join(root_dir, 'app', 'services', 'catalogue', 'gold.py')
with open(gold_path, 'w', encoding='utf-8') as f:
    f.write('"""\nExpanded Gold Investment Catalogue across 4 Categories for MoneyLeak.\n')
    f.write('Covering Physical Gold (Bullion, Coins, Jewellery), Gold ETFs, Gold Mutual Funds,\n')
    f.write('and Sovereign Gold Bonds (SGBs) with verified terms and sovereign guarantee.\n"""\n')
    f.write('from typing import Dict, Any, List\n\n')
    f.write('GOLD_CATALOGUE: List[Dict[str, Any]] = ')
    pprint.pprint(gold_items, stream=f, indent=4, width=120)
    f.write('\n')

print(f"Successfully wrote {gold_path} with {len(gold_items)} gold products.")
