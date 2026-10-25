"""
API endpoints for Indian administrative location selector, PIN validation,
and regional cost-of-living budget recommendation engine.
"""

from flask import Blueprint, request, jsonify, g
from app.extensions import csrf
from app.services.location_service import (
    get_supported_countries,
    get_all_states,
    get_districts_for_state,
    search_cities_for_state,
    validate_indian_pincode,
    validate_location_combination,
    calculate_adaptive_budget_recommendation,
    get_dataset_metadata,
    BUDGET_PRESETS,
    CLASSIFICATION_LABELS
)
from app.services.money import to_minor_units

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/api/locations/metadata', methods=['GET'])
def api_get_metadata():
    """Returns official geographical dataset metadata, version, and urban coverage."""
    return jsonify({
        'success': True,
        'metadata': get_dataset_metadata()
    })


@locations_bp.route('/api/locations/countries', methods=['GET'])
def api_get_countries():
    """Returns supported countries list."""
    return jsonify({
        'success': True,
        'countries': get_supported_countries()
    })


@locations_bp.route('/api/locations/states', methods=['GET'])
def api_get_states():
    """Returns all 28 Indian States and 8 Union Territories with optional search."""
    query = request.args.get('q', '').strip() or None
    states = get_all_states(query=query)
    total_states = sum(1 for s in states if s.get('type') == 'State')
    total_uts = sum(1 for s in states if s.get('type') == 'Union Territory')
    return jsonify({
        'success': True,
        'states': states,
        'total': len(states),
        'total_states': total_states,
        'total_uts': total_uts
    })


@locations_bp.route('/api/locations/districts', methods=['GET'])
def api_get_districts():
    """Returns administrative districts for a given state ID with optional search."""
    state_id = request.args.get('state_id', '').strip()
    query = request.args.get('q', '').strip() or None
    if not state_id:
        return jsonify({'success': False, 'error': 'state_id parameter is required.'}), 400

    from app.services.location_service import STATE_BY_ID
    state_obj = STATE_BY_ID.get(state_id)
    state_name = state_obj.get('name') if state_obj else state_id

    districts = get_districts_for_state(state_id, query=query)
    return jsonify({
        'success': True,
        'state_id': state_id,
        'state_name': state_name,
        'districts': districts,
        'total': len(districts)
    })


@locations_bp.route('/api/locations/cities', methods=['GET'])
def api_get_cities():
    """
    Search recognized cities and statutory/census towns for a state and optional district.
    Strictly excludes villages.
    Handles autocomplete, aliases, transliterations, duplicate disambiguation, and Tier classification.
    """
    state_id = request.args.get('state_id', '').strip()
    district_id = request.args.get('district_id', '').strip() or None
    query = request.args.get('q', '').strip() or None
    limit = int(request.args.get('limit', 100))

    if not state_id:
        return jsonify({'success': False, 'error': 'state_id parameter is required.'}), 400

    cities = search_cities_for_state(state_id, district_id=district_id, query=query, limit=limit)
    return jsonify({
        'success': True,
        'state_id': state_id,
        'district_id': district_id,
        'cities': cities,
        'total': len(cities),
        'villages_excluded': True,
        'dataset_version': get_dataset_metadata().get('dataset_version')
    })


@locations_bp.route('/api/locations/validate-pincode', methods=['GET'])
def api_validate_pincode():
    """Validates 6-digit Indian PIN code and checks postal circle alignment with state."""
    pincode = request.args.get('pincode', '').strip()
    state_id = request.args.get('state_id', '').strip() or None

    res = validate_indian_pincode(pincode, state_id=state_id)
    return jsonify({
        'success': res.get('valid', False),
        **res
    })


@locations_bp.route('/api/locations/recommend-budget', methods=['POST'])
@csrf.exempt
def api_recommend_budget():
    """
    Calculates India-adaptive 50/30/20 budget recommendations based on
    location tier classification and user's actual contractual household commitments.
    """
    data = request.get_json() or {}
    tier = (data.get('location_tier') or 'UNCLASSIFIED').strip()
    currency = (data.get('currency') or 'INR').strip().upper()

    income_val = data.get('monthly_income', 0)
    rent_val = data.get('rent_or_emi', 0)
    essentials_val = data.get('essential_expenses', 0)
    debt_val = data.get('debt_payments', 0)
    dependants = int(data.get('dependants', 0) or 0)

    income_minor = to_minor_units(income_val, currency) if income_val else 0
    rent_minor = to_minor_units(rent_val, currency) if rent_val else 0
    essentials_minor = to_minor_units(essentials_val, currency) if essentials_val else 0
    debt_minor = to_minor_units(debt_val, currency) if debt_val else 0

    recommendation = calculate_adaptive_budget_recommendation(
        location_tier=tier,
        monthly_income_minor=income_minor,
        rent_minor=rent_minor,
        essentials_minor=essentials_minor,
        debt_minor=debt_minor,
        dependants_count=dependants,
        currency=currency
    )

    return jsonify({
        'success': True,
        'recommendation': recommendation
    })


@locations_bp.route('/api/locations/validate', methods=['POST'])
@csrf.exempt
def api_validate_location():
    """
    Validates hierarchical geographical dependency:
    Country -> State/UT -> District -> City/Town.
    Rejects invalid cross-state or cross-district combinations.
    """
    data = request.get_json() or {}
    state_id = data.get('state_id')
    district_id = data.get('district_id')
    city_id = data.get('city_id')
    is_custom_city = bool(data.get('is_custom_city', False))
    city_name = data.get('city_name')
    country = data.get('country') or 'India'

    result = validate_location_combination(
        state_id=state_id,
        district_id=district_id,
        city_id=city_id,
        is_custom_city=is_custom_city,
        city_name=city_name,
        country=country
    )
    status_code = 200 if result.get('valid') else 400
    return jsonify({'success': result.get('valid', False), **result}), status_code
