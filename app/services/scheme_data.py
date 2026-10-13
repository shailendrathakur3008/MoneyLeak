"""
Curated Indian Financial Market Investment Schemes Database for MoneyLeak.

Strictly provides vetted, authentic Indian investments across the FOUR approved categories:
1. Stocks & Equity (NSE/BSE Listed)
2. Equity Mutual Funds (AMFI / SEBI Regulated)
3. SIP Investments (Systematic regular investing in eligible equity funds)
4. Gold (Gold ETFs & Gold Mutual Funds)

Strictly excludes government savings schemes (PPF, NSC), debt/fixed deposits, bonds,
NPS/retirement products, Sovereign Gold Bonds, REITs/real estate, and commodity derivatives.
"""
from typing import Dict, Any, List, Optional

SCHEME_CATEGORIES = {
    'STOCKS_EQUITY': {
        'id': 'STOCKS_EQUITY',
        'name': 'Stocks & Equity',
        'icon': 'chart-candlestick',
        'description': 'Direct equity shares listed on NSE/BSE across Large-Cap, Growth, Dividend, Fundamental and Sector opportunities.',
        'regulator': 'SEBI / NSE / BSE'
    },
    'EQUITY_MUTUAL_FUNDS': {
        'id': 'EQUITY_MUTUAL_FUNDS',
        'name': 'Equity Mutual Funds',
        'icon': 'chart-pie',
        'description': 'Professionally managed pooled equity portfolios: Large-Cap, Flexi-Cap, Mid-Cap, Small-Cap, Index, and ELSS funds via SIP or Lump Sum.',
        'regulator': 'SEBI / AMFI'
    },
    'SIP_INVESTMENTS': {
        'id': 'SIP_INVESTMENTS',
        'name': 'SIP Investments',
        'icon': 'calendar-clock',
        'description': 'Dedicated systematic monthly investment planning in verified equity mutual funds. (An investment method linked to equity funds).',
        'regulator': 'SEBI / AMFI'
    },
    'GOLD': {
        'id': 'GOLD',
        'name': 'Gold',
        'icon': 'coins',
        'description': 'Strategic hedge against inflation and currency depreciation via Gold ETFs and Gold Mutual Funds.',
        'regulator': 'SEBI / AMFI'
    }
}

SCHEMES_DATABASE: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. STOCKS & EQUITY
    # =========================================================================
    # Large-Cap Stocks
    {
        'id': 'reliance-industries',
        'name': 'Reliance Industries Limited (NSE: RELIANCE)',
        'short_name': 'Reliance Industries',
        'ticker': 'RELIANCE',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Large-Cap Stock',
        'provider': 'Reliance Industries Ltd / NSE: RELIANCE',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 2870,
        'min_sip': 2870,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 50',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹2,870.00',
        'historical_cagr': {'1y': 22.0, '3y': 14.8, '5y': 18.2, '10y': 21.4},
        'expected_annual_return': 14.0,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%. Dividends taxed at income slab.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 settlement on NSE/BSE with highest daily market liquidity.',
        'objective': 'Direct equity ownership in India’s largest market-cap conglomerate spanning telecom (Jio), retail, and energy.',
        'how_it_works': 'Purchased via Demat account. Generates wealth through share price appreciation and regular dividends.',
        'eligibility': 'KYC-compliant Demat and Trading account holders.',
        'advantages': ['Unrivalled market leader across Indian telecom, 5G, and retail', 'Robust operating cashflows', 'Consistent multi-decade wealth compounder'],
        'disadvantages': ['Single-company concentration risk', 'Large ongoing capex cycles in new clean energy'],
        'best_for_tags': ['large-cap', 'wealth-creation', 'long-term', 'bluechip'],
        'data_source': 'National Stock Exchange (NSE) / BSE Filings',
        'last_updated': 'October 2026'
    },
    {
        'id': 'tata-consultancy-services',
        'name': 'Tata Consultancy Services Limited (NSE: TCS)',
        'short_name': 'TCS',
        'ticker': 'TCS',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Large-Cap Stock',
        'provider': 'Tata Sons / NSE: TCS',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 4120,
        'min_sip': 4120,
        'lock_in_years': 0,
        'benchmark': 'NIFTY IT',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹4,120.00',
        'historical_cagr': {'1y': 18.5, '3y': 12.2, '5y': 16.1, '10y': 16.9},
        'expected_annual_return': 13.5,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%. ~1.6% dividend yield taxed as income.',
        'tax_benefit': 'None',
        'liquidity': 'Instant intraday liquidity on NSE and BSE (T+1 settlement).',
        'objective': 'Ownership in Asia’s largest IT software enterprise powering global digital transformation and enterprise software solutions.',
        'how_it_works': 'Global software delivery with zero net debt, industry-leading margins (>24%), and generous share buybacks.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Tata Group corporate governance gold standard', 'High return on equity (ROE > 45%)', 'Resilient free cash flow conversion'],
        'disadvantages': ['Vulnerable to US and European enterprise tech budget slowdowns'],
        'best_for_tags': ['large-cap', 'bluechip', 'regular-income', 'long-term'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },
    {
        'id': 'hdfc-bank',
        'name': 'HDFC Bank Limited (NSE: HDFCBANK)',
        'short_name': 'HDFC Bank',
        'ticker': 'HDFCBANK',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Large-Cap Stock',
        'provider': 'HDFC Bank Ltd / NSE: HDFCBANK',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 1680,
        'min_sip': 1680,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Bank',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹1,680.00',
        'historical_cagr': {'1y': 15.2, '3y': 10.8, '5y': 14.5, '10y': 17.8},
        'expected_annual_return': 13.5,
        'tax_treatment': 'Equity capital gains tax: LTCG @ 12.5%, STCG @ 20%. Dividends taxed at slab rate.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 liquid settlement on Indian exchanges.',
        'objective': 'Direct equity ownership in India’s premier private financial sector bellwether with nationwide franchise.',
        'how_it_works': 'Dominates retail lending, corporate banking, credit cards, and digital transaction processing.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Best-in-class asset quality and NPA management', 'Massive distribution network of 8,500+ branches', 'Core compounding backbone of Indian banking'],
        'disadvantages': ['Post-merger credit-deposit ratio normalization taking time'],
        'best_for_tags': ['large-cap', 'bluechip', 'banking', 'long-term'],
        'data_source': 'NSE / RBI Scheduled Bank Reports',
        'last_updated': 'October 2026'
    },
    {
        'id': 'infosys-limited',
        'name': 'Infosys Limited (NSE: INFY)',
        'short_name': 'Infosys',
        'ticker': 'INFY',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Large-Cap Stock',
        'provider': 'Infosys Ltd / NSE: INFY',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 1910,
        'min_sip': 1910,
        'lock_in_years': 0,
        'benchmark': 'NIFTY IT',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹1,910.00',
        'historical_cagr': {'1y': 26.5, '3y': 13.4, '5y': 17.2, '10y': 15.8},
        'expected_annual_return': 14.0,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 market settlement on NSE/BSE.',
        'objective': 'Participation in digital architecture, cloud engineering, and global software engineering growth.',
        'how_it_works': 'Delivers high-margin technology consulting and digital solutions across 50+ countries.',
        'eligibility': 'Demat account holders.',
        'advantages': ['High capital return policy (85% free cash flow returned to shareholders)', 'Debt-free balance sheet', 'Substantial enterprise digital contract pipeline'],
        'disadvantages': ['Sensitivity to global tech enterprise spending sentiment'],
        'best_for_tags': ['large-cap', 'bluechip', 'it-tech', 'long-term'],
        'data_source': 'NSE Filings',
        'last_updated': 'October 2026'
    },

    # Growth Stocks
    {
        'id': 'trent-limited',
        'name': 'Trent Limited (NSE: TRENT)',
        'short_name': 'Trent Ltd',
        'ticker': 'TRENT',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Growth Stock',
        'provider': 'Tata Group / NSE: TRENT',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 7450,
        'min_sip': 7450,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 500',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹7,450.00',
        'historical_cagr': {'1y': 152.0, '3y': 78.4, '5y': 45.8, '10y': 38.2},
        'expected_annual_return': 20.0,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High daily trading volume on NSE/BSE.',
        'objective': 'Aggressive consumer discretionary growth through India’s most successful fast-fashion retail formats (Zudio & Westside).',
        'how_it_works': 'Disruptive agile supply chain model rolling out 150+ profitable stores annually with rapid inventory turns.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Unprecedented retail earnings CAGR (>40%)', 'Zudio value-fashion moat', 'Tata Group backing'],
        'disadvantages': ['Elevated valuation multiples require sustaining high growth trajectory'],
        'best_for_tags': ['growth', 'high-risk', 'consumer', 'multibagger'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },
    {
        'id': 'tata-motors',
        'name': 'Tata Motors Limited (NSE: TATAMOTORS)',
        'short_name': 'Tata Motors',
        'ticker': 'TATAMOTORS',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Growth Stock',
        'provider': 'Tata Group / NSE: TATAMOTORS',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 960,
        'min_sip': 960,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Auto',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹960.00',
        'historical_cagr': {'1y': 52.4, '3y': 41.2, '5y': 38.4, '10y': 14.2},
        'expected_annual_return': 16.5,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 liquid settlement on NSE/BSE.',
        'objective': 'High-conviction turnaround in automotive manufacturing, commercial vehicle leadership, and Indian electric vehicle (EV) dominance.',
        'how_it_works': '70%+ EV market share in India combined with premium luxury cash generation from Jaguar Land Rover (JLR).',
        'eligibility': 'Demat account holders.',
        'advantages': ['Dominant early-mover leadership in Indian electric passenger cars', 'Deleveraging balance sheet', 'JLR order book strength'],
        'disadvantages': ['Automotive industry cyclicality and raw material cost volatility'],
        'best_for_tags': ['growth', 'auto', 'ev', 'wealth-creation'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },
    {
        'id': 'titan-company',
        'name': 'Titan Company Limited (NSE: TITAN)',
        'short_name': 'Titan Company',
        'ticker': 'TITAN',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Growth Stock',
        'provider': 'Tata Group & TIDCO / NSE: TITAN',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 3520,
        'min_sip': 3520,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 50',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹3,520.00',
        'historical_cagr': {'1y': 18.2, '3y': 19.5, '5y': 23.6, '10y': 24.1},
        'expected_annual_return': 16.0,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 trading settlement on NSE/BSE.',
        'objective': 'Capture long-term formalization of India’s massive jewelry (Tanishq), watches, and premium lifestyle consumption.',
        'how_it_works': 'Legendary consumer compounding with trusted Tanishq brand capturing market share from unorganized jewelers.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Trusted Tata consumer umbrella', 'High return on capital employed (>30%)', 'Multi-decade secular compounding story'],
        'disadvantages': ['Gold price fluctuations can temporarily impact retail inventory margins'],
        'best_for_tags': ['growth', 'consumer', 'lifestyle', 'long-term'],
        'data_source': 'NSE / BSE Filings',
        'last_updated': 'October 2026'
    },

    # Dividend-Oriented Stocks
    {
        'id': 'itc-limited',
        'name': 'ITC Limited (NSE: ITC)',
        'short_name': 'ITC Ltd',
        'ticker': 'ITC',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Dividend-Oriented Stock',
        'provider': 'ITC Ltd / NSE: ITC',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 492,
        'min_sip': 492,
        'lock_in_years': 0,
        'benchmark': 'NIFTY FMCG',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹492.50',
        'historical_cagr': {'1y': 14.2, '3y': 28.5, '5y': 18.2, '10y': 11.5},
        'expected_annual_return': 12.0,
        'tax_treatment': 'Equity taxation on capital gains; Dividend yield ~3.2% p.a. taxed at investor income slab.',
        'tax_benefit': 'None',
        'liquidity': 'High daily volume on NSE and BSE.',
        'objective': 'Defensive FMCG portfolio compounding with high dividend yield and expanding non-cigarette consumer brands.',
        'how_it_works': 'Cash-cow core business funds rapid growth in packaged foods (Aashirvaad, Sunfeast), hotels, and agri-business.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Strong 3%+ dividend yield providing reliable passive cashflow', 'Pricing power and massive consumer distribution', 'Low beta defensive resilience during crashes'],
        'disadvantages': ['Tobacco taxation regulatory overhangs'],
        'best_for_tags': ['dividend', 'regular-income', 'defensive', 'beginners'],
        'data_source': 'NSE / BSE Filings',
        'last_updated': 'October 2026'
    },
    {
        'id': 'coal-india-limited',
        'name': 'Coal India Limited (NSE: COALINDIA)',
        'short_name': 'Coal India',
        'ticker': 'COALINDIA',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Dividend-Oriented Stock',
        'provider': 'Government of India (Maharatna PSU) / NSE: COALINDIA',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 485,
        'min_sip': 485,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Energy',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹485.00',
        'historical_cagr': {'1y': 44.0, '3y': 38.6, '5y': 24.1, '10y': 7.5},
        'expected_annual_return': 13.0,
        'tax_treatment': 'Equity capital gains tax; High dividend yield (~5.4% p.a.) added to taxable income.',
        'tax_benefit': 'None',
        'liquidity': 'High trading volume on NSE and BSE.',
        'objective': 'High-yield cash generation powering Indian thermal electricity baseload with substantial sovereign dividend payouts.',
        'how_it_works': 'Near-monopoly miner producing over 80% of India’s domestic coal, distributing the majority of free cash flow as dividends.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Market-leading 5%+ dividend yield', 'Near-monopoly operating moat', 'High sovereign cash reserves'],
        'disadvantages': ['Long-term structural transition toward renewable energy'],
        'best_for_tags': ['dividend', 'regular-income', 'psu', 'value'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },

    # Fundamental-Based Stocks
    {
        'id': 'larsen-and-toubro',
        'name': 'Larsen & Toubro Limited (NSE: LT)',
        'short_name': 'L&T',
        'ticker': 'LT',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Fundamental-Based Stock',
        'provider': 'Larsen & Toubro Ltd / NSE: LT',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 3620,
        'min_sip': 3620,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Infra',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹3,620.00',
        'historical_cagr': {'1y': 24.2, '3y': 22.8, '5y': 22.4, '10y': 16.5},
        'expected_annual_return': 15.0,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 liquid settlement on NSE/BSE.',
        'objective': 'Pure play on India’s massive domestic and Middle-East infrastructure, defense, hydrocarbon, and hi-tech engineering capex.',
        'how_it_works': 'Record multi-lakh-crore order book execution delivering complex mega-projects across transportation, power, and defense.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Peerless engineering capability and execution track record', 'Unrivalled order backlog visibility', 'Beneficiary of government capex push'],
        'disadvantages': ['Working capital intensity on large infrastructure contracts'],
        'best_for_tags': ['fundamental', 'infrastructure', 'wealth-creation', 'bluechip'],
        'data_source': 'NSE / BSE Filings',
        'last_updated': 'October 2026'
    },
    {
        'id': 'bharti-airtel',
        'name': 'Bharti Airtel Limited (NSE: BHARTIARTL)',
        'short_name': 'Bharti Airtel',
        'ticker': 'BHARTIARTL',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Fundamental-Based Stock',
        'provider': 'Bharti Enterprises / NSE: BHARTIARTL',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 1680,
        'min_sip': 1680,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 50',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹1,680.00',
        'historical_cagr': {'1y': 58.2, '3y': 31.4, '5y': 25.1, '10y': 18.2},
        'expected_annual_return': 16.0,
        'tax_treatment': 'Equity capital gains tax: LTCG @ 12.5%, STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 settlement on NSE/BSE.',
        'objective': 'Dominant telecom duopoly play benefiting from steadily rising ARPU (Average Revenue Per User), 5G monetization, and Africa growth.',
        'how_it_works': 'Premium subscriber base with highest industry ARPU, data center expansion (Nxtra), and enterprise cloud solutions.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Consolidated duopoly market structure in Indian mobile services', 'Strong operating leverage expansion', 'Expanding enterprise and fiber revenues'],
        'disadvantages': ['Regulatory spectrum fee reviews and high network equipment maintenance'],
        'best_for_tags': ['fundamental', 'telecom', 'growth', 'long-term'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },

    # Sector-Based Stocks
    {
        'id': 'sun-pharmaceutical',
        'name': 'Sun Pharmaceutical Industries (NSE: SUNPHARMA)',
        'short_name': 'Sun Pharma',
        'ticker': 'SUNPHARMA',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Sector-Based Stock',
        'provider': 'Sun Pharma Ltd / NSE: SUNPHARMA',
        'risk_level': 'High',
        'risk_rating': 4,
        'min_investment': 1840,
        'min_sip': 1840,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Pharma',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹1,840.00',
        'historical_cagr': {'1y': 48.6, '3y': 28.2, '5y': 24.8, '10y': 10.4},
        'expected_annual_return': 14.5,
        'tax_treatment': 'Equity taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 settlement on NSE/BSE.',
        'objective': 'Healthcare & global specialty therapeutics leadership across dermatology, ophthalmology, and chronic care in India and the US.',
        'how_it_works': 'Dominant Indian domestic formulations market share combined with patented specialty drug pipeline in global markets.',
        'eligibility': 'Demat account holders.',
        'advantages': ['#1 market share in Indian domestic pharmaceutical formulations', 'High-margin proprietary specialty drugs pipeline', 'Defensive revenue characteristics'],
        'disadvantages': ['US FDA manufacturing facility inspection audits'],
        'best_for_tags': ['sector', 'pharma', 'healthcare', 'defensive'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },
    {
        'id': 'tata-power-company',
        'name': 'Tata Power Company Limited (NSE: TATAPOWER)',
        'short_name': 'Tata Power',
        'ticker': 'TATAPOWER',
        'category': 'STOCKS_EQUITY',
        'subcategory': 'Sector-Based Stock',
        'provider': 'Tata Group / NSE: TATAPOWER',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 435,
        'min_sip': 435,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Energy',
        'expense_ratio': '0.00% (Direct Equity)',
        'current_rate_or_nav': '₹435.00',
        'historical_cagr': {'1y': 62.4, '3y': 32.5, '5y': 36.2, '10y': 19.8},
        'expected_annual_return': 16.0,
        'tax_treatment': 'Equity capital gains tax: LTCG @ 12.5%, STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 market settlement on NSE/BSE.',
        'objective': 'Pure play on India’s green energy revolution: solar manufacturing, wind generation, EV charging corridors, and smart distribution.',
        'how_it_works': 'Transitioning rapidly from thermal to 70%+ clean green energy capacity by 2030, with nationwide EV charging infrastructure rollout.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Comprehensive clean energy value chain from solar cells to rooftop EPC', 'Over 5,000 public EV chargers deployed nationwide', 'Tata brand trust'],
        'disadvantages': ['High capital requirements and interest rate sensitivity'],
        'best_for_tags': ['sector', 'clean-energy', 'growth', 'ev-infrastructure'],
        'data_source': 'National Stock Exchange (NSE)',
        'last_updated': 'October 2026'
    },

    # =========================================================================
    # 2. EQUITY MUTUAL FUNDS
    # =========================================================================
    # Large-Cap Funds
    {
        'id': 'sbi-bluechip-fund',
        'name': 'SBI Bluechip Fund - Direct Plan',
        'short_name': 'SBI Bluechip Fund',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Large-Cap Fund',
        'provider': 'SBI Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'S&P BSE 100 TRI',
        'expense_ratio': '0.85%',
        'current_rate_or_nav': '₹98.40',
        'historical_cagr': {'1y': 22.8, '3y': 14.8, '5y': 16.8, '10y': 14.2},
        'expected_annual_return': 13.5,
        'tax_treatment': 'Equity Taxation: LTCG > ₹1.25 Lakh taxed @ 12.5%; STCG (<1 yr) @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (T+2 business days redemption; 1% exit load if redeemed within 1 year).',
        'objective': 'Capital appreciation through actively selected top 100 large market-cap established Indian corporate leaders.',
        'how_it_works': 'Fund managers deploy disciplined bottom-up research investing predominantly in bluechips with dominant market share.',
        'eligibility': 'Resident Indians, HUFs, and NRIs with valid KYC.',
        'advantages': ['Established pedigree from India’s largest asset manager', 'Lower volatility than mid/small cap funds', 'Flexible monthly SIP from ₹500'],
        'disadvantages': ['Active expense ratio higher than passive index funds', 'Market risk with equity volatility'],
        'best_for_tags': ['large-cap', 'beginners', 'sip', 'long-term'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / SBI Mutual Fund Official Factsheet',
        'last_updated': 'October 2026'
    },
    {
        'id': 'mirae-asset-large-cap',
        'name': 'Mirae Asset Large Cap Fund - Direct Plan',
        'short_name': 'Mirae Asset Large Cap',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Large-Cap Fund',
        'provider': 'Mirae Asset Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 100 TRI',
        'expense_ratio': '0.54%',
        'current_rate_or_nav': '₹124.50',
        'historical_cagr': {'1y': 23.4, '3y': 14.2, '5y': 16.2, '10y': 15.1},
        'expected_annual_return': 13.5,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (T+2 redemption; 1% exit load for redemptions within 365 days).',
        'objective': 'Long-term capital growth by investing in high-quality large-cap companies with robust cash flows and competitive moats.',
        'how_it_works': 'Maintains at least 80% allocation in top 100 Indian stocks, emphasizing sound management and sector leadership.',
        'eligibility': 'KYC-compliant Indian individuals and entities.',
        'advantages': ['Low direct plan expense ratio (0.54%)', 'Disciplined risk control metrics', 'Excellent 10-year track record'],
        'disadvantages': ['Subject to broader market drawdowns during equity market corrections'],
        'best_for_tags': ['large-cap', 'long-term', 'sip', 'bluechip'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / Mirae Asset Global Factsheet',
        'last_updated': 'October 2026'
    },

    # Flexi-Cap Funds
    {
        'id': 'parag-parikh-flexi-cap',
        'name': 'Parag Parikh Flexi Cap Fund - Direct Plan',
        'short_name': 'PPFAS Flexi Cap',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Flexi-Cap Fund',
        'provider': 'PPFAS Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 1000,
        'min_sip': 1000,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 500 TRI',
        'expense_ratio': '0.62%',
        'current_rate_or_nav': '₹82.14',
        'historical_cagr': {'1y': 31.8, '3y': 19.4, '5y': 22.6, '10y': 19.8},
        'expected_annual_return': 16.0,
        'tax_treatment': 'Equity Taxation: LTCG > ₹1.25 Lakh taxed @ 12.5%; STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (Exit load of 2% within 365 days, 1% between 366-730 days, zero thereafter).',
        'objective': 'Long-term wealth creation by dynamically allocating across Indian large, mid, small caps and selective global tech equities.',
        'how_it_works': 'Deep value investing philosophy holding cash buffers during market euphoria and buying quality companies on dips.',
        'eligibility': 'KYC-compliant Indian residents and NRIs.',
        'advantages': ['Proven long-term alpha over 10+ years', 'Diversified across market caps without rigid mandate constraints', 'High promoter co-investment'],
        'disadvantages': ['Exit load applies for up to 2 years to discourage hot-money speculation'],
        'best_for_tags': ['flexi-cap', 'long-term', 'sip', 'wealth-creation'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / PPFAS AMC Disclosures',
        'last_updated': 'October 2026'
    },
    {
        'id': 'hdfc-flexi-cap-fund',
        'name': 'HDFC Flexi Cap Fund - Direct Plan',
        'short_name': 'HDFC Flexi Cap',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Flexi-Cap Fund',
        'provider': 'HDFC Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 500 TRI',
        'expense_ratio': '0.78%',
        'current_rate_or_nav': '₹1,840.20',
        'historical_cagr': {'1y': 34.2, '3y': 22.8, '5y': 24.2, '10y': 17.5},
        'expected_annual_return': 16.5,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (T+2 redemption; 1% exit load for redemptions within 1 year).',
        'objective': 'Capital appreciation by maintaining flexible exposure across India’s top 500 enterprises based on relative valuations.',
        'how_it_works': 'Actively managed by veteran fund managers rotating between cyclicals, value plays, and compounding growth leaders.',
        'eligibility': 'Resident individuals and HUFs.',
        'advantages': ['Exceptional 3Y & 5Y alpha generation', 'High liquidity and institutional risk management', 'Ideal core equity portfolio foundation'],
        'disadvantages': ['Large AUM requires disciplined portfolio liquidity balancing'],
        'best_for_tags': ['flexi-cap', 'long-term', 'sip', 'wealth-creation'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / HDFC AMC Factsheet',
        'last_updated': 'October 2026'
    },

    # Mid-Cap Funds
    {
        'id': 'motilal-oswal-midcap',
        'name': 'Motilal Oswal Midcap Fund - Direct Plan',
        'short_name': 'Motilal Midcap',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Mid-Cap Fund',
        'provider': 'Motilal Oswal Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Midcap 150 TRI',
        'expense_ratio': '0.68%',
        'current_rate_or_nav': '₹112.40',
        'historical_cagr': {'1y': 48.2, '3y': 34.1, '5y': 32.5, '10y': 20.8},
        'expected_annual_return': 17.5,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (1% exit load if redeemed within 15 days).',
        'objective': 'Aggressive capital growth by taking concentrated, high-conviction positions in fast-growing mid-market companies.',
        'how_it_works': 'QGLP philosophy (Quality, Growth, Longevity, Price) investing in future large-caps during their fastest expansion phase.',
        'eligibility': 'Investors with high risk appetite and 5+ year horizon.',
        'advantages': ['Top-quartile mid-cap CAGR across 3, 5, and 10 years', 'Focused high-conviction portfolio', 'Low exit load window'],
        'disadvantages': ['Higher volatility than large-cap and index funds'],
        'best_for_tags': ['mid-cap', 'high-growth', 'sip', 'wealth-creation'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / Motilal Oswal AMC',
        'last_updated': 'October 2026'
    },
    {
        'id': 'hdfc-mid-cap-opps',
        'name': 'HDFC Mid-Cap Opportunities Fund - Direct Plan',
        'short_name': 'HDFC Mid-Cap Opps',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Mid-Cap Fund',
        'provider': 'HDFC Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Midcap 150 TRI',
        'expense_ratio': '0.74%',
        'current_rate_or_nav': '₹178.60',
        'historical_cagr': {'1y': 41.5, '3y': 28.6, '5y': 26.8, '10y': 19.4},
        'expected_annual_return': 16.5,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (1% exit load for redemptions within 1 year).',
        'objective': 'Long-term capital appreciation by building a well-diversified portfolio of fundamentally sound mid-sized Indian businesses.',
        'how_it_works': 'Invests in businesses positioned between rank 101 and 250 by market capitalization with durable competitive advantages.',
        'eligibility': 'KYC-compliant Indian investors.',
        'advantages': ['One of India’s largest and most trusted mid-cap funds', 'Consistent multi-cycle compounding track record', 'Broad sector diversification'],
        'disadvantages': ['Mid-cap volatility during equity corrections'],
        'best_for_tags': ['mid-cap', 'growth', 'sip', 'long-term'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / HDFC AMC Factsheet',
        'last_updated': 'October 2026'
    },

    # Small-Cap Funds
    {
        'id': 'nippon-india-small-cap',
        'name': 'Nippon India Small Cap Fund - Direct Plan',
        'short_name': 'Nippon Small Cap',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Small-Cap Fund',
        'provider': 'Nippon Life India Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Smallcap 250 TRI',
        'expense_ratio': '0.67%',
        'current_rate_or_nav': '₹185.30',
        'historical_cagr': {'1y': 42.8, '3y': 31.4, '5y': 34.6, '10y': 24.2},
        'expected_annual_return': 18.0,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (1% exit load if redeemed within 1 month).',
        'objective': 'Maximized long-term capital compounding by identifying high-potential early-stage companies beyond the top 250 market cap.',
        'how_it_works': 'Highly diversified portfolio of 150+ small-cap stocks to minimize individual business failure risk while capturing multibagger growth.',
        'eligibility': 'High risk-tolerance investors with 7+ year horizon.',
        'advantages': ['Flagship small-cap fund with proven 10+ year track record', 'Prudent individual stock caps to mitigate downside risk', 'Exceptional compounding engine'],
        'disadvantages': ['Substantial drawdown potential during severe market sell-offs', 'Lump-sum inflows may be occasionally capped by AMC'],
        'best_for_tags': ['small-cap', 'high-risk', 'high-growth', 'sip'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / Nippon India AMC Disclosures',
        'last_updated': 'October 2026'
    },
    {
        'id': 'quant-small-cap-fund',
        'name': 'Quant Small Cap Fund - Direct Plan',
        'short_name': 'Quant Small Cap',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Small-Cap Fund',
        'provider': 'Quant Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 5000,
        'min_sip': 1000,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Smallcap 250 TRI',
        'expense_ratio': '0.74%',
        'current_rate_or_nav': '₹242.10',
        'historical_cagr': {'1y': 44.5, '3y': 28.6, '5y': 38.2, '10y': 22.1},
        'expected_annual_return': 18.5,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'Exit load of 1% if redeemed within 1 year; high volatility.',
        'objective': 'Aggressive capital compounding through quantitative algorithmic momentum stock selection in emerging companies.',
        'how_it_works': 'Dynamic VLRT framework (Valuation, Liquidity, Risk appetite, Timing) rotating dynamically across small-cap sectors.',
        'eligibility': 'Investors with high risk appetite and 7+ year horizon.',
        'advantages': ['Industry-leading multi-year return CAGR', 'Agile sector allocation model', 'High compounding potential'],
        'disadvantages': ['Severe drawdowns during broad market corrections', 'High portfolio turnover ratio'],
        'best_for_tags': ['small-cap', 'high-risk', 'momentum', 'sip'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / Quant AMC Disclosures',
        'last_updated': 'October 2026'
    },

    # Equity Index Funds
    {
        'id': 'uti-nifty-50-index',
        'name': 'UTI Nifty 50 Index Fund - Direct Plan',
        'short_name': 'UTI Nifty 50 Index',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Equity Index Fund',
        'provider': 'UTI Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 500,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY 50 TRI',
        'expense_ratio': '0.18%',
        'current_rate_or_nav': '₹182.40',
        'historical_cagr': {'1y': 24.5, '3y': 15.2, '5y': 16.8, '10y': 13.9},
        'expected_annual_return': 13.5,
        'tax_treatment': 'Equity Taxation: LTCG > ₹1.25 Lakh taxed @ 12.5%; STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (T+2 business days redemption; zero exit load).',
        'objective': 'Passively replicate the performance of India’s top 50 bluechip corporate leaders at minimal expense ratio and tracking error.',
        'how_it_works': 'Matches the constituents and weightings of the benchmark Nifty 50 index with near-zero cash drag.',
        'eligibility': 'All individual and institutional investors.',
        'advantages': ['Ultra-low expense ratio (0.18%)', 'Zero fund-manager risk or style drift', 'Lowest tracking error in Indian mutual funds', 'Zero exit load'],
        'disadvantages': ['Subject to full broader market volatility without active cash preservation'],
        'best_for_tags': ['index-fund', 'beginners', 'low-cost', 'sip', 'long-term'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / UTI Mutual Fund Factsheet',
        'last_updated': 'October 2026'
    },
    {
        'id': 'hdfc-nifty-next-50',
        'name': 'HDFC Nifty Next 50 Index Fund - Direct Plan',
        'short_name': 'HDFC Nifty Next 50',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'Equity Index Fund',
        'provider': 'HDFC Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 500,
        'min_sip': 500,
        'lock_in_years': 0,
        'benchmark': 'NIFTY Next 50 TRI',
        'expense_ratio': '0.30%',
        'current_rate_or_nav': '₹86.20',
        'historical_cagr': {'1y': 38.5, '3y': 19.8, '5y': 21.4, '10y': 16.2},
        'expected_annual_return': 15.0,
        'tax_treatment': 'Equity Taxation: LTCG @ 12.5% (> ₹1.25 Lakh); STCG @ 20%.',
        'tax_benefit': 'None',
        'liquidity': 'High (Zero exit load after 3 days).',
        'objective': 'Invest in the next tier of 50 emerging bluechips (ranks 51-100) poised to graduate into the benchmark Nifty 50.',
        'how_it_works': 'Passive indexing capturing high-growth leaders in aerospace, green energy, electronics, and chemicals.',
        'eligibility': 'KYC-compliant Indian investors.',
        'advantages': ['Higher historical return than Nifty 50', 'Zero fund-manager bias', 'Low cost indexing format'],
        'disadvantages': ['Higher short-term volatility than core Nifty 50'],
        'best_for_tags': ['index-fund', 'growth', 'sip', 'long-term'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / HDFC AMC',
        'last_updated': 'October 2026'
    },

    # ELSS Funds (Tax Saving)
    {
        'id': 'mirae-asset-elss-tax-saver',
        'name': 'Mirae Asset ELSS Tax Saver Fund - Direct Plan',
        'short_name': 'Mirae Asset ELSS',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'ELSS Tax-Saving Fund',
        'provider': 'Mirae Asset Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 500,
        'min_sip': 500,
        'lock_in_years': 3,
        'benchmark': 'NIFTY 500 TRI',
        'expense_ratio': '0.59%',
        'current_rate_or_nav': '₹48.72',
        'historical_cagr': {'1y': 28.2, '3y': 16.8, '5y': 18.9, '10y': 17.4},
        'expected_annual_return': 15.0,
        'tax_treatment': 'Section 80C deduction up to ₹1.5 Lakh. LTCG on redemption taxed @ 12.5% beyond ₹1.25 Lakh.',
        'tax_benefit': 'Section 80C (Save up to ₹46,800 under Old Tax Regime)',
        'liquidity': 'Mandatory 3-Year statutory lock-in from date of each SIP installment.',
        'objective': 'Dual benefit of statutory income tax deduction under Section 80C and aggressive equity capital growth.',
        'how_it_works': 'Invests predominantly in diversified large-cap and growth mid-cap stocks with a 36-month lock-in period.',
        'eligibility': 'Indian taxpayers (Individuals & HUFs).',
        'advantages': ['Shortest lock-in period (3 years) among all Section 80C tax savers', 'Significantly higher historical returns than debt tax-savers', 'Flexible SIP from ₹500/mo'],
        'disadvantages': ['Market linked risk with equity volatility', 'Each SIP installment is locked in for 36 months independently'],
        'best_for_tags': ['elss', 'tax-saving', 'sip', 'long-term'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / Mirae Asset AMC',
        'last_updated': 'October 2026'
    },
    {
        'id': 'quant-elss-tax-saver',
        'name': 'Quant ELSS Tax Saver Fund - Direct Plan',
        'short_name': 'Quant ELSS Tax Saver',
        'category': 'EQUITY_MUTUAL_FUNDS',
        'subcategory': 'ELSS Tax-Saving Fund',
        'provider': 'Quant Mutual Fund',
        'risk_level': 'Very High',
        'risk_rating': 5,
        'min_investment': 500,
        'min_sip': 500,
        'lock_in_years': 3,
        'benchmark': 'NIFTY 500 TRI',
        'expense_ratio': '0.71%',
        'current_rate_or_nav': '₹420.50',
        'historical_cagr': {'1y': 38.6, '3y': 24.2, '5y': 31.8, '10y': 21.5},
        'expected_annual_return': 17.0,
        'tax_treatment': 'Section 80C deduction up to ₹1.5 Lakh. LTCG taxed @ 12.5% above ₹1.25 Lakh.',
        'tax_benefit': 'Section 80C Tax Deduction',
        'liquidity': 'Mandatory 36-month statutory lock-in period.',
        'objective': 'Generate alpha and optimize Section 80C tax efficiency through quantitative macroeconomic momentum models.',
        'how_it_works': 'Active VLRT model dynamically adjusting sector weights across high-performing Indian equities.',
        'eligibility': 'Indian taxpayers.',
        'advantages': ['Category-leading 5Y CAGR (>31%)', 'Statutory tax savings under Section 80C', 'Aggressive compounding'],
        'disadvantages': ['Higher portfolio turnover and volatility than conservative ELSS peers'],
        'best_for_tags': ['elss', 'tax-saving', 'high-growth', 'sip'],
        'supports_sip': True,
        'supports_lumpsum': True,
        'data_source': 'AMFI / Quant AMC Disclosures',
        'last_updated': 'October 2026'
    },

    # =========================================================================
    # 3. GOLD
    # =========================================================================
    # =========================================================================
    # Gold ETFs
    {
        'id': 'nippon-gold-bees-etf',
        'name': 'Nippon India ETF Gold BeES (NSE: GOLDBEES)',
        'short_name': 'Gold BeES ETF',
        'ticker': 'GOLDBEES',
        'category': 'GOLD',
        'subcategory': 'Gold ETF',
        'provider': 'Nippon Life India AMC / NSE: GOLDBEES',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 68,
        'min_sip': 68,
        'lock_in_years': 0,
        'benchmark': 'Domestic Physical Gold Price (995 Purity)',
        'expense_ratio': '0.78%',
        'current_rate_or_nav': '₹68.40 per unit',
        'historical_cagr': {'1y': 27.2, '3y': 15.4, '5y': 13.9, '10y': 11.2},
        'expected_annual_return': 11.5,
        'tax_treatment': 'LTCG @ 12.5% for holding period > 12 months (Budget 2024 revised); STCG at slab rate if held < 12 months.',
        'tax_benefit': 'None',
        'liquidity': 'Highest liquidity among all commodity ETFs on NSE/BSE during market hours (9:15 AM - 3:30 PM).',
        'objective': 'Liquid, fractional investment in physical gold without locker storage, making charges, or purity testing worries.',
        'how_it_works': 'Each unit represents ~0.01 gram of 99.5% pure physical gold held in secure bank vaults audited by SEBI-appointed trustees.',
        'eligibility': 'Any investor with a Demat and Trading account.',
        'advantages': ['Start investing with as little as ~₹70', 'Zero locker rent, zero making charges, zero purity risk', 'Instant exchange liquidity and tight bid-ask spreads', 'Excellent equity hedge'],
        'disadvantages': ['Does not generate cash dividends or interest; returns derive purely from gold price movement'],
        'best_for_tags': ['gold', 'etf', 'inflation-hedge', 'beginners', 'defensive'],
        'data_source': 'National Stock Exchange (NSE) / Nippon India',
        'last_updated': 'October 2026'
    },
    {
        'id': 'hdfc-gold-etf',
        'name': 'HDFC Gold ETF (NSE: HDFCGOLD)',
        'short_name': 'HDFC Gold ETF',
        'ticker': 'HDFCGOLD',
        'category': 'GOLD',
        'subcategory': 'Gold ETF',
        'provider': 'HDFC Mutual Fund / NSE: HDFCGOLD',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 68,
        'min_sip': 68,
        'lock_in_years': 0,
        'benchmark': 'Domestic Spot Gold (995 Purity)',
        'expense_ratio': '0.59%',
        'current_rate_or_nav': '₹67.80 per unit',
        'historical_cagr': {'1y': 27.0, '3y': 15.2, '5y': 13.8, '10y': 11.1},
        'expected_annual_return': 11.5,
        'tax_treatment': 'LTCG @ 12.5% for holding > 12 months; STCG @ regular income slab.',
        'tax_benefit': 'None',
        'liquidity': 'T+1 liquid settlement on NSE and BSE.',
        'objective': 'Low-cost tracking of physical gold bullion prices with institutional safety backed by HDFC AMC.',
        'how_it_works': 'Units trade on exchange matching prevailing gold spot rates, backed 1:1 by physical bullion.',
        'eligibility': 'Demat account holders.',
        'advantages': ['Competitive expense ratio (0.59%)', 'HDFC institutional custodian security', 'Convenient fractional gold ownership'],
        'disadvantages': ['Requires Demat account and brokerage charges'],
        'best_for_tags': ['gold', 'etf', 'inflation-hedge', 'low-cost'],
        'data_source': 'National Stock Exchange (NSE) / HDFC AMC',
        'last_updated': 'October 2026'
    },
    {
        'id': 'sbi-gold-etf',
        'name': 'SBI Gold ETF (NSE: SETFGOLD)',
        'short_name': 'SBI Gold ETF',
        'ticker': 'SETFGOLD',
        'category': 'GOLD',
        'subcategory': 'Gold ETF',
        'provider': 'SBI Mutual Fund / NSE: SETFGOLD',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 68,
        'min_sip': 68,
        'lock_in_years': 0,
        'benchmark': 'Domestic Physical Gold Price',
        'expense_ratio': '0.65%',
        'current_rate_or_nav': '₹68.10 per unit',
        'historical_cagr': {'1y': 26.8, '3y': 15.1, '5y': 13.7, '10y': 11.0},
        'expected_annual_return': 11.5,
        'tax_treatment': 'LTCG @ 12.5% (> 12 months); STCG @ slab rate.',
        'tax_benefit': 'None',
        'liquidity': 'Traded on NSE and BSE.',
        'objective': 'Sovereign PSU institutional backing for exchange-traded gold accumulation.',
        'how_it_works': 'Secured by physical standard gold bars in audited custody vaults.',
        'eligibility': 'Demat account holders.',
        'advantages': ['SBI Group trust and governance', 'Zero physical theft risk', 'Intraday price transparency'],
        'disadvantages': ['Intraday price fluctuations dependent on international gold spot rates and USD/INR exchange rate'],
        'best_for_tags': ['gold', 'etf', 'inflation-hedge', 'safe-haven'],
        'data_source': 'NSE / SBI Mutual Fund',
        'last_updated': 'October 2026'
    },

    # Gold Mutual Funds (Fund of Funds investing in Gold ETFs)
    {
        'id': 'icici-pru-gold-savings',
        'name': 'ICICI Prudential Regular Gold Savings Fund - Direct Plan',
        'short_name': 'ICICI Gold Savings Fund',
        'category': 'GOLD',
        'subcategory': 'Gold Mutual Fund',
        'provider': 'ICICI Prudential Mutual Fund',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 1000,
        'min_sip': 100,
        'lock_in_years': 0,
        'benchmark': 'Domestic Price of Gold',
        'expense_ratio': '0.15% (Direct Plan FoF)',
        'current_rate_or_nav': '₹25.40',
        'historical_cagr': {'1y': 26.5, '3y': 14.8, '5y': 13.5, '10y': 10.8},
        'expected_annual_return': 11.2,
        'tax_treatment': 'LTCG @ 12.5% for holding > 12 months; STCG @ investor income slab rate.',
        'tax_benefit': 'None',
        'liquidity': 'High (T+2 redemption via AMC; 2% exit load within 15 days).',
        'objective': 'Invest in gold systematically through regular mutual fund SIP without needing a Demat or Trading account.',
        'how_it_works': 'Fund of Funds (FoF) that pools investor capital and invests 95%+ in ICICI Prudential Gold ETF units.',
        'eligibility': 'All individual investors with standard mutual fund KYC (No Demat needed).',
        'advantages': ['No Demat account needed', 'Micro-SIP starting at just ₹100/month', 'Automatic monthly bank auto-debit', 'Pure gold exposure'],
        'disadvantages': ['FoF adds minor additional layer of expense ratio (0.15%) above underlying ETF'],
        'best_for_tags': ['gold', 'gold-fund', 'sip', 'beginners', 'inflation-hedge'],
        'data_source': 'AMFI / ICICI Prudential AMC Factsheet',
        'last_updated': 'October 2026'
    },
    {
        'id': 'kotak-gold-fund',
        'name': 'Kotak Gold Fund - Direct Plan',
        'short_name': 'Kotak Gold Fund',
        'category': 'GOLD',
        'subcategory': 'Gold Mutual Fund',
        'provider': 'Kotak Mahindra Mutual Fund',
        'risk_level': 'Moderate',
        'risk_rating': 3,
        'min_investment': 1000,
        'min_sip': 100,
        'lock_in_years': 0,
        'benchmark': 'Price of Gold',
        'expense_ratio': '0.18% (Direct Plan FoF)',
        'current_rate_or_nav': '₹28.90',
        'historical_cagr': {'1y': 26.6, '3y': 14.9, '5y': 13.6, '10y': 10.9},
        'expected_annual_return': 11.2,
        'tax_treatment': 'LTCG @ 12.5% (> 12 months); STCG @ slab rate.',
        'tax_benefit': 'None',
        'liquidity': 'High (T+2 redemption; 2% exit load within 30 days).',
        'objective': 'Hassle-free automated gold savings via mutual fund mechanism with transparent daily NAV.',
        'how_it_works': 'Invests predominantly in Kotak Gold ETF units, reflecting domestic physical gold bullion values.',
        'eligibility': 'Resident individuals and HUFs (Demat not required).',
        'advantages': ['Zero demat account requirement', 'Flexible systematic SIP options from ₹100', 'Effective inflation and portfolio shock-absorber'],
        'disadvantages': ['Subject to commodity market fluctuations and currency movements'],
        'best_for_tags': ['gold', 'gold-fund', 'sip', 'inflation-hedge'],
        'data_source': 'AMFI / Kotak Mahindra AMC',
        'last_updated': 'October 2026'
    }
]

# Strict scheme alias map (maps any legacy queries to approved schemes)
SCHEME_ALIASES: Dict[str, str] = {
    'sip-uti-nifty-50': 'uti-nifty-50-index',
    'sip-parag-parikh-flexi-cap': 'parag-parikh-flexi-cap',
    'sip-sbi-bluechip': 'sbi-bluechip-fund',
    'sip-motilal-midcap': 'motilal-oswal-midcap',
    'sip-nippon-small-cap': 'nippon-india-small-cap',
    'sip-mirae-elss': 'mirae-asset-elss-tax-saver',
    'sbi-nifty-50-index': 'uti-nifty-50-index',
    'nippon-nifty-bees': 'uti-nifty-50-index',
    'gold-bees': 'nippon-gold-bees-etf'
}


def _enrich_scheme(s: Dict[str, Any]) -> Dict[str, Any]:
    """Return a scheme dict augmented with display properties, durations, and normalized tags."""
    item = dict(s)
    tags = list(item.get('best_for_tags', []))
    item['tags'] = tags
    item['best_for_tags'] = tags
    item['category_label'] = SCHEME_CATEGORIES.get(item['category'], {}).get('name', item['category'])
    item['min_investment_inr'] = item.get('min_investment', 500)
    item['min_investment_formatted'] = f"₹{item.get('min_investment', 0):,}"
    lock_years = item.get('lock_in_years', 0)
    item['lock_in'] = f"{lock_years} Years" if lock_years > 0 else 'None'

    cagrs = item.get('historical_cagr', {})
    item['cagr_1y'] = cagrs.get('1y')
    item['cagr_3y'] = cagrs.get('3y')
    item['cagr_5y'] = cagrs.get('5y')
    item['cagr_10y'] = cagrs.get('10y')
    item['current_interest_rate'] = item.get('expected_annual_return')

    # Standardized company_name
    if not item.get('company_name'):
        item['company_name'] = item.get('provider', '').split('/')[0].strip()

    # Standardized ticker
    if 'ticker' not in item:
        item['ticker'] = ''

    # Standardized investment_type
    cat = item.get('category')
    subcat = item.get('subcategory', '')
    if cat == 'STOCKS_EQUITY':
        item['investment_type'] = 'Individual Listed Stock'
    elif cat == 'EQUITY_MUTUAL_FUNDS':
        item['investment_type'] = f"Equity Mutual Fund ({subcat})"
    elif cat == 'GOLD':
        item['investment_type'] = subcat
    else:
        item['investment_type'] = subcat or 'Investment'

    # Numeric expense ratio percentage
    if 'expense_ratio_pct' not in item or item['expense_ratio_pct'] is None:
        raw_exp = str(item.get('expense_ratio', ''))
        import re
        m = re.search(r'([0-9]+\.?[0-9]*)%', raw_exp)
        if m and 'Direct Equity' not in raw_exp:
            item['expense_ratio_pct'] = float(m.group(1))
        elif 'Direct Equity' in raw_exp or cat == 'STOCKS_EQUITY':
            item['expense_ratio_pct'] = None
        else:
            item['expense_ratio_pct'] = None

    # Supported durations (SEBI/AMFI horizon suitability)
    if 'supported_durations' not in item:
        if cat == 'STOCKS_EQUITY':
            item['supported_durations'] = ['3_TO_5Y', '5_TO_10Y', 'MORE_THAN_10Y']
        elif cat == 'EQUITY_MUTUAL_FUNDS':
            if subcat in ['Mid-Cap Fund', 'Small-Cap Fund']:
                item['supported_durations'] = ['5_TO_10Y', 'MORE_THAN_10Y']
            else:
                item['supported_durations'] = ['3_TO_5Y', '5_TO_10Y', 'MORE_THAN_10Y']
        elif cat == 'GOLD':
            if 'ETF' in subcat:
                item['supported_durations'] = ['UP_TO_1Y', '1_TO_3Y', '3_TO_5Y', '5_TO_10Y', 'MORE_THAN_10Y']
            else:
                item['supported_durations'] = ['1_TO_3Y', '3_TO_5Y', '5_TO_10Y', 'MORE_THAN_10Y']
        else:
            item['supported_durations'] = ['3_TO_5Y', '5_TO_10Y']

    # SIP availability
    if item.get('supports_sip'):
        min_sip_val = item.get('min_sip', 500)
        item['sip_availability'] = f"Available from ₹{min_sip_val:,}/month"
    else:
        item['sip_availability'] = 'SIP not supported'

    return item


def get_all_schemes() -> List[Dict[str, Any]]:
    """Return all approved investment schemes in the database, fully enriched and deduplicated."""
    schemes_dict = {}
    for s in SCHEMES_DATABASE:
        resolved_id = SCHEME_ALIASES.get(s['id'], s['id'])
        if resolved_id not in schemes_dict:
            schemes_dict[resolved_id] = s
    return [_enrich_scheme(s) for s in schemes_dict.values()]


def get_scheme_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
    """Find an approved scheme by its unique identifier or alias."""
    resolved_id = SCHEME_ALIASES.get(scheme_id, scheme_id)
    for s in SCHEMES_DATABASE:
        if s['id'] == resolved_id or s['id'] == scheme_id:
            return _enrich_scheme(s)
    return None


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
    max_min_investment: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Filter schemes across approved discovery criteria with exact AND logic:
    1. Deduplicated product dataset
    2. Main tab selection
    3. Search query
    4. Compatible filters (Risk, Duration, Min Investment, Expense Ratio)
    5. Sorting (Relevance, Return, Expense, Name)
    """
    # Step 1: Base canonical dataset deduplicated by ID
    schemes_dict = {}
    for s in SCHEMES_DATABASE:
        resolved_id = SCHEME_ALIASES.get(s['id'], s['id'])
        if resolved_id not in schemes_dict:
            schemes_dict[resolved_id] = s
    results = list(schemes_dict.values())

    # Step 2: Main tab filtering
    if category and category.upper() != 'ALL':
        cat_upper = category.upper()
        if cat_upper in ['STOCKS', 'STOCK', 'STOCKS_EQUITY', 'STOCKS_ETFS']:
            results = [s for s in results if s['category'] == 'STOCKS_EQUITY']
        elif cat_upper in ['MUTUAL_FUNDS', 'EQUITY_MUTUAL_FUNDS', 'MF']:
            results = [s for s in results if s['category'] == 'EQUITY_MUTUAL_FUNDS']
        elif cat_upper in ['SIP', 'SIP_INVESTMENTS']:
            # Only eligible equity mutual funds that currently support SIP investments
            results = [s for s in results if s['category'] == 'EQUITY_MUTUAL_FUNDS' and s.get('supports_sip')]
        elif cat_upper in ['GOLD', 'GOLD_SILVER', 'GOLD_ETFS']:
            results = [s for s in results if s['category'] == 'GOLD']
        else:
            results = [s for s in results if s['category'].upper() == cat_upper]

    # Step 3: Search query (case-insensitive across name, company_name, ticker, subcategory)
    if query:
        q = query.strip().lower()
        results = [
            s for s in results
            if q in s.get('name', '').lower()
            or q in s.get('short_name', '').lower()
            or q in s.get('company_name', '').lower()
            or q in s.get('provider', '').lower()
            or q in s.get('ticker', '').lower()
            or q in s.get('subcategory', '').lower()
            or any(q in t.lower() for t in s.get('best_for_tags', []))
        ]

    # Step 4: Compatible Filters (AND Logic)
    # 4a. Risk Level
    if risk_level and risk_level.upper() != 'ALL':
        r_target = risk_level.strip().lower()
        def matches_risk(s):
            r = (s.get('risk_level') or '').strip().lower()
            if not r or r in ['not available', 'unknown', 'n/a']:
                return False
            if r_target == 'moderate':
                return 'moderate' in r
            return r == r_target
        results = [s for s in results if matches_risk(s)]

    # 4b. Investment Duration
    if duration and duration.upper() != 'ALL':
        d_target = duration.strip().upper()
        results = [
            s for s in results
            if d_target in _enrich_scheme(s).get('supported_durations', [])
        ]

    # 4c. Minimum Investment threshold
    min_inv_threshold = min_investment if min_investment is not None else max_min_investment
    if min_inv_threshold is not None and min_inv_threshold > 0:
        is_sip_tab = (category and category.upper() in ['SIP', 'SIP_INVESTMENTS'])
        def satisfies_min(s):
            threshold = float(min_inv_threshold)
            val = s.get('min_sip') if is_sip_tab else s.get('min_investment')
            return val is not None and val <= threshold
        results = [s for s in results if satisfies_min(s)]

    # 4d. Expense Ratio (Applicable to mutual funds and SIP-enabled mutual funds only; not stocks)
    if max_expense_ratio is not None and max_expense_ratio > 0:
        if not (category and category.upper() in ['STOCKS', 'STOCK', 'STOCKS_EQUITY']):
            enriched_temp = [_enrich_scheme(s) for s in results]
            valid_ids = {
                e['id'] for e in enriched_temp
                if e.get('category') != 'STOCKS_EQUITY'
                and e.get('expense_ratio_pct') is not None
                and e.get('expense_ratio_pct') <= float(max_expense_ratio)
            }
            results = [s for s in results if s['id'] in valid_ids]

    # 4e. Tag Filter
    if tag and tag.upper() != 'ALL':
        raw_tag = tag.lower().strip()
        tag_variants = {raw_tag, raw_tag.replace('_', '-'), raw_tag.replace('-', '_')}
        results = [
            s for s in results
            if any(t.lower() in tag_variants or t.lower().replace('-', '_') in tag_variants for t in s.get('best_for_tags', []))
        ]

    # Step 5: Enrich
    enriched = [_enrich_scheme(s) for s in results]

    # Step 6: Sorting
    period = (return_period or '5y').lower()
    cagr_key = f'cagr_{period}'

    if sort_by == 'return_desc':
        # Place products with unavailable returns after products with valid values
        enriched.sort(key=lambda x: (x.get(cagr_key) is not None, x.get(cagr_key) or 0.0), reverse=True)
    elif sort_by == 'expense_asc':
        # Lowest expense ratio; unavailable values after valid values
        enriched.sort(key=lambda x: (x.get('expense_ratio_pct') is None, x.get('expense_ratio_pct') if x.get('expense_ratio_pct') is not None else 999.0))
    elif sort_by == 'name_asc':
        enriched.sort(key=lambda x: x.get('name', '').lower())

    return enriched


def get_schemes_by_ids(scheme_ids: List[str]) -> List[Dict[str, Any]]:
    """Retrieve multiple schemes for side-by-side comparison."""
    results = []
    for sid in scheme_ids:
        s = get_scheme_by_id(sid)
        if s:
            results.append(s)
    return results
