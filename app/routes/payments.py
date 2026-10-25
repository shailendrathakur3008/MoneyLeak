"""
Upcoming Payments & Payment Schedule Management Routes for MoneyLeak.

Endpoints:
- GET /payments: Upcoming Payments web view (List & Calendar, stats, modals)
- GET /api/payments: JSON list with dashboard statistics (7-day, 30-day, overdue)
- POST /api/payments: Create scheduled payment (SIPs, EMIs, Subscriptions, Bills)
- PUT /api/payments/<id>: Edit scheduled payment
- DELETE /api/payments/<id>: Cancel scheduled payment
- POST /api/payments/occurrences/<id>/mark-paid: Manually mark an installment as paid
- POST /api/payments/occurrences/<id>/snooze: Snooze a reminder by N days
- POST /api/scheduler/run-reminders: Protected scheduler trigger for crons/workers
"""
import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, g, current_app
from app.extensions import db
from app.routes.auth import login_required
from app.models.recurring_payment import RecurringPayment, PaymentSchedule
from app.models.payment_notification import PaymentOccurrence, Notification
from app.services.reminder_service import (
    advance_due_date,
    format_inr
)
from app.services.scheduler_service import (
    ensure_occurrences_for_schedule,
    process_reminders_for_user,
    run_all_scheduled_reminders
)

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/payments')
@login_required
def view_payments():
    """Renders the Upcoming Payments dashboard page."""
    user = g.current_user
    # Opportunistically ensure occurrences and process pending reminders
    try:
        process_reminders_for_user(user.id)
    except Exception as e:
        print(f"[payments.view_payments] Opportunistic reminder error: {e}")

    return render_template(
        'payments.html',
        user=user
    )


@payments_bp.route('/api/payments', methods=['GET'])
@login_required
def api_get_payments():
    """
    Returns all scheduled payments, occurrences, and summary statistics:
    - Next payment amount & date
    - Obligations due in next 7 days
    - Obligations due in next 30 days
    - Total monthly scheduled commitments
    - Overdue payment count
    """
    user = g.current_user
    today = date.today()

    # 1. Fetch active schedules
    schedules = (
        RecurringPayment.query
        .filter_by(user_id=user.id)
        .order_by(RecurringPayment.status.asc(), RecurringPayment.next_due_date.asc())
        .all()
    )

    # Ensure occurrences exist for all active schedules
    for s in schedules:
        if s.status == 'ACTIVE':
            ensure_occurrences_for_schedule(s)

    # 2. Fetch occurrences (past 30 days to next 60 days)
    min_date = today - timedelta(days=30)
    max_date = today + timedelta(days=60)

    occurrences = (
        PaymentOccurrence.query
        .join(RecurringPayment, PaymentOccurrence.payment_schedule_id == RecurringPayment.id)
        .filter(
            RecurringPayment.user_id == user.id,
            PaymentOccurrence.due_date >= min_date,
            PaymentOccurrence.due_date <= max_date
        )
        .order_by(PaymentOccurrence.due_date.asc())
        .all()
    )

    # 3. Calculate Dashboard Statistics
    next_7_days = today + timedelta(days=7)
    next_30_days = today + timedelta(days=30)

    sum_7_days = 0.0
    sum_30_days = 0.0
    overdue_count = 0
    next_payment_item = None

    for occ in occurrences:
        if not occ.is_paid:
            if occ.due_date < today:
                overdue_count += 1
                occ.status = 'OVERDUE'
            else:
                if occ.due_date <= next_7_days:
                    sum_7_days += occ.amount
                if occ.due_date <= next_30_days:
                    sum_30_days += occ.amount
                if next_payment_item is None:
                    next_payment_item = occ.to_dict()

    total_monthly_obligations = sum(
        s.monthly_equivalent_minor_units / 100.0
        for s in schedules
        if s.status == 'ACTIVE'
    )

    return jsonify({
        'success': True,
        'statistics': {
            'next_payment': next_payment_item,
            'next_7_days_total': round(sum_7_days, 2),
            'next_7_days_formatted': format_inr(sum_7_days),
            'next_30_days_total': round(sum_30_days, 2),
            'next_30_days_formatted': format_inr(sum_30_days),
            'total_monthly_obligations': round(total_monthly_obligations, 2),
            'total_monthly_formatted': format_inr(total_monthly_obligations),
            'overdue_count': overdue_count
        },
        'schedules': [s.to_dict() for s in schedules],
        'occurrences': [occ.to_dict() for occ in occurrences]
    })


@payments_bp.route('/api/payments', methods=['POST'])
@login_required
def api_create_payment():
    """Creates a new scheduled payment and generates its initial occurrence."""
    user = g.current_user
    data = request.get_json(silent=True) or {}

    name = (data.get('payment_name') or data.get('name') or '').strip()
    category = (data.get('category') or 'CUSTOM').upper()
    amount_val = data.get('amount')
    frequency = (data.get('frequency') or 'MONTHLY').upper()
    next_due_raw = data.get('next_due_date')
    scheme_name = (data.get('scheme_name') or '').strip()
    scheme_id = (data.get('scheme_id') or '').strip()
    notes = (data.get('notes') or '').strip()

    if not name:
        return jsonify({'success': False, 'error': 'Payment name is required.'}), 400

    try:
        amount_float = float(amount_val)
        if amount_float <= 0:
            raise ValueError
        amount_minor = int(round(amount_float * 100))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Valid payment amount in INR is required.'}), 400

    try:
        next_due = datetime.strptime(next_due_raw, '%Y-%m-%d').date() if next_due_raw else date.today()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid next due date format. Use YYYY-MM-DD.'}), 400

    schedule = RecurringPayment(
        user_id=user.id,
        name=name,
        category=category,
        amount_minor_units=amount_minor,
        currency='INR',
        frequency=frequency,
        next_due_date=next_due,
        start_date=date.today(),
        status='ACTIVE',
        scheme_name=scheme_name or (name if 'SIP' in category else None),
        scheme_id=scheme_id or None,
        notes=notes or None
    )
    db.session.add(schedule)
    db.session.commit()

    # Create initial occurrence
    occ = PaymentOccurrence(
        payment_schedule_id=schedule.id,
        due_date=next_due,
        amount_minor_units=amount_minor,
        status='PENDING'
    )
    db.session.add(occ)
    db.session.commit()

    # Opportunistically evaluate reminders
    try:
        process_reminders_for_user(user.id)
    except Exception:
        pass

    return jsonify({
        'success': True,
        'message': f"Scheduled payment '{name}' created successfully.",
        'schedule': schedule.to_dict(),
        'occurrence': occ.to_dict()
    }), 201


@payments_bp.route('/api/payments/<int:schedule_id>', methods=['PUT'])
@login_required
def api_update_payment(schedule_id: int):
    """Updates an existing payment schedule and synchronizes upcoming pending occurrences."""
    user = g.current_user
    schedule = RecurringPayment.query.filter_by(id=schedule_id, user_id=user.id).first()
    if not schedule:
        return jsonify({'success': False, 'error': 'Payment schedule not found.'}), 404

    data = request.get_json(silent=True) or {}

    if 'name' in data or 'payment_name' in data:
        schedule.name = (data.get('payment_name') or data.get('name') or schedule.name).strip()
    if 'category' in data:
        schedule.category = (data['category'] or 'CUSTOM').upper()
    if 'frequency' in data:
        schedule.frequency = (data['frequency'] or schedule.frequency).upper()
    if 'scheme_name' in data:
        schedule.scheme_name = (data['scheme_name'] or '').strip() or None
    if 'notes' in data:
        schedule.notes = (data['notes'] or '').strip() or None
    if 'status' in data:
        schedule.status = data['status'].upper()

    if 'amount' in data:
        try:
            amt = float(data['amount'])
            if amt > 0:
                schedule.amount_minor_units = int(round(amt * 100))
        except (ValueError, TypeError):
            pass

    date_changed = False
    if 'next_due_date' in data and data['next_due_date']:
        try:
            new_date = datetime.strptime(data['next_due_date'], '%Y-%m-%d').date()
            if new_date != schedule.next_due_date:
                schedule.next_due_date = new_date
                date_changed = True
        except ValueError:
            pass

    # Update pending occurrences with new amount / due date
    pending_occ = PaymentOccurrence.query.filter_by(
        payment_schedule_id=schedule.id,
        status='PENDING'
    ).first()
    if pending_occ:
        pending_occ.amount_minor_units = schedule.amount_minor_units
        if date_changed:
            pending_occ.due_date = schedule.next_due_date

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Payment schedule '{schedule.name}' updated.",
        'schedule': schedule.to_dict()
    })


@payments_bp.route('/api/payments/<int:schedule_id>', methods=['DELETE'])
@login_required
def api_cancel_payment(schedule_id: int):
    """Cancels a payment schedule and marks upcoming pending occurrences as cancelled."""
    user = g.current_user
    schedule = RecurringPayment.query.filter_by(id=schedule_id, user_id=user.id).first()
    if not schedule:
        return jsonify({'success': False, 'error': 'Payment schedule not found.'}), 404

    schedule.status = 'CANCELLED'

    # Cancel future pending occurrences
    PaymentOccurrence.query.filter(
        PaymentOccurrence.payment_schedule_id == schedule.id,
        PaymentOccurrence.status.in_(['PENDING', 'AWAITING_CONFIRMATION', 'OVERDUE'])
    ).update({'status': 'CANCELLED'}, synchronize_session=False)

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Payment schedule '{schedule.name}' has been cancelled."
    })


@payments_bp.route('/api/payments/occurrences/<int:occ_id>/mark-paid', methods=['POST'])
@login_required
def api_mark_occurrence_paid(occ_id: int):
    """
    Manually marks a payment occurrence as paid.
    Distinguished from verified external bank confirmation ('PAID_MANUAL' vs 'CONFIRMED_EXTERNAL').
    Advances the schedule's next_due_date and creates the next occurrence.
    """
    user = g.current_user
    occ = (
        PaymentOccurrence.query
        .join(RecurringPayment, PaymentOccurrence.payment_schedule_id == RecurringPayment.id)
        .filter(PaymentOccurrence.id == occ_id, RecurringPayment.user_id == user.id)
        .first()
    )
    if not occ:
        return jsonify({'success': False, 'error': 'Payment occurrence not found.'}), 404

    occ.status = 'PAID_MANUAL'
    occ.manually_confirmed_at = datetime.utcnow()

    sched = occ.schedule
    # Advance schedule's next_due_date if this occurrence was for current due date
    if sched.next_due_date <= occ.due_date and sched.status == 'ACTIVE':
        sched.next_due_date = advance_due_date(occ.due_date, sched.frequency)
        # Create next occurrence
        ensure_occurrences_for_schedule(sched)

    # Create in-app payment update notification
    notif = Notification(
        user_id=user.id,
        payment_occurrence_id=occ.id,
        payment_schedule_id=sched.id,
        notification_type='PAYMENT_PAID_MANUAL',
        channel='IN_APP',
        title=f"Payment Marked as Paid: {sched.name}",
        message=f"You marked {format_inr(occ.amount)} for {sched.name} as paid on {datetime.utcnow().strftime('%d %b %Y')}.",
        link_url='/payments',
        idempotency_key=f"manual_paid_{occ.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        delivery_status='DELIVERED',
        sent_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Payment for '{sched.name}' marked as paid.",
        'occurrence': occ.to_dict(),
        'next_due_date': sched.next_due_date.isoformat() if sched.next_due_date else None
    })


@payments_bp.route('/api/payments/occurrences/<int:occ_id>/snooze', methods=['POST'])
@login_required
def api_snooze_occurrence(occ_id: int):
    """Snoozes an upcoming reminder by shifting the occurrence due date by N days (default 3)."""
    user = g.current_user
    occ = (
        PaymentOccurrence.query
        .join(RecurringPayment, PaymentOccurrence.payment_schedule_id == RecurringPayment.id)
        .filter(PaymentOccurrence.id == occ_id, RecurringPayment.user_id == user.id)
        .first()
    )
    if not occ:
        return jsonify({'success': False, 'error': 'Payment occurrence not found.'}), 404

    data = request.get_json(silent=True) or {}
    days = max(1, min(7, int(data.get('days', 3))))

    occ.due_date = occ.due_date + timedelta(days=days)
    if occ.status == 'OVERDUE' and occ.due_date >= date.today():
        occ.status = 'PENDING'

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Reminder snoozed by {days} days. New due date: {occ.due_date.strftime('%d %b %Y')}.",
        'occurrence': occ.to_dict()
    })


# -----------------------------------------------------------------------------
# PROTECTED SCHEDULER EXECUTION ENDPOINT
# -----------------------------------------------------------------------------

@payments_bp.route('/api/scheduler/run-reminders', methods=['POST'])
def api_trigger_scheduler():
    """
    Protected scheduler endpoint callable by cron jobs (Vercel Cron, external curl) or admin session.
    Protected via X-Scheduler-Token or Bearer Authorization header.
    """
    expected_secret = os.environ.get('SCHEDULER_SECRET_KEY') or current_app.config.get('SECRET_KEY')
    auth_header = request.headers.get('Authorization', '')
    token_header = request.headers.get('X-Scheduler-Token', '')

    bearer_token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''
    provided_token = token_header or bearer_token

    # Allow if token matches or user is logged in
    has_valid_token = bool(provided_token and provided_token == expected_secret)
    is_authenticated_user = bool(g.get('current_user') or session.get('user_id'))

    if not has_valid_token and not is_authenticated_user:
        return jsonify({'success': False, 'error': 'Unauthorized scheduler invocation.'}), 401

    if is_authenticated_user and not has_valid_token:
        # Run for current user
        res = process_reminders_for_user(g.current_user.id if g.get('current_user') else session.get('user_id'))
        return jsonify(res)

    # Run for all registered users
    res = run_all_scheduled_reminders()
    return jsonify(res)
