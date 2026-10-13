"""
Financial Tools, Investment Explorer & Advanced Calculator routes.
Supports 9 Indian investment categories, 'What If I Invested Earlier?' historical engine,
side-by-side scheme comparison, and curated best scheme filters.
"""
from flask import Blueprint, render_template, request, jsonify, g
from app.routes.auth import login_required
from app.services.investment_calculator import calculate_compound_growth
from app.services.scheme_data import (
    SCHEME_CATEGORIES,
    get_all_schemes,
    get_scheme_by_id,
    filter_schemes,
    get_schemes_by_ids
)
from app.services.historical_engine import calculate_what_if_investment
from app.services.comparison_service import compare_schemes
from app.services.recommendation_service import get_personalized_recommendations
from app.services.portfolio_service import calculate_portfolio_projection

tools_bp = Blueprint('tools', __name__)


@tools_bp.route('/calculator')
@login_required
def view_calculator():
    user = g.current_user
    default_calc = calculate_compound_growth(
        initial_amount=10000.0,
        periodic_contribution=5000.0,
        frequency='MONTHLY',
        annual_return_pct=12.0,
        duration_years=10,
        timing='BEGINNING',
        currency=user.currency,
        step_up_pct=0.0
    )

    all_schemes = get_all_schemes()
    categories = SCHEME_CATEGORIES

    # Default What-If Calculation on Parag Parikh Flexi Cap for 5 years
    default_what_if = calculate_what_if_investment(
        scheme_id='parag-parikh-flexi-cap',
        amount=50000.0,
        duration_years=5,
        method='LUMPSUM',
        currency=user.currency
    )

    # Initial personalized recommendations
    initial_recs = get_personalized_recommendations(
        amount=10000.0,
        frequency='MONTHLY',
        duration_years=5,
        risk_tolerance='High',
        objective='wealth_accumulation'
    )

    return render_template(
        'investment_calculator.html',
        user=user,
        default_calc=default_calc,
        default_what_if=default_what_if,
        schemes=all_schemes,
        categories=categories,
        initial_recommendations=initial_recs
    )


# -----------------------------------------------------------------------------
# REST API: SCHEMES & EXPLORER
# -----------------------------------------------------------------------------

@tools_bp.route('/api/schemes', methods=['GET'])
@login_required
def api_get_schemes():
    category = request.args.get('category')
    risk = request.args.get('risk')
    tag = request.args.get('tag')
    query = request.args.get('q')
    duration = request.args.get('duration')
    min_inv = request.args.get('min_investment', type=float)
    max_ter = request.args.get('max_expense_ratio', type=float)
    sort_by = request.args.get('sort_by')
    period = request.args.get('period')

    filtered = filter_schemes(
        category=category,
        risk_level=risk,
        duration=duration,
        min_investment=min_inv,
        max_expense_ratio=max_ter,
        tag=tag,
        query=query,
        sort_by=sort_by,
        return_period=period
    )
    return jsonify({
        'success': True,
        'count': len(filtered),
        'schemes': filtered
    })


@tools_bp.route('/api/schemes/categories', methods=['GET'])
@login_required
def api_get_categories():
    counts = {}
    for s in get_all_schemes():
        cat = s['category']
        counts[cat] = counts.get(cat, 0) + 1

    cats_with_counts = {}
    for key, val in SCHEME_CATEGORIES.items():
        cats_with_counts[key] = {
            **val,
            'count': counts.get(key, 0)
        }

    return jsonify({
        'success': True,
        'categories': cats_with_counts
    })


@tools_bp.route('/api/schemes/<scheme_id>', methods=['GET'])
@login_required
def api_get_single_scheme(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        return jsonify({'success': False, 'error': 'Scheme not found.'}), 404
    return jsonify({'success': True, 'scheme': scheme})


# -----------------------------------------------------------------------------
# REST API: "WHAT IF I INVESTED EARLIER?"
# -----------------------------------------------------------------------------

@tools_bp.route('/api/schemes/what-if', methods=['POST'])
@login_required
def api_what_if_invested():
    user = g.current_user
    data = request.get_json() or {}

    scheme_id = data.get('scheme_id', 'sbi-nifty-50-index')
    try:
        amount = float(data.get('amount', 50000))
        duration_years = int(data.get('duration_years', 5))
        method = (data.get('method') or 'LUMPSUM').upper()

        result = calculate_what_if_investment(
            scheme_id=scheme_id,
            amount=amount,
            duration_years=duration_years,
            method=method,
            currency=user.currency
        )
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# -----------------------------------------------------------------------------
# REST API: SIDE-BY-SIDE SCHEME COMPARISON
# -----------------------------------------------------------------------------

@tools_bp.route('/api/schemes/compare', methods=['POST'])
@login_required
def api_compare_schemes():
    user = g.current_user
    data = request.get_json() or {}

    scheme_ids = data.get('scheme_ids', [])
    if not scheme_ids or not isinstance(scheme_ids, list):
        return jsonify({'success': False, 'error': 'Select at least 2 schemes to compare.'}), 400

    try:
        amount = float(data.get('amount', 50000))
        duration_years = int(data.get('duration_years', 5))
        method = (data.get('method') or 'LUMPSUM').upper()

        result = compare_schemes(
            scheme_ids=scheme_ids,
            amount=amount,
            duration_years=duration_years,
            method=method,
            currency=user.currency
        )
        return jsonify({'success': True, 'comparison': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# -----------------------------------------------------------------------------
# REST API: CURATED BEST SCHEMES
# -----------------------------------------------------------------------------

@tools_bp.route('/api/schemes/best', methods=['GET'])
@login_required
def api_best_schemes():
    tag = request.args.get('tag', 'beginners')
    schemes = filter_schemes(tag=tag)
    return jsonify({
        'success': True,
        'tag': tag,
        'count': len(schemes),
        'schemes': schemes
    })


# -----------------------------------------------------------------------------
# REST API: FUTURE INVESTMENT RETURN CALCULATOR
# -----------------------------------------------------------------------------

@tools_bp.route('/api/tools/investment-calculate', methods=['POST'])
@login_required
def api_investment_calculate():
    user = g.current_user
    data = request.get_json() or {}

    try:
        initial_amount = float(data.get('initial_amount', 0))
        periodic_contribution = float(data.get('periodic_contribution', 0))
        frequency = data.get('frequency', 'MONTHLY').upper()
        annual_return = float(data.get('annual_return_pct', 12.0))
        duration_years = int(data.get('duration_years', 10))
        timing = data.get('timing', 'BEGINNING').upper()
        step_up_pct = float(data.get('step_up_pct', 0.0))
        scheme_id = data.get('scheme_id')

        result = calculate_compound_growth(
            initial_amount=initial_amount,
            periodic_contribution=periodic_contribution,
            frequency=frequency,
            annual_return_pct=annual_return,
            duration_years=duration_years,
            timing=timing,
            currency=user.currency,
            step_up_pct=step_up_pct,
            scheme_id=scheme_id
        )
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# -----------------------------------------------------------------------------
# REST API: PERSONALIZED RECOMMENDATIONS (4 APPROVED CATEGORIES)
# -----------------------------------------------------------------------------

@tools_bp.route('/api/schemes/recommend', methods=['GET', 'POST'])
@login_required
def api_recommend_schemes():
    data = {}
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()

    try:
        amount = float(data.get('amount', 10000.0))
        frequency = data.get('frequency', 'MONTHLY')
        duration_years = int(data.get('duration_years', 5))
        risk_tolerance = data.get('risk_tolerance', 'High')
        objective = data.get('objective', 'wealth_accumulation')
        preferred_category = data.get('preferred_category', 'ALL')
        liquidity = data.get('liquidity', 'HIGH')

        recommendations = get_personalized_recommendations(
            amount=amount,
            frequency=frequency,
            duration_years=duration_years,
            risk_tolerance=risk_tolerance,
            objective=objective,
            preferred_category=preferred_category,
            liquidity=liquidity
        )
        return jsonify({
            'success': True,
            'count': len(recommendations),
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# -----------------------------------------------------------------------------
# REST API: MULTI-INVESTMENT PORTFOLIO PROJECTION & ASSET ALLOCATION
# -----------------------------------------------------------------------------

@tools_bp.route('/api/tools/portfolio-calculate', methods=['POST'])
@login_required
def api_portfolio_calculate():
    user = g.current_user
    data = request.get_json() or {}

    try:
        investments = data.get('investments', [])
        duration_years = int(data.get('duration_years', 10))

        result = calculate_portfolio_projection(
            investments=investments,
            duration_years=duration_years,
            currency=user.currency
        )
        return jsonify({'success': True, 'portfolio': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

