"""
50/30/20 Budget configuration and comparison routes.
"""
from datetime import date
from flask import Blueprint, render_template, request, jsonify, g
from app.extensions import db
from app.routes.auth import login_required
from app.models.budget import Budget
from app.services.location_service import BUDGET_PRESETS, CLASSIFICATION_LABELS
from app.services.budget_engine import calculate_budget_summary, DEFAULT_NEEDS_PCT, DEFAULT_WANTS_PCT, DEFAULT_SAVINGS_PCT

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/budget')
@login_required
def view_budget():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    return render_template(
        'budget.html',
        user=user,
        summary=summary,
        current_year=year,
        current_month=month,
        budget_presets=BUDGET_PRESETS,
        classification_labels=CLASSIFICATION_LABELS
    )


@budget_bp.route('/api/budget/apply-preset', methods=['POST'])
@login_required
def api_apply_preset():
    """Applies an India-adaptive budget preset without affecting transaction history."""
    user = g.current_user
    data = request.get_json() or {}
    preset_key = data.get('preset_key', 'standard')

    if preset_key not in BUDGET_PRESETS:
        return jsonify({'success': False, 'error': f'Invalid preset: {preset_key}'}), 400

    preset = BUDGET_PRESETS[preset_key]
    budget = Budget.query.filter_by(user_id=user.id).order_by(Budget.created_at.desc()).first()
    if not budget:
        budget = Budget(user_id=user.id)
        db.session.add(budget)

    budget.needs_percentage = preset['needs']
    budget.wants_percentage = preset['wants']
    budget.savings_percentage = preset['savings']
    user.budget_preset = preset_key
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Applied {preset['title']}.",
        'budget': {
            'needs_percentage': preset['needs'],
            'wants_percentage': preset['wants'],
            'savings_percentage': preset['savings'],
            'preset': preset_key
        }
    })


@budget_bp.route('/api/budget', methods=['GET'])
@login_required
def api_get_budget():
    user = g.current_user
    budget = Budget.query.filter_by(user_id=user.id).order_by(Budget.created_at.desc()).first()
    if not budget:
        return jsonify({
            'success': True,
            'needs_percentage': DEFAULT_NEEDS_PCT,
            'wants_percentage': DEFAULT_WANTS_PCT,
            'savings_percentage': DEFAULT_SAVINGS_PCT
        })
    return jsonify({
        'success': True,
        'needs_percentage': budget.needs_percentage,
        'wants_percentage': budget.wants_percentage,
        'savings_percentage': budget.savings_percentage
    })


@budget_bp.route('/api/budget', methods=['PUT', 'POST'])
@login_required
def api_update_budget():
    user = g.current_user
    data = request.get_json() or {}

    try:
        needs = float(data.get('needs_percentage', DEFAULT_NEEDS_PCT))
        wants = float(data.get('wants_percentage', DEFAULT_WANTS_PCT))
        savings = float(data.get('savings_percentage', DEFAULT_SAVINGS_PCT))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Percentages must be valid numbers.'}), 400

    if needs < 0 or wants < 0 or savings < 0:
        return jsonify({'success': False, 'error': 'Percentages cannot be negative.'}), 400

    if round(needs + wants + savings, 1) != 100.0:
        return jsonify({'success': False, 'error': f'Percentages must sum exactly to 100%. (Current sum: {needs + wants + savings}%)'}), 400

    budget = Budget.query.filter_by(user_id=user.id).order_by(Budget.created_at.desc()).first()
    if not budget:
        budget = Budget(user_id=user.id)
        db.session.add(budget)

    budget.needs_percentage = needs
    budget.wants_percentage = wants
    budget.savings_percentage = savings

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Budget allocations updated successfully.',
        'budget': {
            'needs_percentage': needs,
            'wants_percentage': wants,
            'savings_percentage': savings
        }
    })


@budget_bp.route('/api/budget/reset', methods=['POST'])
@login_required
def api_reset_budget():
    user = g.current_user
    budget = Budget.query.filter_by(user_id=user.id).order_by(Budget.created_at.desc()).first()
    if not budget:
        budget = Budget(user_id=user.id)
        db.session.add(budget)

    budget.needs_percentage = DEFAULT_NEEDS_PCT
    budget.wants_percentage = DEFAULT_WANTS_PCT
    budget.savings_percentage = DEFAULT_SAVINGS_PCT
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Budget reset to standard 50/30/20 framework.',
        'budget': {
            'needs_percentage': DEFAULT_NEEDS_PCT,
            'wants_percentage': DEFAULT_WANTS_PCT,
            'savings_percentage': DEFAULT_SAVINGS_PCT
        }
    })


@budget_bp.route('/api/budget/analysis', methods=['GET'])
@login_required
def api_budget_analysis():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    return jsonify({'success': True, 'analysis': summary})
