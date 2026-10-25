"""
Comprehensive Tests for MoneyLeak Market Data Service & Verified Investment Data:
1. Stock quote parser & live/delayed status check (NSE/BSE via Yahoo Finance chart API)
2. Official AMFI Mutual Fund NAV retrieval, AMC extraction, and scheme code matching
3. Gold composite rates (Gold ETF live price, Physical 24K spot + 3% GST breakdown, Gold MF, SGB)
4. Centralized scheme enrichment (symbols, freshness status, day change, risk methodology)
5. Evidence-based risk methodology & regulatory disclosure sources
6. Actual historical time series retrieval & sampling
7. Historical What-If backtesting (OFFICIAL_HISTORICAL_SERIES vs VERIFIED_CAGR_MODEL)
8. API endpoints (/api/tools/market-data/<id>, /api/tools/gold-rates, /api/tools/sip-backtest)
9. Caching, rate-limiting resilience, and graceful baseline fallbacks
"""
import pytest
from app import create_app
from app.services.market_data_service import market_data_service, VERIFIED_INSTRUMENTS
from app.services.scheme_data import get_scheme_by_id, get_all_schemes
from app.services.historical_engine import calculate_what_if_investment


def test_verified_instruments_catalogue_coverage():
    """Verify core Indian instruments across sectors are mapped with official symbols and baselines."""
    assert len(VERIFIED_INSTRUMENTS) >= 30, f"Expected >= 30 verified mappings, got {len(VERIFIED_INSTRUMENTS)}"

    # Check key stocks
    for stock_id in ['reliance-industries', 'tata-consultancy-services', 'hdfc-bank', 'infosys']:
        assert stock_id in VERIFIED_INSTRUMENTS
        meta = VERIFIED_INSTRUMENTS[stock_id]
        assert meta['exchange_symbol'].endswith('.NS')
        assert meta['baseline_price'] > 0
        assert 'risk_methodology' in meta
        assert 'risk_source' in meta

    # Check key mutual funds
    for mf_id in ['parag-parikh-flexi-cap', 'uti-nifty-50-index', 'mirae-asset-large-cap', 'sbi-bluechip-fund']:
        assert mf_id in VERIFIED_INSTRUMENTS
        meta = VERIFIED_INSTRUMENTS[mf_id]
        assert meta['amfi_code'].isdigit()
        assert 'Direct' in meta['plan_type']
        assert meta['option'] == 'Growth'
        assert meta['baseline_nav'] > 0
        assert 'AMFI' in meta['risk_source'] or 'SEBI' in meta['risk_source'] or 'Riskometer' in meta['risk_source']

    # Check gold
    assert 'nippon-gold-bees-etf' in VERIFIED_INSTRUMENTS
    assert 'sovereign-gold-bonds' in VERIFIED_INSTRUMENTS
    assert 'physical-gold-24k' in VERIFIED_INSTRUMENTS


def test_stock_quote_retrieval_and_structure():
    """Test get_stock_quote returns valid quote structure or graceful baseline with proper status."""
    quote = market_data_service.get_stock_quote('RELIANCE.NS')

    assert isinstance(quote, dict)
    assert 'price' in quote
    assert quote['price'] > 500  # Reliance trades well above 500
    assert 'currency' in quote and quote['currency'] == 'INR'
    assert 'freshness' in quote
    assert quote['freshness'] in ['LIVE', 'LAST_TRADED', 'CACHED_BASELINE']
    assert 'source' in quote
    assert 'day_change' in quote


def test_stock_quote_fallback_on_invalid_symbol():
    """Test fallback when an invalid or unreachable symbol is requested."""
    bad_quote = market_data_service.get_stock_quote('INVALID_NON_EXISTENT_TICKER.ZZ')
    assert isinstance(bad_quote, dict)
    assert bad_quote['price'] > 0
    assert bad_quote['freshness'] == 'CACHED_BASELINE'
    assert bad_quote['is_fallback'] is True


def test_amfi_mutual_fund_nav_retrieval():
    """Test official AMFI NAV retrieval for Parag Parikh Flexi Cap (code: 122639)."""
    nav_data = market_data_service.get_mutual_fund_nav('122639')

    assert isinstance(nav_data, dict)
    assert nav_data['nav'] > 40.0  # PPFCF NAV is well above 40
    assert nav_data['amfi_code'] == '122639'
    assert 'nav_date' in nav_data
    assert nav_data['freshness'] in ['OFFICIAL_AMFI_NAV', 'CACHED_BASELINE']
    assert 'AMFI' in nav_data['source'] or 'Mutual Funds' in nav_data['source']


def test_amfi_fallback_on_invalid_code():
    """Test mutual fund fallback on invalid code."""
    bad_mf = market_data_service.get_mutual_fund_nav('9999999999')
    assert isinstance(bad_mf, dict)
    assert bad_mf['nav'] > 0
    assert bad_mf['freshness'] in ['END_OF_DAY_BASELINE', 'CACHED_BASELINE']
    assert bad_mf['is_fallback'] is True


def test_gold_market_data_four_forms():
    """Test composite gold rates across ETF, 24K Physical Spot + 3% GST, Mutual Fund, and SGB."""
    gold_data = market_data_service.get_gold_market_data()

    assert 'gold_etf' in gold_data
    assert 'physical_gold' in gold_data
    assert 'gold_mutual_fund' in gold_data
    assert 'sovereign_gold_bond' in gold_data

    # 1. Gold ETF
    etf = gold_data['gold_etf']
    assert etf['market_price'] > 40.0
    assert 'GOLDBEES' in etf['symbol']
    assert 'freshness' in etf

    # 2. Physical 24K Gold with statutory 3% GST
    phys = gold_data['physical_gold']
    assert '24 Karat' in phys['name'] or 'Bullion' in phys['purity']
    assert phys['spot_rate_per_gram'] > 5000
    assert phys['gst_pct'] == 3.0
    expected_total = round(phys['spot_rate_per_gram'] * 1.03, 2)
    assert abs(phys['total_rate_with_gst'] - expected_total) < 0.1
    assert 'IBJA' in phys['source']

    # 3. Gold Mutual Fund
    mf = gold_data['gold_mutual_fund']
    assert '119608' in mf['symbol']
    assert mf['nav'] > 5.0

    # 4. SGB
    sgb = gold_data['sovereign_gold_bond']
    assert '2.50%' in sgb['annual_interest_rate']
    assert sgb['tenor_years'] == 8
    assert 'exempt' in sgb['tax_treatment'].lower()


def test_scheme_enrichment():
    """Test scheme_data _enrich_scheme integrates verified market data without altering base catalog."""
    scheme = get_scheme_by_id('parag-parikh-flexi-cap')
    assert scheme is not None

    # Check enriched fields
    assert 'currentNAV' in scheme or 'currentPrice' in scheme
    assert scheme.get('price_numeric') is not None and scheme['price_numeric'] > 0
    assert 'freshness_status' in scheme
    assert 'official_symbol' in scheme and '122639' in scheme['official_symbol']
    assert 'risk_methodology' in scheme
    assert 'risk_classification_source' in scheme
    assert 'Direct' in scheme.get('plan_type', '')
    assert 'Growth' in scheme.get('option', '')


def test_evidence_based_risk_methodologies():
    """Verify evidence-based risk methodology is distinct from investment category and properly cited."""
    # Stock
    reliance = get_scheme_by_id('reliance-industries')
    assert 'Large-Cap' in reliance['risk_methodology'] or 'Beta' in reliance['risk_methodology']
    assert 'Exchange' in reliance['risk_classification_source'] or 'Stock' in reliance['risk_classification_source']

    # Mutual Fund
    ppfc = get_scheme_by_id('parag-parikh-flexi-cap')
    assert 'Riskometer' in ppfc['risk_methodology']
    assert 'SEBI' in ppfc['risk_classification_source'] or 'AMFI' in ppfc['risk_classification_source']

    # Fixed Deposit
    sbi_fd = get_scheme_by_id('sbi-fixed-deposit-term')
    assert sbi_fd is not None
    assert 'DICGC' in sbi_fd['capitalProtection'] or sbi_fd['riskLevel'] == 'Low'

    # Government Scheme
    ppf = get_scheme_by_id('public-provident-fund')
    assert ppf is not None
    assert 'Sovereign' in ppf['capitalProtection'] or ppf['riskLevel'] == 'Low'


def test_historical_time_series_retrieval():
    """Test get_historical_time_series retrieves actual AMFI series for supported fund."""
    result = market_data_service.get_historical_time_series('parag-parikh-flexi-cap', years=3)

    assert isinstance(result, dict)
    assert 'series' in result
    series = result['series']
    assert isinstance(series, list)
    assert len(series) >= 2, f"Expected at least 2 points in 3Y series, got {len(series)}"
    # First point must have a date and price
    assert 'date' in series[0] and 'price' in series[0]
    assert series[0]['price'] > 0 and series[-1]['price'] > 0


def test_what_if_calculation_basis_flag():
    """Test calculate_what_if_investment flags calculation_basis accurately."""
    # Supported mutual fund with actual historical NAV series
    res_mf = calculate_what_if_investment(
        scheme_id='parag-parikh-flexi-cap',
        amount=50000.0,
        duration_years=5,
        method='LUMPSUM'
    )
    assert res_mf['summary']['calculation_basis'] == 'OFFICIAL_HISTORICAL_SERIES'
    assert res_mf['summary']['data_source'] is not None

    # Fixed deposit / contractual scheme without daily open-market NAV series
    res_fd = calculate_what_if_investment(
        scheme_id='sbi-fixed-deposit-term',
        amount=50000.0,
        duration_years=5,
        method='LUMPSUM'
    )
    assert res_fd['summary']['calculation_basis'] == 'VERIFIED_CAGR_MODEL'


def test_api_market_data_endpoint(client, test_user):
    """Test GET /api/tools/market-data/<instrument_id>."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    resp = client.get('/api/tools/market-data/reliance-industries')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['instrument_id'] == 'reliance-industries'
    assert 'freshness_status' in data


def test_api_gold_rates_endpoint(client, test_user):
    """Test GET /api/tools/gold-rates."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    resp = client.get('/api/tools/gold-rates')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'gold' in data
    assert 'physical_gold' in data['gold']
    assert 'gold_etf' in data['gold']
    assert data['gold']['physical_gold']['gst_pct'] == 3.0


def test_api_sip_backtest_endpoint(client, test_user):
    """Test POST /api/tools/sip-backtest."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    resp = client.post('/api/tools/sip-backtest', json={
        'scheme_id': 'parag-parikh-flexi-cap',
        'monthly_amount': 5000,
        'duration_years': 3
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'result' in data
    summary = data['result']['summary']
    assert summary['original_investment'] == 5000 * 36
    assert summary['current_value'] > 0
    assert summary['calculation_basis'] == 'OFFICIAL_HISTORICAL_SERIES'
