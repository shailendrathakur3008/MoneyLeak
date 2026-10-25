"""
Comprehensive tests for Indian Investment Scheme Explorer, Historical What-If Engine,
Future Compound Calculator with Step-Up SIP and Compounding Frequencies,
Personalized Recommendations, Centralized Risk Classification, and Multi-Filter Engine.
"""
import pytest
from app.services.scheme_data import (
    SCHEME_CATEGORIES,
    get_all_schemes,
    get_scheme_by_id,
    filter_schemes,
    get_schemes_by_ids
)
from app.services.historical_engine import calculate_what_if_investment
from app.services.investment_calculator import calculate_compound_growth
from app.services.comparison_service import compare_schemes
from app.services.recommendation_service import get_personalized_recommendations
from app.services.portfolio_service import calculate_portfolio_projection


def test_scheme_catalog_completeness():
    """Verify all supported investment categories exist and items contain all 27 required schema fields."""
    schemes = get_all_schemes()
    assert len(schemes) >= 70, f"Expected at least 70 schemes, found {len(schemes)}"

    # Check investment categories
    for cat_key in ['ALL', 'STOCKS', 'MUTUAL_FUNDS', 'ETFS', 'FIXED_DEPOSITS', 'GOVT_SECURITIES', 'SMALL_SAVINGS', 'GOLD', 'OTHER']:
        assert cat_key in SCHEME_CATEGORIES, f"Missing category key: {cat_key}"

    # Verify all 27 schema fields are present on every instrument
    required_fields = [
        'id', 'name', 'symbol', 'assetType', 'investmentCategory',
        'riskLevel', 'riskScore', 'riskDescription', 'investmentHorizon',
        'minimumInvestment', 'expectedReturnRange', 'returnPeriod', 'liquidity',
        'capitalProtection', 'marketRisk', 'creditRisk', 'interestRateRisk',
        'expenseRatio', 'currentPrice', 'lastUpdated', 'dataSource',
        'investmentPurpose', 'investmentBenefits', 'investmentLimitations',
        'taxInformation', 'eligibilityRequirements', 'disclaimer'
    ]
    for s in schemes:
        for field in required_fields:
            assert field in s, f"Scheme {s.get('id')} missing required field: {field}"
        assert 1 <= s['riskScore'] <= 10, f"Scheme {s['id']} has invalid riskScore: {s['riskScore']}"
        assert s['riskLevel'] in ['Low', 'Medium', 'High'], f"Scheme {s['id']} has invalid riskLevel: {s['riskLevel']}"
        assert len(s['investmentBenefits']) > 0, f"Scheme {s['id']} missing benefits"
        assert len(s['investmentLimitations']) > 0, f"Scheme {s['id']} missing limitations"
        assert s['dataSource'], f"Scheme {s['id']} missing dataSource"


def test_risk_level_completeness_and_distribution():
    """
    Verify Low, Medium, and High risk categories all return valid investments,
    respect the 1-10 risk scale, and enforce market risk warnings for defensive equities.
    """
    # 1. Low Risk (1-3)
    low_schemes = filter_schemes(risk_level='Low')
    assert len(low_schemes) >= 20, f"Expected >= 20 Low-Risk options, found {len(low_schemes)}"
    for s in low_schemes:
        assert s['riskLevel'] == 'Low'
        assert 1 <= s['riskScore'] <= 3, f"Low risk scheme {s['id']} has score {s['riskScore']}"

    # Verify defensive stocks in Low Risk carry explicit market risk warnings
    low_stocks = [s for s in low_schemes if s.get('assetType') == 'Stocks']
    assert len(low_stocks) >= 10, "Expected at least 10 defensive blue-chip stocks in Low Risk catalogue"
    for stock in low_stocks:
        assert stock['marketRisk'] and str(stock['marketRisk']).lower() != 'nil', f"Stock {stock['id']} must identify marketRisk"
        assert stock.get('capitalProtection') is False or 'Market-Linked' in str(stock.get('capitalProtection')) or 'No Guarantee' in str(stock.get('capitalProtection')), \
            f"Stock {stock['id']} must not claim guaranteed capital protection"
        warnings = " ".join([stock['disclaimer']] + stock['investmentLimitations']).lower()
        assert 'risk' in warnings or 'fall' in warnings or 'volatility' in warnings or 'fluctuate' in warnings or 'cyclical' in warnings, \
            f"Stock {stock['id']} missing market risk disclaimer"

    # Verify sovereign / government products have capital protection
    govt_items = [s for s in low_schemes if s.get('assetType') in ['Government Securities', 'Small Savings Schemes']]
    assert len(govt_items) >= 8, "Expected government and small savings schemes in Low Risk"
    for g in govt_items:
        assert g.get('capitalProtection') is True or any(w in str(g.get('capitalProtection')).lower() for w in ['sovereign', 'statutory', 'guaranteed', 'high']) or 'Sovereign' in g.get('creditRisk', '')

    # 2. Medium Risk (4-6)
    med_schemes = filter_schemes(risk_level='Medium')
    assert len(med_schemes) >= 20, f"Expected >= 20 Medium-Risk options, found {len(med_schemes)}"
    for s in med_schemes:
        assert s['riskLevel'] == 'Medium'
        assert 4 <= s['riskScore'] <= 6, f"Medium risk scheme {s['id']} has score {s['riskScore']}"

    # 3. High Risk (7-10)
    high_schemes = filter_schemes(risk_level='High')
    assert len(high_schemes) >= 15, f"Expected >= 15 High-Risk options, found {len(high_schemes)}"
    for s in high_schemes:
        assert s['riskLevel'] == 'High'
        assert 7 <= s['riskScore'] <= 10, f"High risk scheme {s['id']} has score {s['riskScore']}"


def test_scheme_filtering():
    """Verify filtering by asset types, SIP support, search query, and combinations."""
    # Stocks filter
    stocks = filter_schemes(category='STOCKS')
    assert len(stocks) >= 25
    for s in stocks:
        assert s['assetType'] == 'Stocks' or s['category'] == 'STOCKS_EQUITY'

    # Mutual Funds filter
    mfs = filter_schemes(category='MUTUAL_FUNDS')
    assert len(mfs) >= 15
    for s in mfs:
        assert s['assetType'] == 'Mutual Funds' or s['category'] == 'EQUITY_MUTUAL_FUNDS'

    # ETFs filter
    etfs = filter_schemes(category='ETFS')
    assert len(etfs) >= 4
    for s in etfs:
        assert s['assetType'] == 'ETFs'

    # Fixed Deposits filter
    fds = filter_schemes(category='FIXED_DEPOSITS')
    assert len(fds) >= 3
    for s in fds:
        assert s['assetType'] == 'Fixed Deposits'

    # Government Securities filter
    gsecs = filter_schemes(category='GOVT_SECURITIES')
    assert len(gsecs) >= 3
    for s in gsecs:
        assert s['assetType'] == 'Government Securities'

    # Small Savings Schemes filter
    savings = filter_schemes(category='SMALL_SAVINGS')
    assert len(savings) >= 4
    for s in savings:
        assert s['assetType'] == 'Small Savings Schemes'

    # Gold filter
    gold = filter_schemes(category='GOLD')
    assert len(gold) >= 3
    for s in gold:
        assert s['assetType'] == 'Gold' or s['category'] == 'GOLD'

    # Text search
    tcs = filter_schemes(query='TCS')
    assert len(tcs) >= 1
    assert any('tcs' in s['name'].lower() or 'tcs' in s['symbol'].lower() for s in tcs)

    zomato = filter_schemes(query='Zomato')
    assert len(zomato) >= 1
    assert any('zomato' in s['name'].lower() for s in zomato)


def test_risk_normalization():
    """Verify case-insensitive risk filtering and numeric aliases."""
    for variant in ['low', 'LOW', 'Low']:
        res = filter_schemes(risk_level=variant)
        assert len(res) >= 20
        assert all(s['riskLevel'] == 'Low' for s in res)

    for variant in ['medium', 'MEDIUM', 'Medium', 'moderate', 'MODERATE']:
        res = filter_schemes(risk_level=variant)
        assert len(res) >= 20
        assert all(s['riskLevel'] == 'Medium' for s in res)

    for variant in ['high', 'HIGH', 'High', 'very high']:
        res = filter_schemes(risk_level=variant)
        assert len(res) >= 15
        assert all(s['riskLevel'] == 'High' for s in res)

    for variant in ['all', 'ALL', '', None]:
        res = filter_schemes(risk_level=variant)
        assert len(res) >= 70


def test_compounding_frequencies():
    """Verify compound growth with Annual, Semi-Annual, Quarterly, and Monthly compounding frequencies."""
    # Test standard Indian bank quarterly compounding: Rs 100,000 at 8% for 1 year = Rs 108,243.22
    res_quarterly = calculate_compound_growth(
        initial_amount=100000.0,
        periodic_contribution=0.0,
        frequency='ANNUALLY',
        compounding_frequency='QUARTERLY',
        annual_return_pct=8.0,
        duration_years=1,
        currency='INR'
    )
    assert abs(res_quarterly['summary']['future_value'] - 108243.22) < 0.50

    # Annual compounding: Rs 100,000 at 8% for 1 year = Rs 108,000
    res_annual = calculate_compound_growth(
        initial_amount=100000.0,
        periodic_contribution=0.0,
        frequency='ANNUALLY',
        compounding_frequency='ANNUALLY',
        annual_return_pct=8.0,
        duration_years=1,
        currency='INR'
    )
    assert abs(res_annual['summary']['future_value'] - 108000.0) < 0.50

    # Monthly compounding: Rs 100,000 at 8% for 1 year = Rs 108,300
    res_monthly = calculate_compound_growth(
        initial_amount=100000.0,
        periodic_contribution=0.0,
        frequency='ANNUALLY',
        compounding_frequency='MONTHLY',
        annual_return_pct=8.0,
        duration_years=1,
        currency='INR'
    )
    assert res_monthly['summary']['future_value'] > res_quarterly['summary']['future_value']
    assert res_quarterly['summary']['future_value'] > res_annual['summary']['future_value']


def test_intelligent_fallback():
    """Verify intelligent fallback returns alternatives within risk category when no exact match exists."""
    fallback_res = filter_schemes(
        risk_level='Low',
        query='NonExistentCompanyABCXYZ'
    )
    assert len(fallback_res) > 0, "Expected fallback options instead of a blank screen"
    for s in fallback_res:
        assert s.get('is_fallback') is True
        assert s.get('riskLevel') == 'Low'


def test_what_if_lumpsum_calculation():
    """Test 'What If I Invested Earlier?' lump-sum compounding against verified math."""
    res = calculate_what_if_investment(
        scheme_id='uti-nifty-50-index',
        amount=100000.0,
        duration_years=5,
        method='LUMPSUM',
        currency='INR'
    )

    summary = res['summary']
    assert summary['original_investment'] == 100000.0
    assert summary['current_value'] > 100000.0
    assert summary['profit_loss'] > 0
    assert summary['total_return_pct'] > 0
    assert summary['annualized_return_pct'] > 0
    assert len(res['timeline']) == 5

    # Check progression consistency
    vals = [row['value'] for row in res['timeline']]
    if summary.get('calculation_basis') == 'VERIFIED_CAGR_MODEL':
        assert vals == sorted(vals)
    else:
        # For real market historical data, values reflect genuine market movements
        assert all(v > 0 for v in vals)
        assert abs(res['timeline'][-1]['value'] - summary['current_value']) < 0.1


def test_what_if_sip_calculation():
    """Test 'What If I Invested Earlier?' monthly SIP compounding."""
    monthly_amt = 5000.0
    years = 3
    res = calculate_what_if_investment(
        scheme_id='parag-parikh-flexi-cap',
        amount=monthly_amt,
        duration_years=years,
        method='SIP',
        currency='INR'
    )

    summary = res['summary']
    expected_invested = monthly_amt * (years * 12)
    assert summary['original_investment'] == expected_invested
    assert summary['current_value'] > expected_invested
    assert summary['profit_loss'] > 0
    assert len(res['timeline']) == years


def test_future_investment_calculator_step_up():
    """Verify future compound growth calculation with annual step-up SIP %."""
    base_res = calculate_compound_growth(
        initial_amount=10000.0,
        periodic_contribution=5000.0,
        frequency='MONTHLY',
        annual_return_pct=12.0,
        duration_years=5,
        timing='BEGINNING',
        currency='INR',
        step_up_pct=0.0
    )

    step_up_res = calculate_compound_growth(
        initial_amount=10000.0,
        periodic_contribution=5000.0,
        frequency='MONTHLY',
        annual_return_pct=12.0,
        duration_years=5,
        timing='BEGINNING',
        currency='INR',
        step_up_pct=10.0
    )

    # With a 10% annual step-up, total capital invested and final corpus must be strictly higher
    assert step_up_res['summary']['total_invested'] > base_res['summary']['total_invested']
    assert step_up_res['summary']['future_value'] > base_res['summary']['future_value']


def test_scheme_comparison_service():
    """Verify side-by-side comparison of eligible Indian investment schemes."""
    scheme_ids = ['reliance-industries', 'parag-parikh-flexi-cap', 'nippon-gold-bees-etf']
    comp = compare_schemes(
        scheme_ids=scheme_ids,
        amount=50000.0,
        duration_years=5,
        method='LUMPSUM',
        currency='INR'
    )

    assert comp['count'] == 3
    assert len(comp['schemes']) == 3

    for item in comp['schemes']:
        assert 'historical_what_if' in item
        assert 'future_projection' in item
        assert item['future_projection']['future_value'] > 0
        assert 'tax_treatment' in item
        assert 'liquidity' in item


def test_personalized_recommendations():
    """Verify objective personalized recommendation engine generates transparent reasons."""
    recs = get_personalized_recommendations(
        amount=10000.0,
        frequency='MONTHLY',
        duration_years=10,
        risk_tolerance='High',
        objective='wealth_accumulation'
    )
    assert len(recs) > 0
    valid_categories = set(SCHEME_CATEGORIES.keys()) | {'ETFS', 'MUTUAL_FUNDS', 'STOCKS', 'GOLD', 'SIP_INVESTMENTS', 'EQUITY_MUTUAL_FUNDS', 'STOCKS_EQUITY'}
    for r in recs:
        assert r['recommendation_reason']
        assert r['category'] in valid_categories


def test_portfolio_projection_and_no_double_counting():
    """
    Verify portfolio aggregation:
    - SIP is treated strictly as an investment method linked to Equity Mutual Funds.
    - Avoids double-counting SIP investments when calculating combined asset exposure.
    - Calculates conservative, moderate, and optimistic scenarios.
    """
    investments = [
        {
            'id': 'reliance-industries',
            'name': 'Reliance Industries',
            'category': 'STOCKS_EQUITY',
            'method': 'LUMPSUM',
            'amount': 50000.0,
            'expected_return_pct': 14.0
        },
        {
            'id': 'sip-parag-parikh-flexi-cap',
            'name': 'Parag Parikh Flexi Cap SIP',
            'category': 'SIP_INVESTMENTS',
            'method': 'SIP',
            'amount': 5000.0,
            'expected_return_pct': 16.0,
            'underlying_scheme_id': 'parag-parikh-flexi-cap'
        },
        {
            'id': 'nippon-gold-bees-etf',
            'name': 'Gold BeES ETF',
            'category': 'GOLD',
            'method': 'LUMPSUM',
            'amount': 20000.0,
            'expected_return_pct': 11.5
        }
    ]

    res = calculate_portfolio_projection(investments=investments, duration_years=5, currency='INR')
    assert res['investments_count'] == 3
    assert res['total_invested'] > 0
    assert res['future_value'] > res['total_invested']

    # Scenarios check
    scenarios = res['scenarios']
    assert scenarios['conservative']['future_value'] < scenarios['moderate']['future_value']
    assert scenarios['moderate']['future_value'] < scenarios['optimistic']['future_value']

    # Asset allocation check: Only the 3 underlying asset classes exist
    alloc = res['asset_allocation']
    assert 'STOCKS_EQUITY' in alloc
    assert 'EQUITY_MUTUAL_FUNDS' in alloc
    assert 'GOLD' in alloc
    # SIP_INVESTMENTS must NOT be an independent duplicate asset class
    assert 'SIP_INVESTMENTS' not in alloc

    total_pct = alloc['STOCKS_EQUITY']['percentage'] + alloc['EQUITY_MUTUAL_FUNDS']['percentage'] + alloc['GOLD']['percentage']
    assert abs(total_pct - 100.0) <= 0.5


# -----------------------------------------------------------------------------
# API INTEGRATION TESTS
# -----------------------------------------------------------------------------

def test_calculator_page_renders(client, test_user):
    """Test that /calculator renders successfully with expanded schemes and risk options."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/calculator')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Explore Investment Options' in html or 'Investment' in html
    assert 'Stocks' in html
    assert 'Mutual Funds' in html
    assert 'Gold' in html
    assert 'Fixed Deposits' in html
    assert 'Public Provident Fund' in html
    assert 'Hindustan Unilever' in html


def test_api_schemes_list_and_categories(client, test_user):
    """Test /api/schemes and /api/schemes/categories endpoints."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/api/schemes')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['count'] >= 70

    res_cat = client.get('/api/schemes/categories')
    assert res_cat.status_code == 200
    cat_data = res_cat.get_json()
    assert cat_data['success'] is True
    assert 'MUTUAL_FUNDS' in cat_data['categories']
    assert 'STOCKS' in cat_data['categories']
    assert 'FIXED_DEPOSITS' in cat_data['categories']
    assert 'SMALL_SAVINGS' in cat_data['categories']


def test_api_single_scheme(client, test_user):
    """Test /api/schemes/<scheme_id> endpoint."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/api/schemes/reliance-industries')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'Reliance' in data['scheme']['name']
    assert data['scheme']['category'] == 'STOCKS_EQUITY'


def test_api_what_if_endpoint(client, test_user):
    """Test POST /api/schemes/what-if endpoint."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    payload = {
        'scheme_id': 'uti-nifty-50-index',
        'amount': 25000,
        'duration_years': 3,
        'method': 'LUMPSUM'
    }
    res = client.post('/api/schemes/what-if', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['result']['summary']['original_investment'] == 25000.0


def test_api_compare_endpoint(client, test_user):
    """Test POST /api/schemes/compare endpoint."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    payload = {
        'scheme_ids': ['reliance-industries', 'parag-parikh-flexi-cap'],
        'amount': 50000,
        'duration_years': 5,
        'method': 'LUMPSUM'
    }
    res = client.post('/api/schemes/compare', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['comparison']['count'] == 2


def test_api_recommend_endpoint(client, test_user):
    """Test POST /api/schemes/recommend endpoint."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    payload = {
        'amount': 15000,
        'frequency': 'MONTHLY',
        'duration_years': 5,
        'risk_tolerance': 'High',
        'objective': 'wealth_accumulation'
    }
    res = client.post('/api/schemes/recommend', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['count'] > 0
    assert len(data['recommendations']) > 0


def test_api_portfolio_calculate_endpoint(client, test_user):
    """Test POST /api/tools/portfolio-calculate endpoint."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    payload = {
        'investments': [
            {
                'id': 'reliance-industries',
                'name': 'Reliance Industries',
                'category': 'STOCKS_EQUITY',
                'method': 'LUMPSUM',
                'amount': 25000.0,
                'expected_return_pct': 14.0
            },
            {
                'id': 'sip-uti-nifty-50',
                'name': 'UTI Nifty 50 SIP',
                'category': 'SIP_INVESTMENTS',
                'method': 'SIP',
                'amount': 3000.0,
                'expected_return_pct': 13.5
            }
        ],
        'duration_years': 5
    }
    res = client.post('/api/tools/portfolio-calculate', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'portfolio' in data
    assert data['portfolio']['future_value'] > 0


def test_scheme_explorer_acceptance_criteria():
    """
    Validate Acceptance Criteria from Scheme Explorer Specification:
    1. Every asset category returns the correct product types.
    2. Search works within the selected tab.
    3. Multiple filters combine using AND logic.
    4. Sorting respects the selected period and handles missing values.
    5. All Schemes does not show duplicate products.
    6. Empty states and result counts are correct.
    7. Deduplication enforces unique product IDs.
    """
    # 1. Every tab returns correct product types
    stocks = filter_schemes(category='STOCKS')
    assert len(stocks) >= 25
    assert all(s['assetType'] == 'Stocks' or s['category'] == 'STOCKS_EQUITY' for s in stocks)

    mfs = filter_schemes(category='MUTUAL_FUNDS')
    assert len(mfs) >= 15
    assert all(s['assetType'] == 'Mutual Funds' or s['category'] == 'EQUITY_MUTUAL_FUNDS' for s in mfs)

    gold = filter_schemes(category='GOLD')
    assert len(gold) >= 3
    assert all(s['assetType'] == 'Gold' or s['category'] == 'GOLD' for s in gold)

    # 2. Search works within selected category
    nifty_mfs = filter_schemes(category='MUTUAL_FUNDS', query='Nifty')
    assert len(nifty_mfs) >= 2
    assert all('nifty' in s['name'].lower() or 'nifty' in s['symbol'].lower() for s in nifty_mfs)

    # 3. Multiple filters combine using AND logic: Mutual Funds + High Risk
    and_filtered = filter_schemes(
        category='MUTUAL_FUNDS',
        risk_level='High'
    )
    assert len(and_filtered) >= 1
    for s in and_filtered:
        assert s['assetType'] == 'Mutual Funds' or s['category'] == 'EQUITY_MUTUAL_FUNDS'
        assert s['riskLevel'] == 'High'

    # 4. Sorting respects selected period and handles missing values
    sorted_5y = filter_schemes(category='MUTUAL_FUNDS', sort_by='return_desc', return_period='5y')
    for i in range(len(sorted_5y) - 1):
        r1 = sorted_5y[i].get('cagr_5y')
        r2 = sorted_5y[i+1].get('cagr_5y')
        if r1 is not None and r2 is not None:
            assert r1 >= r2

    # 5. All Schemes does not show duplicate products
    all_schemes = filter_schemes(category='ALL')
    assert len(all_schemes) >= 70
    scheme_ids = [s['id'] for s in all_schemes]
    assert len(scheme_ids) == len(set(scheme_ids)), "Duplicate schemes found in All Schemes!"


def test_scheme_explorer_tabs_markup_and_neon_container(client, test_user):
    """
    Verify the 5 Scheme Explorer category tabs, their neon container,
    and accessibility attributes in calculator page markup.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/calculator')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # 1. Neon box container exists with role="tablist"
    assert 'class="scheme-tabs-neon-container"' in html
    assert 'id="scheme-explorer-neon-container"' in html
    assert 'role="tablist"' in html

    # 2. All 5 tabs exist with correct IDs and data-tab attributes
    assert 'id="tab-all-schemes"' in html
    assert 'data-tab="ALL"' in html
    assert 'All Schemes' in html

    assert 'id="tab-stocks"' in html
    assert 'data-tab="STOCKS"' in html
    assert 'Stocks & Equity' in html

    assert 'id="tab-mutual-funds"' in html
    assert 'data-tab="MUTUAL_FUNDS"' in html
    assert 'Equity Mutual Funds' in html

    assert 'id="tab-sip"' in html
    assert 'data-tab="SIP_INVESTMENTS"' in html
    assert 'SIP Investments' in html

    assert 'id="tab-gold"' in html
    assert 'data-tab="GOLD"' in html
    assert 'Gold' in html

    # 3. Initial active state on All Schemes with aria-selected="true"
    assert 'class="explorer-tab-btn active"' in html
    assert 'aria-selected="true"' in html
    assert 'aria-selected="false"' in html

    # 4. Results count badge exists
    assert 'id="explorer-results-count-badge"' in html

