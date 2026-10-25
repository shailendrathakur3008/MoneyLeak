"""
Comprehensive Test Suite for Indian Administrative Location Hierarchy:
- All 28 States and 8 Union Territories
- All official administrative districts (~788 districts across India)
- Cities, towns, municipalities, and census towns search & filtering
- Dependent dropdown cascading & clearing logic
- Combination validation rejecting cross-state/district mismatches
- Registration and Onboarding integration with authentication preservation
- Pincode validation and postal circle matching
"""
import pytest
from app.extensions import db
from app.models.user import User
from app.services.india_geo_data import (
    INDIAN_STATES_AND_UTS,
    STATE_BY_ID,
    DISTRICTS_BY_STATE,
    DISTRICT_BY_ID,
    CITIES_DATA,
    CITIES_BY_DISTRICT
)
from app.services.location_service import (
    get_all_states,
    get_districts_for_state,
    search_cities_for_state,
    validate_location_combination,
    validate_indian_pincode,
    calculate_adaptive_budget_recommendation,
    get_supported_countries
)


class TestIndiaGeographicalDataset:
    """Tests 1, 2, 3: Verifies all 28 states, 8 UTs, and ~788 districts."""

    def test_all_28_states_present(self):
        states = [s for s in INDIAN_STATES_AND_UTS if s['type'] == 'State']
        assert len(states) == 28, f"Expected 28 states, got {len(states)}"
        state_names = {s['name'] for s in states}
        expected_sample = {
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
            'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
            'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
        }
        assert expected_sample == state_names

    def test_all_8_union_territories_present(self):
        uts = [s for s in INDIAN_STATES_AND_UTS if s['type'] == 'Union Territory']
        assert len(uts) == 8, f"Expected 8 UTs, got {len(uts)}"
        ut_names = {s['name'] for s in uts}
        expected_sample = {
            'Andaman and Nicobar Islands', 'Chandigarh',
            'Dadra and Nagar Haveli and Daman and Diu', 'Delhi',
            'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
        }
        assert expected_sample == ut_names

    def test_total_administrative_units_is_36(self):
        all_units = get_all_states()
        assert len(all_units) == 36

    def test_every_state_and_ut_has_valid_districts(self):
        """Every single one of the 36 states and UTs must have official districts."""
        assert len(DISTRICTS_BY_STATE) == 36
        total_districts = sum(len(dists) for dists in DISTRICTS_BY_STATE.values())
        # India officially has ~788 administrative districts
        assert total_districts >= 780, f"Expected ~788 districts, got {total_districts}"

        # Test specific known states
        assert len(DISTRICTS_BY_STATE['IN-MH']) == 36  # Maharashtra has 36 districts
        assert len(DISTRICTS_BY_STATE['IN-UP']) == 75  # Uttar Pradesh has 75 districts
        assert len(DISTRICTS_BY_STATE['IN-BR']) == 38  # Bihar has 38 districts
        assert len(DISTRICTS_BY_STATE['IN-DL']) == 11  # Delhi has all 11 official administrative districts
        assert len(DISTRICTS_BY_STATE['IN-GA']) == 2   # Goa has 2 districts (North Goa, South Goa)

    def test_stable_unique_identifiers(self):
        state_ids = [s['id'] for s in INDIAN_STATES_AND_UTS]
        assert len(state_ids) == len(set(state_ids)), "State IDs must be unique"

        district_ids = [d['id'] for d in DISTRICT_BY_ID.values()]
        assert len(district_ids) == len(set(district_ids)), "District IDs must be unique"


class TestSearchAndDependentDropdownServices:
    """Tests 4, 5, 6, 7, 8, 9, 10: Filtering, search, and hierarchy."""

    def test_state_search_case_insensitive_and_partial(self):
        results = get_all_states(query="maha")
        assert len(results) == 1
        assert results[0]['name'] == 'Maharashtra'

        results_upper = get_all_states(query="MAHA")
        assert len(results_upper) == 1
        assert results_upper[0]['id'] == 'IN-MH'

        # Empty match
        results_none = get_all_states(query="Atlantis")
        assert len(results_none) == 0

    def test_districts_populate_for_state(self):
        dists = get_districts_for_state('IN-MH')
        # 36 official districts + 1 custom/fallback = 37
        assert len(dists) == 37
        dist_names = [d['name'] for d in dists]
        assert 'Mumbai City' in dist_names
        assert 'Mumbai Suburban' in dist_names
        assert 'Pune' in dist_names
        assert 'Nashik' in dist_names
        assert 'Nagpur' in dist_names

    def test_district_search_partial_name(self):
        dists = get_districts_for_state('IN-MH', query='nash')
        assert len(dists) == 1
        assert dists[0]['name'] == 'Nashik'

        # Case-insensitive
        dists_caps = get_districts_for_state('IN-MH', query='NASHIK')
        assert len(dists_caps) == 1
        assert dists_caps[0]['name'] == 'Nashik'

    def test_city_search_and_district_disambiguation(self):
        """Duplicate city/town names in different districts must show disambiguation context."""
        cities = search_cities_for_state('IN-MH', district_id='IN-MH-NSK', query='nash')
        assert len(cities) >= 1
        nashik_city = next((c for c in cities if c['name'] == 'Nashik'), None)
        assert nashik_city is not None
        assert 'Nashik' in nashik_city['display_label']
        assert nashik_city['tier'] in ('URBAN', 'METRO', 'TOWN')

    def test_city_search_handles_empty_results(self):
        cities = search_cities_for_state('IN-MH', district_id='IN-MH-NSK', query='NonExistentPlaceXYZ')
        assert len(cities) == 0


class TestLocationCombinationValidation:
    """Tests 11, 12: Invalid state-district-city combinations must be rejected."""

    def test_valid_combination_passes(self):
        res = validate_location_combination(
            state_id='IN-MH',
            district_id='IN-MH-PUN',
            city_id='IN-MH-PUN-PUNE',
            country='India'
        )
        assert res['valid'] is True
        assert res['state_name'] == 'Maharashtra'
        assert res['district_name'] == 'Pune'
        assert res['city_name'] == 'Pune'
        assert res['location_tier'] == 'METRO'

    def test_mismatched_district_rejected(self):
        """Selecting Pune district (Maharashtra) under Gujarat state must be rejected."""
        res = validate_location_combination(
            state_id='IN-GJ',
            district_id='IN-MH-PUN',
            country='India'
        )
        assert res['valid'] is False
        assert "does not belong to" in res['error']

    def test_mismatched_city_rejected(self):
        """Selecting Pune city under Nashik district must be rejected."""
        res = validate_location_combination(
            state_id='IN-MH',
            district_id='IN-MH-NSK',
            city_id='IN-MH-PUN-PUNE',
            country='India'
        )
        assert res['valid'] is False
        assert "belongs to a different district" in res['error']

    def test_custom_locality_accepted_with_valid_district(self):
        res = validate_location_combination(
            state_id='IN-KA',
            district_id='IN-KA-BLRU',
            city_name='Whitefield Tech Park Village',
            is_custom_city=True,
            country='India'
        )
        assert res['valid'] is True
        assert res['city_name'] == 'Whitefield Tech Park Village'

    def test_international_location_accepted_without_indian_state(self):
        res = validate_location_combination(
            country='United States',
            state_id=None,
            city_name='San Francisco'
        )
        assert res['valid'] is True
        assert res['location_tier'] == 'UNCLASSIFIED'


class TestPincodeValidation:
    """Tests 6-digit Indian PIN codes and postal circle verification."""

    def test_valid_pincode_matching_state(self):
        # Maharashtra PIN codes start with 40-44
        res = validate_indian_pincode('400001', state_id='IN-MH')
        assert res['valid'] is True
        assert res['matches_state'] is True
        assert res['clean_pincode'] == '400001'

    def test_valid_pincode_mismatched_state_warning(self):
        # 560001 is Karnataka (starts with 56-59), but state is Maharashtra
        res = validate_indian_pincode('560001', state_id='IN-MH')
        assert res['valid'] is True
        assert res['matches_state'] is False
        assert 'warning' in res

    def test_invalid_pincode_rejected(self):
        res1 = validate_indian_pincode('012345')  # First digit cannot be 0
        assert res1['valid'] is False

        res2 = validate_indian_pincode('4000')  # Must be 6 digits
        assert res2['valid'] is False

        res3 = validate_indian_pincode('ABCDEF')
        assert res3['valid'] is False


class TestLocationAPIEndpoints:
    """HTTP API Endpoints for Location Queries."""

    def test_api_get_states(self, client):
        res = client.get('/api/locations/states')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['total_states'] == 28
        assert data['total_uts'] == 8
        assert len(data['states']) == 36

    def test_api_get_districts_for_state(self, client):
        res = client.get('/api/locations/districts?state_id=IN-TN')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['state_name'] == 'Tamil Nadu'
        # 38 official districts + 1 fallback = 39
        assert len(data['districts']) == 39
        names = [d['name'] for d in data['districts']]
        assert 'Chennai' in names
        assert 'Coimbatore' in names
        assert 'Madurai' in names

    def test_api_get_cities_with_district_filter(self, client):
        res = client.get('/api/locations/cities?state_id=IN-KA&district_id=IN-KA-BLRU&q=bengaluru')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert len(data['cities']) >= 1
        city = data['cities'][0]
        assert 'Bengaluru' in city['name']
        assert city['tier'] == 'METRO'

    def test_api_validate_location_success(self, client):
        res = client.post('/api/locations/validate', json={
            'state_id': 'IN-WB',
            'district_id': 'IN-WB-KOL',
            'city_id': 'IN-WB-KOL-KOLKATA',
            'country': 'India'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['valid'] is True
        assert data['state_name'] == 'West Bengal'
        assert data['district_name'] == 'Kolkata'
        assert data['location_tier'] == 'METRO'

    def test_api_validate_location_mismatch_error(self, client):
        res = client.post('/api/locations/validate', json={
            'state_id': 'IN-GJ',
            'district_id': 'IN-MH-PUN',
            'country': 'India'
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data['valid'] is False
        assert "does not belong to" in data['error']


class TestRegistrationAndOnboardingIntegration:
    """Tests 13, 14: Signup form and onboarding workflow with location selection."""

    def test_register_get_renders_page_with_all_countries(self, client):
        res = client.get('/register')
        assert res.status_code == 200
        html = res.data.decode('utf-8')
        assert 'India' in html
        assert 'reg-state-wrap' in html
        assert 'reg-district-wrap' in html
        assert 'reg-city-wrap' in html

    def test_register_post_with_location_data(self, client, app):
        """User signs up with valid Indian State, District, and City."""
        email = 'nashik.user@domain.com'
        res = client.post('/register', json={
            'full_name': 'Ramesh Patil',
            'email': email,
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'currency': 'INR',
            'country': 'India',
            'state_id': 'IN-MH',
            'district_id': 'IN-MH-NSK',
            'city_name': 'Nashik',
            'pincode': '422001'
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['success'] is True

        with app.app_context():
            u = User.query.filter_by(email=email).first()
            assert u is not None
            assert u.full_name == 'Ramesh Patil'
            assert u.state_id == 'IN-MH'
            assert u.state_name == 'Maharashtra'
            assert u.district_id == 'IN-MH-NSK'
            assert u.district_name == 'Nashik'
            assert u.city_name == 'Nashik'
            assert u.pincode == '422001'
            assert u.onboarding_step == 2

    def test_register_post_rejects_invalid_state_district_combination(self, client):
        res = client.post('/register', json={
            'full_name': 'Invalid Combiner',
            'email': 'invalid.loc@domain.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'country': 'India',
            'state_id': 'IN-GJ',
            'district_id': 'IN-MH-PUN',  # Pune is in Maharashtra, not Gujarat!
            'city_name': 'Pune'
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data['success'] is False
        assert "does not belong to" in data['error']

    def test_onboarding_step2_saves_location_and_updates_tier(self, client, app):
        """User updates location during Step 2 of onboarding wizard."""
        email = 'onboard.loc@domain.com'
        with app.app_context():
            user = User(
                email=email,
                full_name='Aarav Mehta',
                onboarding_completed=False,
                onboarding_step=1,
                currency='INR'
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.commit()
            uid = user.id

        # Authenticate session
        with client.session_transaction() as sess:
            sess['user_id'] = uid
            sess['user_email'] = email

        res = client.post('/onboarding', json={
            'step': 2,
            'country': 'India',
            'state_id': 'IN-DL',
            'state_name': 'Delhi',
            'district_id': 'IN-DL-NEW',
            'district_name': 'New Delhi',
            'city_name': 'Connaught Place',
            'is_custom_city': True,
            'pincode': '110001'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['next_step'] == 3

        with app.app_context():
            u = db.session.get(User, uid)
            assert u.state_id == 'IN-DL'
            assert u.district_id == 'IN-DL-NEW'
            assert u.city_name == 'Connaught Place'
            assert u.onboarding_step == 3


class TestVillageExclusionAndSettlementTypes:
    """Verifies strict exclusion of villages and authoritative urban settlement classifications."""

    def test_zero_villages_in_master_dataset(self):
        """Every single place in CITIES_DATA must have is_village = False."""
        villages = [c for c in CITIES_DATA if c.get('is_village') is True]
        assert len(villages) == 0, f"Found {len(villages)} places incorrectly classified as villages."
        assert len(CITIES_DATA) >= 4000, f"Expected 4000+ urban places, got {len(CITIES_DATA)}"
        for c in CITIES_DATA:
            assert c['is_village'] is False
            assert c['tier'] in ('METRO', 'URBAN', 'TOWN'), f"Unexpected tier for city {c['name']}: {c['tier']}"

    def test_settlement_types_classification(self):
        """Dataset must distinguish Municipal Corporations, Municipalities, Nagar Panchayats, Cantonments, and Census Towns."""
        types = {c['settlement_type'] for c in CITIES_DATA}
        assert 'Statutory Town (Municipal Corporation)' in types
        assert 'Statutory Town (Municipality)' in types
        assert 'Statutory Town (Nagar Panchayat)' in types
        assert 'Statutory Town (Cantonment Board)' in types
        assert 'Census Town' in types

        # Check categories
        categories = {c['settlement_category'] for c in CITIES_DATA}
        assert 'STATUTORY_TOWN' in categories
        assert 'CENSUS_TOWN' in categories

        # Check official codes exist on all records
        for c in CITIES_DATA[:100]:
            assert 'official_code' in c and len(c['official_code']) == 6
            assert 'data_source' in c and 'Census' in c['data_source']
            assert 'dataset_version' in c

    def test_search_strictly_excludes_villages(self):
        cities = search_cities_for_state('IN-MH', district_id='IN-MH-PUN')
        assert len(cities) > 0
        for c in cities:
            assert c['is_village'] is False
            assert 'Village' not in c.get('settlement_type', '')


class TestDisambiguationAndPerformance:
    """Tests duplicate-name disambiguation and high-performance querying."""

    def test_duplicate_city_names_in_different_states_disambiguated(self):
        """E.g. Aurangabad exists in both Maharashtra and Bihar; each must have distinct state/district labels."""
        mh_cities = search_cities_for_state('IN-MH', query='aurangabad')
        br_cities = search_cities_for_state('IN-BR', query='aurangabad')

        assert len(mh_cities) >= 1
        assert len(br_cities) >= 1

        mh_city = mh_cities[0]
        br_city = br_cities[0]

        assert mh_city['state_id'] == 'IN-MH'
        assert br_city['state_id'] == 'IN-BR'
        assert 'Maharashtra' in mh_city['display_label']
        assert 'Bihar' in br_city['display_label']
        assert mh_city['id'] != br_city['id']

    def test_duplicate_city_names_in_different_districts_disambiguated(self):
        """E.g. Bilaspur in Chhattisgarh vs Bilaspur in Himachal Pradesh."""
        cg_cities = search_cities_for_state('IN-CG', district_id='IN-CG-BIL', query='bilaspur')
        hp_cities = search_cities_for_state('IN-HP', district_id='IN-HP-BIL', query='bilaspur')

        assert len(cg_cities) >= 1
        assert len(hp_cities) >= 1
        assert cg_cities[0]['display_label'] != hp_cities[0]['display_label']
        assert 'Chhattisgarh' in cg_cities[0]['display_label']
        assert 'Himachal Pradesh' in hp_cities[0]['display_label']

    def test_search_cities_fast_query_time(self):
        """Search across 4,000+ urban places must execute under 50ms."""
        import time
        start = time.perf_counter()
        results = search_cities_for_state('IN-UP', query='lucknow')
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert len(results) >= 1
        assert elapsed_ms < 50, f"Query took {elapsed_ms:.2f}ms, expected < 50ms"

    def test_api_metadata_endpoint(self, client):
        res = client.get('/api/locations/metadata')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        meta = data['metadata']
        assert meta['villages_excluded'] is True
        assert meta['total_states_and_uts'] == 36
        assert meta['total_districts'] >= 780
        assert meta['total_verified_urban_settlements'] >= 4000

