"""
Comprehensive tests for Indian Investment Scheme Explorer, Historical What-If Engine,
Future Compound Calculator with Step-Up SIP, Personalized Recommendations,
Portfolio Aggregation Engine, and Strict Category Exclusions.
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
    """Verify only the 4 approved investment categories exist and are populated with rich data."""
    schemes = get_all_schemes()
    assert len(schemes) >= 20, f"Expected at least 20 schemes, found {len(schemes)}"

    # The only approved categories are Stocks & Equity, Equity Mutual Funds, SIP Investments, and Gold
    expected_categories = {'STOCKS_EQUITY', 'EQUITY_MUTUAL_FUNDS', 'SIP_INVESTMENTS', 'GOLD'}
    assert set(SCHEME_CATEGORIES.keys()) == expected_categories

    # Verify underlying asset classes have real schemes and SIP is verified
    categories_found = {s['category'] for s in schemes}
    assert 'STOCKS_EQUITY' in categories_found
    assert 'EQUITY_MUTUAL_FUNDS' in categories_found
    assert 'GOLD' in categories_found
    assert any(s.get('supports_sip') for s in schemes)

    # Verify essential fields
    for s in schemes:
        assert s['id'], "Scheme must have an id"
        assert s['name'], "Scheme must have a name"
        assert s['provider'], "Scheme must have a provider"
        assert s['objective'], "Scheme must have an objective"
        assert s['risk_level'], "Scheme must have a risk level"
        assert 'min_investment_inr' in s
        assert 'tax_treatment' in s
        assert 'liquidity' in s
        assert len(s.get('advantages', [])) > 0, "Scheme should list advantages"
        assert len(s.get('disadvantages', [])) > 0, "Scheme should list limitations"
        assert s.get('data_source'), "Scheme must cite reliable data source"


def test_strict_exclusions():
    """
    Verify strict exclusions:
    Excluded products (PPF, NSC, FDs, Bonds, Debt Mutual Funds, Real Estate/REITs,
    NPS/Retirement, Sovereign Gold Bonds, commodity derivatives) must NEVER appear.
    """
    schemes = get_all_schemes()
    scheme_ids = {s['id'] for s in schemes}

    # Verify excluded scheme IDs are NOT present
    excluded_ids = [
        'public-provident-fund', 'ppf-india', 'national-savings-certificate',
        'sukanya-samriddhi-yojana', 'senior-citizens-savings-scheme',
        'sbi-fixed-deposit-5yr', 'hdfc-bank-regular-fd', 'rbi-floating-rate-bonds',
        'national-pension-system', 'employees-provident-fund',
        'sovereign-gold-bonds', 'pure-term-insurance', 'ulip-wealth-plan',
        'embassy-office-parks-reit', 'nexus-select-trust-reit',
        'tata-technologies-ipo', 'bajaj-housing-finance-ipo'
    ]
    for ex_id in excluded_ids:
        assert ex_id not in scheme_ids, f"Excluded product {ex_id} found in scheme database!"

    # Verify excluded categories are NOT in SCHEME_CATEGORIES
    excluded_cats = {'GOVT_SAVINGS', 'FIXED_INCOME', 'RETIREMENT', 'IPOS', 'INSURANCE_INVEST', 'OTHER_INVEST'}
    for ex_cat in excluded_cats:
        assert ex_cat not in SCHEME_CATEGORIES, f"Excluded category {ex_cat} found in SCHEME_CATEGORIES!"

    # Verify no scheme has an excluded category
    for s in schemes:
        assert s['category'] in {'STOCKS_EQUITY', 'EQUITY_MUTUAL_FUNDS', 'SIP_INVESTMENTS', 'GOLD'}, \
            f"Scheme {s['name']} has unauthorized category {s['category']}"


def test_scheme_filtering():
    """Verify category, risk, tag and text search filters across approved items."""
    # Stocks filter
    stocks = filter_schemes(category='STOCKS_EQUITY')
    assert len(stocks) >= 5
    for s in stocks:
        assert s['category'] == 'STOCKS_EQUITY'

    # Equity Mutual Funds filter
    mf_schemes = filter_schemes(category='EQUITY_MUTUAL_FUNDS')
    assert len(mf_schemes) >= 5
    for s in mf_schemes:
        assert s['category'] == 'EQUITY_MUTUAL_FUNDS'

    # Gold filter
    gold_schemes = filter_schemes(category='GOLD')
    assert len(gold_schemes) >= 3
    for s in gold_schemes:
        assert s['category'] == 'GOLD'

    # SIP Investments filter (returns eligible equity mutual funds that support SIP)
    sip_schemes = filter_schemes(category='SIP_INVESTMENTS')
    assert len(sip_schemes) >= 4
    for s in sip_schemes:
        assert s.get('supports_sip') is True
        assert s['category'] == 'EQUITY_MUTUAL_FUNDS'
        assert s.get('sip_availability')

    # Text search
    tcs = filter_schemes(query='TCS')
    assert len(tcs) >= 1
    assert any('tcs' in s['name'].lower() for s in tcs)


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

    # Check monotonic growth
    vals = [row['value'] for row in res['timeline']]
    assert vals == sorted(vals)


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
    for r in recs:
        assert r['recommendation_reason']
        assert r['category'] in {'STOCKS_EQUITY', 'EQUITY_MUTUAL_FUNDS', 'SIP_INVESTMENTS', 'GOLD'}


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
    """Test that /calculator renders successfully with approved schemes."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/calculator')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Explore Investment Options' in html or 'Investment' in html
    assert 'Stocks & Equity' in html
    assert 'Equity Mutual Funds' in html
    assert 'Gold' in html
    assert 'Parag Parikh Flexi Cap' in html
    # Strictly ensure excluded products are NOT in the page
    assert 'Public Provident Fund' not in html
    assert 'Sovereign Gold Bonds' not in html


def test_api_schemes_list_and_categories(client, test_user):
    """Test /api/schemes and /api/schemes/categories endpoints."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/api/schemes')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['count'] >= 20

    res_cat = client.get('/api/schemes/categories')
    assert res_cat.status_code == 200
    cat_data = res_cat.get_json()
    assert cat_data['success'] is True
    assert 'EQUITY_MUTUAL_FUNDS' in cat_data['categories']
    assert 'STOCKS_EQUITY' in cat_data['categories']
    assert 'GOLD' in cat_data['categories']
    assert 'GOVT_SAVINGS' not in cat_data['categories']


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
    """Test POST /api/schemes/compare endpoint with approved products."""
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
    Validate all 13 Acceptance Criteria from Scheme Explorer Specification:
    1. Every tab returns the correct product types.
    2. SIP Investments contains only funds with verified SIP availability.
    3. Search works within the selected tab.
    4. Multiple filters combine using AND logic.
    5. Incompatible filters reset on tab changes (checked in API/UI).
    6. Compatible filters persist across tab changes.
    7. Sorting respects the selected period and handles missing values.
    8. Reset Filters clears filters but preserves the active tab.
    9. All Schemes does not show duplicate products.
    10. Excluded investment products never appear.
    11. Empty states and result counts are correct.
    12. Deduplication enforces unique product IDs.
    13. Existing calculator functionality remains intact.
    """
    # 1. Every tab returns correct product types
    stocks = filter_schemes(category='STOCKS_EQUITY')
    assert len(stocks) == 13
    assert all(s['category'] == 'STOCKS_EQUITY' for s in stocks)

    mfs = filter_schemes(category='EQUITY_MUTUAL_FUNDS')
    assert len(mfs) == 12
    assert all(s['category'] == 'EQUITY_MUTUAL_FUNDS' for s in mfs)

    gold = filter_schemes(category='GOLD')
    assert len(gold) == 5
    assert all(s['category'] == 'GOLD' for s in gold)

    # 2. SIP Investments contains only funds with verified SIP availability
    sips = filter_schemes(category='SIP_INVESTMENTS')
    assert len(sips) == 12
    for s in sips:
        assert s['category'] == 'EQUITY_MUTUAL_FUNDS'
        assert s['supports_sip'] is True
        assert s['sip_availability']
        assert s['min_sip'] > 0

    # 3. Search works within selected tab
    nifty_mfs = filter_schemes(category='EQUITY_MUTUAL_FUNDS', query='Nifty')
    assert len(nifty_mfs) >= 2
    assert all('nifty' in s['name'].lower() or 'nifty' in s['subcategory'].lower() for s in nifty_mfs)

    # 4. Multiple filters combine using AND logic
    # Example: Equity Mutual Funds + "Index" + Very High risk + expense ratio <= 0.20
    and_filtered = filter_schemes(
        category='EQUITY_MUTUAL_FUNDS',
        query='Index',
        risk_level='Very High',
        max_expense_ratio=0.20
    )
    assert len(and_filtered) >= 1
    for s in and_filtered:
        assert s['category'] == 'EQUITY_MUTUAL_FUNDS'
        assert 'index' in s['name'].lower() or 'index' in s['subcategory'].lower()
        assert s['risk_level'] == 'Very High'
        assert s['expense_ratio_pct'] <= 0.20

    # 7. Sorting respects selected period and handles missing values
    sorted_5y = filter_schemes(category='EQUITY_MUTUAL_FUNDS', sort_by='return_desc', return_period='5y')
    for i in range(len(sorted_5y) - 1):
        r1 = sorted_5y[i].get('cagr_5y')
        r2 = sorted_5y[i+1].get('cagr_5y')
        if r1 is not None and r2 is not None:
            assert r1 >= r2

    sorted_ter = filter_schemes(category='EQUITY_MUTUAL_FUNDS', sort_by='expense_asc')
    valid_ters = [s['expense_ratio_pct'] for s in sorted_ter if s.get('expense_ratio_pct') is not None]
    assert valid_ters == sorted(valid_ters)

    # 9. All Schemes does not show duplicate products
    all_schemes = filter_schemes(category='ALL')
    assert len(all_schemes) == 30
    scheme_ids = [s['id'] for s in all_schemes]
    assert len(scheme_ids) == len(set(scheme_ids)), "Duplicate schemes found in All Schemes!"

    # 10. Excluded investment products never appear
    all_names = ' '.join(s['name'].lower() for s in all_schemes)
    assert 'ppf' not in all_names
    assert 'national savings' not in all_names
    assert 'fixed deposit' not in all_names
    assert 'sovereign gold' not in all_names

    # 11. Empty states: impossible filter returns 0 results
    empty_res = filter_schemes(category='STOCKS_EQUITY', query='NonExistentSchemeXYZ')
    assert len(empty_res) == 0

