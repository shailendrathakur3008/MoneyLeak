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
from app.services.money import to_minor_units, format_money
from app.services.persistent_budget_service import (
    get_or_create_monthly_budget,
    set_monthly_budget,
    confirm_retained_budget,
    postpone_budget_confirmation,
    dismiss_budget_prompt,
    mark_prompt_shown,
    get_monthly_prompt_info,
    get_budget_history
)

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

    income_val = data.get('monthly_income')
    if income_val not in (None, ''):
        try:
            user.monthly_income_minor_units = to_minor_units(income_val, user.currency)
        except Exception:
            pass

    budget_val = data.get('monthly_budget')
    if budget_val not in (None, ''):
        try:
            today = date.today()
            target_year = int(data.get('year', today.year))
            target_month = int(data.get('month', today.month))
            b_minor = to_minor_units(budget_val, user.currency)
            if b_minor >= 0:
                set_monthly_budget(user.id, target_year, target_month, b_minor, update_future=True)
        except Exception:
            pass

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


@budget_bp.route('/api/budget/monthly-status', methods=['GET'])
@login_required
def api_monthly_budget_status():
    """Returns monthly confirmation prompt metadata and marks prompt as shown if eligible."""
    user = g.current_user
    today = date.today()
    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    prompt_info = get_monthly_prompt_info(user.id, year, month)
    if prompt_info['should_prompt']:
        mark_prompt_shown(user.id, year, month)
    return jsonify({'success': True, 'prompt_info': prompt_info})


@budget_bp.route('/api/budget/confirm-action', methods=['POST'])
@login_required
def api_confirm_budget_action():
    """Handles the monthly confirmation prompt actions: set_new, keep_previous, remind_later, dismiss."""
    user = g.current_user
    data = request.get_json() or {}
    today = date.today()
    try:
        year = int(data.get('year', today.year))
        month = int(data.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    action = (data.get('action') or '').strip().lower()

    if action in ('set_new', 'new_budget_saved'):
        amount_raw = data.get('amount')
        if amount_raw in (None, ''):
            return jsonify({'success': False, 'error': 'Budget amount is required.'}), 400
        try:
            amount_minor = to_minor_units(amount_raw, user.currency)
            if amount_minor < 0:
                raise ValueError()
        except Exception:
            return jsonify({'success': False, 'error': 'Please enter a valid positive budget amount.'}), 400

        mb = set_monthly_budget(user.id, year, month, amount_minor, update_future=True)
        message = f"Budget for {data.get('month_name', 'this month')} saved as {format_money(amount_minor, user.currency)}."
    elif action in ('keep_previous', 'previous_budget_retained'):
        mb = confirm_retained_budget(user.id, year, month)
        message = f"Previous budget of {format_money(mb.budget_amount_minor_units, user.currency)} retained."
    elif action in ('remind_later', 'reminder_postponed', 'postpone'):
        mb = postpone_budget_confirmation(user.id, year, month)
        message = "Reminder postponed. You can set or confirm your budget anytime from Dashboard or Settings."
    elif action in ('dismiss', 'prompt_dismissed'):
        mb = dismiss_budget_prompt(user.id, year, month)
        message = "Prompt dismissed. Existing saved budget remains active."
    else:
        return jsonify({
            'success': False,
            'error': f"Invalid action: '{action}'. Expected 'set_new', 'keep_previous', 'remind_later', or 'dismiss'."
        }), 400

    summary = calculate_budget_summary(user.id, year, month)
    prompt_info = get_monthly_prompt_info(user.id, year, month)

    return jsonify({
        'success': True,
        'message': message,
        'summary': summary,
        'prompt_info': prompt_info
    })


@budget_bp.route('/api/budget/update-amount', methods=['POST'])
@login_required
def api_update_budget_amount():
    """Allows user to explicitly set their monthly persistent budget amount directly."""
    user = g.current_user
    data = request.get_json() or {}
    today = date.today()
    try:
        year = int(data.get('year', today.year))
        month = int(data.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    amount_raw = data.get('amount')
    if amount_raw in (None, ''):
        return jsonify({'success': False, 'error': 'Budget amount is required.'}), 400
    try:
        amount_minor = to_minor_units(amount_raw, user.currency)
        if amount_minor < 0:
            raise ValueError()
    except Exception:
        return jsonify({'success': False, 'error': 'Please enter a valid positive budget amount.'}), 400

    mb = set_monthly_budget(user.id, year, month, amount_minor, update_future=True)
    summary = calculate_budget_summary(user.id, year, month)
    return jsonify({
        'success': True,
        'message': f"Monthly budget set to {format_money(amount_minor, user.currency)}.",
        'budget': {
            'amount_minor': mb.budget_amount_minor_units,
            'amount_formatted': format_money(mb.budget_amount_minor_units, user.currency),
            'year': mb.year,
            'month': mb.month
        },
        'summary': summary
    })


@budget_bp.route('/api/budget/history', methods=['GET'])
@login_required
def api_budget_history():
    """Returns chronological monthly budget history."""
    user = g.current_user
    limit = int(request.args.get('limit', 12))
    history = get_budget_history(user.id, limit=limit)
    return jsonify({'success': True, 'history': history})

