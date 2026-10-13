"""
MoneyLeak Analysis routes, leak detection alerts, and recurring bills tracking.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, g
from app.extensions import db
from app.routes.auth import login_required
from app.models.alert import FinancialAlert
from app.models.recurring_payment import RecurringPayment
from app.models.category import Category
from app.services.leak_detection import run_leak_detection
from app.services.budget_engine import calculate_budget_summary
from app.services.money import to_minor_units, format_money

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analysis')
@login_required
def view_analysis():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    alerts = run_leak_detection(user.id, year, month)
    summary = calculate_budget_summary(user.id, year, month)
    recurring_items = RecurringPayment.query.filter_by(user_id=user.id).all()
    categories = Category.query.filter(
        (Category.user_id == user.id) | (Category.user_id.is_(None)),
        Category.is_active.is_(True)
    ).order_by(Category.name.asc()).all()

    total_recurring_monthly = sum(r.monthly_equivalent_minor_units for r in recurring_items if r.status == 'ACTIVE')
    annual_recurring = total_recurring_monthly * 12

    return render_template(
        'analysis.html',
        user=user,
        alerts=alerts,
        summary=summary,
        recurring_items=recurring_items,
        categories=categories,
        total_recurring_monthly_formatted=format_money(total_recurring_monthly, user.currency),
        annual_recurring_formatted=format_money(annual_recurring, user.currency),
        current_year=year,
        current_month=month
    )


@analysis_bp.route('/api/analysis/summary', methods=['GET'])
@login_required
def api_analysis_summary():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    alerts = run_leak_detection(user.id, year, month)
    return jsonify({
        'success': True,
        'summary': summary,
        'alerts': alerts
    })


@analysis_bp.route('/api/analysis/alerts', methods=['GET'])
@login_required
def api_get_alerts():
    user = g.current_user
    alerts = FinancialAlert.query.filter_by(user_id=user.id, is_dismissed=False)\
        .order_by(FinancialAlert.created_at.desc()).all()
    return jsonify({'success': True, 'alerts': [a.to_dict() for a in alerts]})


@analysis_bp.route('/api/analysis/alerts/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def api_dismiss_alert(alert_id):
    user = g.current_user
    alert = FinancialAlert.query.filter_by(id=alert_id, user_id=user.id).first()
    if not alert:
        return jsonify({'success': False, 'error': 'Alert not found.'}), 404

    alert.is_dismissed = True
    alert.dismissed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'message': 'Alert dismissed.'})


@analysis_bp.route('/api/analysis/recurring', methods=['GET', 'POST'])
@login_required
def api_recurring():
    user = g.current_user
    if request.method == 'POST':
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        amt_raw = data.get('amount')
        freq = (data.get('frequency') or 'MONTHLY').upper()
        next_due_raw = data.get('next_due_date')
        cat_id = data.get('category_id')

        if not name or not amt_raw:
            return jsonify({'success': False, 'error': 'Name and Amount are required.'}), 400

        try:
            amt_minor = to_minor_units(amt_raw, user.currency)
            if amt_minor <= 0:
                return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid amount.'}), 400

        try:
            next_due = datetime.strptime(next_due_raw, '%Y-%m-%d').date() if next_due_raw else date.today()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format.'}), 400

        rp = RecurringPayment(
            user_id=user.id,
            name=name,
            amount_minor_units=amt_minor,
            frequency=freq,
            next_due_date=next_due,
            category_id=cat_id or None,
            status='ACTIVE'
        )
        db.session.add(rp)
        db.session.commit()

        d = rp.to_dict()
        d['formatted_amount'] = format_money(rp.amount_minor_units, user.currency)
        return jsonify({'success': True, 'recurring_payment': d}), 201

    # GET
    recurr_items = RecurringPayment.query.filter_by(user_id=user.id).all()
    results = []
    for r in recurr_items:
        d = r.to_dict()
        d['formatted_amount'] = format_money(r.amount_minor_units, user.currency)
        d['formatted_monthly'] = format_money(r.monthly_equivalent_minor_units, user.currency)
        d['formatted_annual'] = format_money(r.annual_cost_minor_units, user.currency)
        results.append(d)

    return jsonify({'success': True, 'recurring_payments': results})


@analysis_bp.route('/api/analysis/recurring/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_recurring(item_id):
    user = g.current_user
    rp = RecurringPayment.query.filter_by(id=item_id, user_id=user.id).first()
    if not rp:
        return jsonify({'success': False, 'error': 'Item not found.'}), 404

    db.session.delete(rp)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Recurring rule removed.'})
