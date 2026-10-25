"""
Dashboard routes and analytics API.
"""
from datetime import date
from flask import Blueprint, render_template, request, jsonify, g
from app.routes.auth import login_required
from app.models.transaction import Transaction
from app.models.recurring_payment import RecurringPayment
from app.models.goal import SavingsGoal
from app.services.budget_engine import calculate_budget_summary, get_month_date_range
from app.services.leak_detection import run_leak_detection
from app.services.goal_engine import get_all_goals_summary
from app.services.money import format_money
from app.services.persistent_budget_service import get_monthly_prompt_info

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    return render_template('index.html')


@dashboard_bp.route('/dashboard')
@login_required
def view_dashboard():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    alerts = run_leak_detection(user.id, year, month)
    goals_data = get_all_goals_summary(user.id, user.currency)
    prompt_info = get_monthly_prompt_info(user.id, year, month)

    # Recent transactions
    recent_txns = Transaction.query.filter_by(user_id=user.id)\
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())\
        .limit(6).all()

    # Recurring active summary
    recurring_items = RecurringPayment.query.filter_by(user_id=user.id, status='ACTIVE').all()
    total_recurring_monthly = sum(r.monthly_equivalent_minor_units for r in recurring_items)

    return render_template(
        'dashboard.html',
        user=user,
        summary=summary,
        alerts=alerts,
        goals_data=goals_data,
        prompt_info=prompt_info,
        recent_txns=recent_txns,
        recurring_count=len(recurring_items),
        recurring_monthly_formatted=format_money(total_recurring_monthly, user.currency),
        current_year=year,
        current_month=month
    )


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    alerts = run_leak_detection(user.id, year, month)
    goals_data = get_all_goals_summary(user.id, user.currency)
    prompt_info = get_monthly_prompt_info(user.id, year, month)

    return jsonify({
        'success': True,
        'summary': summary,
        'alerts': alerts,
        'goals': goals_data,
        'prompt_info': prompt_info
    })


@dashboard_bp.route('/api/dashboard/trends', methods=['GET'])
@login_required
def api_dashboard_trends():
    user = g.current_user
    today = date.today()
    num_months = int(request.args.get('months', 6))

    trends = []
    # Collect chronological data for the past num_months
    for i in range(num_months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        summary = calculate_budget_summary(user.id, y, m)
        label = date(y, m, 1).strftime('%b %y')
        trends.append({
            'label': label,
            'year': y,
            'month': m,
            'income_minor': summary['income']['minor'],
            'expenses_minor': summary['expenses']['minor'],
            'savings_minor': summary['actual_savings']['minor'],
            'surplus_minor': summary['surplus']['minor']
        })

    return jsonify({
        'success': True,
        'currency': user.currency,
        'trends': trends
    })
