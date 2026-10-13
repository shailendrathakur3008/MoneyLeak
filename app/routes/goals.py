"""
Financial Goals Planner routes and contribution logging API.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, g
from app.extensions import db
from app.routes.auth import login_required
from app.models.goal import SavingsGoal, GoalContribution
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.goal_engine import get_all_goals_summary, calculate_goal_metrics
from app.services.money import to_minor_units, format_money

goals_bp = Blueprint('goals', __name__)


@goals_bp.route('/goals')
@login_required
def view_goals():
    user = g.current_user
    summary = get_all_goals_summary(user.id, user.currency)
    return render_template('goals.html', user=user, summary=summary)


@goals_bp.route('/api/goals', methods=['GET'])
@login_required
def api_get_goals():
    user = g.current_user
    summary = get_all_goals_summary(user.id, user.currency)
    return jsonify({'success': True, 'data': summary})


@goals_bp.route('/api/goals', methods=['POST'])
@login_required
def api_create_goal():
    user = g.current_user
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    target_amt_raw = data.get('target_amount')
    target_date_raw = data.get('target_date')
    cat_type = (data.get('category_type') or 'EMERGENCY_FUND').upper()
    icon = data.get('icon', 'piggy-bank')

    if not name or not target_amt_raw or not target_date_raw:
        return jsonify({'success': False, 'error': 'Name, Target Amount, and Target Date are required.'}), 400

    try:
        target_minor = to_minor_units(target_amt_raw, user.currency)
        if target_minor <= 0:
            return jsonify({'success': False, 'error': 'Target amount must be greater than zero.'}), 400
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid target amount.'}), 400

    try:
        target_dt = datetime.strptime(target_date_raw, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format (use YYYY-MM-DD).'}), 400

    goal = SavingsGoal(
        user_id=user.id,
        name=name,
        target_amount_minor_units=target_minor,
        target_date=target_dt,
        category_type=cat_type,
        icon=icon,
        status='ACTIVE'
    )
    db.session.add(goal)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Goal created successfully.',
        'goal': calculate_goal_metrics(goal, user.currency)
    }), 201


@goals_bp.route('/api/goals/<int:goal_id>', methods=['PATCH', 'PUT'])
@login_required
def api_update_goal(goal_id):
    user = g.current_user
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'success': False, 'error': 'Goal not found.'}), 404

    data = request.get_json() or {}
    if 'name' in data and data['name'].strip():
        goal.name = data['name'].strip()

    if 'target_amount' in data:
        try:
            amt = to_minor_units(data['target_amount'], user.currency)
            if amt > 0:
                goal.target_amount_minor_units = amt
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid target amount.'}), 400

    if 'target_date' in data and data['target_date']:
        try:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid target date.'}), 400

    if 'status' in data:
        goal.status = data['status'].upper()

    db.session.commit()
    return jsonify({'success': True, 'goal': calculate_goal_metrics(goal, user.currency)})


@goals_bp.route('/api/goals/<int:goal_id>', methods=['DELETE'])
@login_required
def api_delete_goal(goal_id):
    user = g.current_user
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'success': False, 'error': 'Goal not found.'}), 404

    db.session.delete(goal)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Goal deleted.'})


@goals_bp.route('/api/goals/<int:goal_id>/contributions', methods=['POST'])
@login_required
def api_add_goal_contribution(goal_id):
    user = g.current_user
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'success': False, 'error': 'Goal not found.'}), 404

    data = request.get_json() or {}
    amt_raw = data.get('amount')
    notes = (data.get('notes') or '').strip()
    c_date_raw = data.get('contribution_date')

    if not amt_raw:
        return jsonify({'success': False, 'error': 'Contribution amount is required.'}), 400

    try:
        amt_minor = to_minor_units(amt_raw, user.currency)
        if amt_minor <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid amount.'}), 400

    try:
        c_date = datetime.strptime(c_date_raw, '%Y-%m-%d').date() if c_date_raw else date.today()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid contribution date.'}), 400

    # 1. Add GoalContribution
    contrib = GoalContribution(
        user_id=user.id,
        goal_id=goal.id,
        amount_minor_units=amt_minor,
        contribution_date=c_date,
        notes=notes
    )
    db.session.add(contrib)

    # 2. Also register a synchronized SAVINGS_CONTRIBUTION transaction under Emergency/Savings category
    savings_cat = Category.query.filter(
        (Category.user_id == user.id) | (Category.user_id.is_(None)),
        Category.budget_group == 'SAVINGS'
    ).first()

    sync_txn = Transaction(
        user_id=user.id,
        category_id=savings_cat.id if savings_cat else None,
        amount_minor_units=amt_minor,
        transaction_type='SAVINGS_CONTRIBUTION',
        transaction_date=c_date,
        description=f"Goal Contribution: {goal.name}",
        merchant=goal.name,
        notes=notes
    )
    db.session.add(sync_txn)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Logged {format_money(amt_minor, user.currency)} to {goal.name}!',
        'goal': calculate_goal_metrics(goal, user.currency)
    }), 201
