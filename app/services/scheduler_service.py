"""
Backend Reminder Scheduler & Notification Dispatch Engine for MoneyLeak.

Automates:
- Generation of pending PaymentOccurrences for active schedules
- Smart evaluation of due dates against user reminder preferences
- Multi-channel delivery across In-App, Transactional Email, and Browser Push
- Idempotency guarantees preventing duplicate notifications
- Safe error logging and outcome recording in the database
"""
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from app.extensions import db
from app.models.user import User
from app.models.recurring_payment import RecurringPayment, PaymentSchedule
from app.models.payment_notification import (
    PaymentOccurrence,
    Notification,
    NotificationPreference,
    PushSubscription
)
from app.services.reminder_service import (
    generate_reminder_content,
    advance_due_date,
    format_inr
)
from app.services.email_service import send_payment_reminder_email
from app.services.push_service import send_web_push


def get_or_create_user_preference(user_id: int) -> NotificationPreference:
    """Retrieve existing user preferences or initialize sensible defaults."""
    pref = NotificationPreference.query.filter_by(user_id=user_id).first()
    if not pref:
        pref = NotificationPreference(
            user_id=user_id,
            in_app_enabled=True,
            email_enabled=True,
            browser_push_enabled=True,
            reminder_days_before='[3, 1]',
            reminder_on_due_date=True,
            quiet_hours_enabled=False,
            timezone='Asia/Kolkata',
            category_sip_enabled=True,
            category_subscription_enabled=True,
            category_emi_enabled=True,
            category_bill_enabled=True,
            category_insurance_enabled=True,
            category_other_enabled=True
        )
        db.session.add(pref)
        db.session.commit()
    return pref


def ensure_occurrences_for_schedule(schedule: RecurringPayment, days_ahead: int = 45) -> List[PaymentOccurrence]:
    """
    Ensures that a PaymentOccurrence exists for the schedule's next_due_date
    if it falls within the upcoming lookahead horizon.
    """
    if schedule.status != 'ACTIVE' or not schedule.next_due_date:
        return []

    cutoff = date.today() + timedelta(days=days_ahead)
    created = []

    # If current next_due_date is within lookahead, ensure occurrence exists
    if schedule.next_due_date <= cutoff:
        existing = PaymentOccurrence.query.filter_by(
            payment_schedule_id=schedule.id,
            due_date=schedule.next_due_date
        ).first()

        if not existing:
            occ = PaymentOccurrence(
                payment_schedule_id=schedule.id,
                due_date=schedule.next_due_date,
                amount_minor_units=schedule.amount_minor_units,
                status='PENDING'
            )
            db.session.add(occ)
            db.session.commit()
            created.append(occ)

    return created


def process_reminders_for_user(user_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Evaluates and dispatches all due payment reminders for a single user.
    Enforces idempotency keys so re-running produces zero duplicates.
    """
    today = target_date or date.today()
    user = db.session.get(User, user_id)
    if not user:
        return {'success': False, 'error': 'User not found.'}

    pref = get_or_create_user_preference(user_id)
    stats = {
        'in_app_created': 0,
        'emails_sent': 0,
        'push_sent': 0,
        'skipped_idempotent': 0,
        'occurrences_evaluated': 0
    }

    # 1. Ensure occurrences exist for active schedules
    active_schedules = RecurringPayment.query.filter_by(user_id=user_id, status='ACTIVE').all()
    for sched in active_schedules:
        ensure_occurrences_for_schedule(sched)

    # 2. Query all pending/unconfirmed occurrences for this user
    occurrences = (
        PaymentOccurrence.query
        .join(RecurringPayment, PaymentOccurrence.payment_schedule_id == RecurringPayment.id)
        .filter(
            RecurringPayment.user_id == user_id,
            RecurringPayment.status == 'ACTIVE',
            PaymentOccurrence.status.in_(['PENDING', 'AWAITING_CONFIRMATION', 'OVERDUE']),
            PaymentOccurrence.due_date <= (today + timedelta(days=14))
        )
        .all()
    )

    offsets = pref.reminder_offsets  # e.g. [7, 3, 1]

    for occ in occurrences:
        sched = occ.schedule
        stats['occurrences_evaluated'] += 1

        # Check if category is enabled in user settings
        if not pref.is_category_enabled(sched.category):
            continue

        days_until_due = (occ.due_date - today).days

        # Determine if today matches any scheduled reminder offset
        matches_offset = False
        offset_key = days_until_due

        if days_until_due in offsets:
            matches_offset = True
        elif days_until_due == 0 and pref.reminder_on_due_date:
            matches_offset = True
        elif days_until_due < 0:
            # Overdue: trigger reminder on day 1 after due date
            if days_until_due == -1:
                matches_offset = True
                occ.status = 'OVERDUE'

        if not matches_offset:
            continue

        content = generate_reminder_content(sched, occ, days_until_due)

        # ---------------------------------------------------------------------
        # Channel 1: In-App Notification
        # ---------------------------------------------------------------------
        if pref.in_app_enabled:
            idemp_in_app = f"inapp_occ_{occ.id}_d_{offset_key}"
            existing_notif = Notification.query.filter_by(idempotency_key=idemp_in_app).first()
            if not existing_notif:
                in_app = Notification(
                    user_id=user_id,
                    payment_occurrence_id=occ.id,
                    payment_schedule_id=sched.id,
                    notification_type=content['notification_type'],
                    channel='IN_APP',
                    title=content['title'],
                    message=content['message'],
                    link_url='/payments',
                    idempotency_key=idemp_in_app,
                    delivery_status='DELIVERED',
                    sent_at=datetime.utcnow()
                )
                db.session.add(in_app)
                stats['in_app_created'] += 1
            else:
                stats['skipped_idempotent'] += 1

        # ---------------------------------------------------------------------
        # Channel 2: Transactional Email
        # ---------------------------------------------------------------------
        if pref.email_enabled and user.email:
            idemp_email = f"email_occ_{occ.id}_d_{offset_key}"
            existing_email = Notification.query.filter_by(idempotency_key=idemp_email).first()
            if not existing_email:
                dispatch_res = send_payment_reminder_email(
                    user_email=user.email,
                    user_name=user.full_name or 'there',
                    schedule_data=sched,
                    occurrence_data=occ,
                    days_before=days_until_due,
                    content_dict=content
                )
                status_str = 'DELIVERED' if dispatch_res.delivered else (
                    'PROVIDER_NOT_CONFIGURED' if dispatch_res.provider == 'UNCONFIGURED' else 'FAILED'
                )
                email_notif = Notification(
                    user_id=user_id,
                    payment_occurrence_id=occ.id,
                    payment_schedule_id=sched.id,
                    notification_type=content['notification_type'],
                    channel='EMAIL',
                    title=content['title'],
                    message=content['message'],
                    link_url='/payments',
                    idempotency_key=idemp_email,
                    delivery_status=status_str,
                    provider_message_id=dispatch_res.provider,
                    error_details=dispatch_res.message if not dispatch_res.delivered else None,
                    sent_at=datetime.utcnow() if dispatch_res.delivered else None
                )
                db.session.add(email_notif)
                if dispatch_res.delivered:
                    stats['emails_sent'] += 1
            else:
                stats['skipped_idempotent'] += 1

        # ---------------------------------------------------------------------
        # Channel 3: Browser Push Notification
        # ---------------------------------------------------------------------
        if pref.browser_push_enabled:
            idemp_push = f"push_occ_{occ.id}_d_{offset_key}"
            existing_push = Notification.query.filter_by(idempotency_key=idemp_push).first()
            if not existing_push:
                push_subs = PushSubscription.query.filter_by(user_id=user_id, is_active=True).all()
                push_delivered = False
                push_errors = []

                if push_subs:
                    push_payload = {
                        'title': content['title'],
                        'body': content['push_body'],
                        'icon': '/static/icons/icon-192.png',
                        'badge': '/static/icons/badge-72.png',
                        'data': {
                            'url': '/payments',
                            'occurrence_id': occ.id
                        }
                    }
                    for sub in push_subs:
                        ok, msg = send_web_push(sub, push_payload)
                        if ok:
                            push_delivered = True
                        else:
                            push_errors.append(msg)

                push_status = 'DELIVERED' if push_delivered else (
                    'NO_ACTIVE_SUBSCRIPTION' if not push_subs else 'FAILED'
                )
                push_notif = Notification(
                    user_id=user_id,
                    payment_occurrence_id=occ.id,
                    payment_schedule_id=sched.id,
                    notification_type=content['notification_type'],
                    channel='BROWSER_PUSH',
                    title=content['title'],
                    message=content['push_body'],
                    link_url='/payments',
                    idempotency_key=idemp_push,
                    delivery_status=push_status,
                    error_details="; ".join(push_errors) if push_errors else None,
                    sent_at=datetime.utcnow() if push_delivered else None
                )
                db.session.add(push_notif)
                if push_delivered:
                    stats['push_sent'] += 1
            else:
                stats['skipped_idempotent'] += 1

    db.session.commit()
    return {'success': True, 'stats': stats}


def run_all_scheduled_reminders(target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Global scheduler worker function called by cron, background worker, or secure API endpoint.
    Processes reminder schedules across all registered users.
    """
    today = target_date or date.today()
    users = User.query.all()
    total_stats = {
        'total_users': len(users),
        'in_app_created': 0,
        'emails_sent': 0,
        'push_sent': 0,
        'skipped_idempotent': 0,
        'occurrences_evaluated': 0
    }

    for u in users:
        try:
            res = process_reminders_for_user(u.id, target_date=today)
            if res.get('success') and 'stats' in res:
                s = res['stats']
                total_stats['in_app_created'] += s.get('in_app_created', 0)
                total_stats['emails_sent'] += s.get('emails_sent', 0)
                total_stats['push_sent'] += s.get('push_sent', 0)
                total_stats['skipped_idempotent'] += s.get('skipped_idempotent', 0)
                total_stats['occurrences_evaluated'] += s.get('occurrences_evaluated', 0)
        except Exception as e:
            print(f"[SchedulerService] Error processing reminders for user {u.id}: {e}")

    return {'success': True, 'date': today.isoformat(), 'stats': total_stats}
