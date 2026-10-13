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
    calculate_adaptive_budget_recommendation,
    BUDGET_PRESETS,
    CLASSIFICATION_LABELS
)
from app.services.money import to_minor_units

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/api/locations/countries', methods=['GET'])
def api_get_countries():
    """Returns supported countries list."""
    return jsonify({
        'success': True,
        'countries': get_supported_countries()
    })


@locations_bp.route('/api/locations/states', methods=['GET'])
def api_get_states():
    """Returns all 28 Indian States and 8 Union Territories."""
    return jsonify({
        'success': True,
        'states': get_all_states()
    })


@locations_bp.route('/api/locations/districts', methods=['GET'])
def api_get_districts():
    """Returns administrative districts for a given state ID."""
    state_id = request.args.get('state_id', '').strip()
    if not state_id:
        return jsonify({'success': False, 'error': 'state_id parameter is required.'}), 400

    districts = get_districts_for_state(state_id)
    return jsonify({
        'success': True,
        'state_id': state_id,
        'districts': districts
    })


@locations_bp.route('/api/locations/cities', methods=['GET'])
def api_get_cities():
    """
    Search cities for a state and optional district.
    Handles autocomplete, aliases, transliterations, and Tier classification.
    """
    state_id = request.args.get('state_id', '').strip()
    district_id = request.args.get('district_id', '').strip() or None
    query = request.args.get('q', '').strip() or None
    limit = int(request.args.get('limit', 50))

    if not state_id:
        return jsonify({'success': False, 'error': 'state_id parameter is required.'}), 400

    cities = search_cities_for_state(state_id, district_id=district_id, query=query, limit=limit)
    return jsonify({
        'success': True,
        'state_id': state_id,
        'district_id': district_id,
        'cities': cities
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
