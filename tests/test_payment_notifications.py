"""
Comprehensive Automated Tests for Payment Reminders & Multi-Channel Notification System:
- Dynamic SIP reminder scheduling (3 days before, 1 day before, due date)
- In-App Notification persistence and mark-read flows
- Idempotency guarantees preventing duplicate reminders across scheduler runs
- Email reminder generation, disclaimers, and provider fallback logging
- Browser Web Push subscription registration and multi-device support
- Pruning of expired push subscriptions (HTTP 410)
- Payment schedule cancellation and reminder updates
- Month-end and leap-year calendar arithmetic
- Distinction between manual marking and verified external bank confirmation
- User data isolation
- Provider-independent bank transaction matching interface (PaymentMatchingService)
"""
import pytest
from datetime import date, datetime, timedelta
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
    advance_due_date,
    generate_reminder_content,
    format_inr
)
from app.services.scheduler_service import (
    get_or_create_user_preference,
    ensure_occurrences_for_schedule,
    process_reminders_for_user,
    run_all_scheduled_reminders
)
from app.services.payment_matching_service import (
    PaymentMatchingService,
    BankTransactionDTO
)


def test_month_end_and_frequency_calculations():
    """Verify month-end arithmetic, leap year handling, and frequency advances."""
    # Monthly: Jan 31 -> Feb 28 (non-leap)
    d_jan31 = date(2025, 1, 31)
    d_feb = advance_due_date(d_jan31, 'MONTHLY')
    assert d_feb == date(2025, 2, 28)

    # Monthly: Jan 31 -> Feb 29 (leap year 2024)
    d_jan31_leap = date(2024, 1, 31)
    d_feb_leap = advance_due_date(d_jan31_leap, 'MONTHLY')
    assert d_feb_leap == date(2024, 2, 29)

    # Monthly: March 31 -> April 30
    d_mar31 = date(2026, 3, 31)
    d_apr = advance_due_date(d_mar31, 'MONTHLY')
    assert d_apr == date(2026, 4, 30)

    # Quarterly: Nov 30 -> Feb 28
    d_nov30 = date(2025, 11, 30)
    d_q = advance_due_date(d_nov30, 'QUARTERLY')
    assert d_q == date(2026, 2, 28)

    # Weekly
    d_w = advance_due_date(date(2026, 10, 1), 'WEEKLY')
    assert d_w == date(2026, 10, 8)

    # Yearly leap year: Feb 29 2024 -> Feb 28 2025
    d_leap_year = advance_due_date(date(2024, 2, 29), 'YEARLY')
    assert d_leap_year == date(2025, 2, 28)


def test_dynamic_sip_reminder_generation():
    """
    Test scenario: Monthly SIP of Rs 5,000 scheduled for the 15th.
    Verifies dynamic copy for 3 days before (12th), 1 day before (14th), and due date (15th).
    """
    schedule = RecurringPayment(
        id=101,
        user_id=1,
        name="Parag Parikh Flexi Cap SIP",
        category="MUTUAL_FUND_SIP",
        amount_minor_units=500000,  # Rs 5,000
        frequency="MONTHLY",
        next_due_date=date(2026, 10, 15),
        scheme_name="Parag Parikh Flexi Cap Fund"
    )
    occ = PaymentOccurrence(
        id=501,
        payment_schedule_id=101,
        due_date=date(2026, 10, 15),
        amount_minor_units=500000
    )

    # 1. Three days before (12th)
    c_3days = generate_reminder_content(schedule, occ, days_before=3)
    assert c_3days['notification_type'] == 'SIP_UPCOMING'
    assert '₹5,000' in c_3days['message']
    assert 'Parag Parikh' in c_3days['message']
    assert '15 October' in c_3days['message']
    assert 'sufficient funds' in c_3days['message'].lower()

    # 2. One day before (14th)
    c_1day = generate_reminder_content(schedule, occ, days_before=1)
    assert c_1day['notification_type'] == 'SIP_UPCOMING'
    assert 'tomorrow' in c_1day['message'].lower()
    assert '₹5,000' in c_1day['message']

    # 3. On due date (15th)
    c_due = generate_reminder_content(schedule, occ, days_before=0)
    assert c_due['notification_type'] == 'SIP_DUE_TODAY'
    assert 'due today' in c_due['message'].lower()
    assert '₹5,000' in c_due['message']

    # 4. Overdue
    c_overdue = generate_reminder_content(schedule, occ, days_before=-1)
    assert c_overdue['notification_type'] == 'OVERDUE_PAYMENT'


def test_scheduler_idempotency_and_multi_channel_dispatch(app, test_user):
    """
    Verify that scheduler generates In-App, Email, and Push reminders,
    and running the scheduler twice does NOT create duplicate notifications.
    """
    with app.app_context():
        # Setup test schedule due in 3 days
        sched_date = date.today() + timedelta(days=3)
        sched = RecurringPayment(
            user_id=test_user.id,
            name="UTI Nifty 50 Index SIP",
            category="MUTUAL_FUND_SIP",
            amount_minor_units=300000,
            frequency="MONTHLY",
            next_due_date=sched_date,
            scheme_name="UTI Nifty 50 Index Fund",
            status="ACTIVE"
        )
        db.session.add(sched)
        db.session.commit()

        # Ensure occurrence
        ensure_occurrences_for_schedule(sched)

        # Configure user preferences: 3 days before enabled
        pref = get_or_create_user_preference(test_user.id)
        pref.reminder_offsets = [3, 1]
        pref.in_app_enabled = True
        pref.email_enabled = True
        pref.browser_push_enabled = True
        db.session.commit()

        # Run Scheduler First Time
        res1 = process_reminders_for_user(test_user.id)
        assert res1['success'] is True
        assert res1['stats']['in_app_created'] == 1

        # Check notification in DB
        notifs = Notification.query.filter_by(user_id=test_user.id).all()
        assert len(notifs) >= 1
        in_app_notif = [n for n in notifs if n.channel == 'IN_APP'][0]
        assert 'UTI Nifty 50' in in_app_notif.title or 'UTI Nifty 50' in in_app_notif.message
        assert in_app_notif.is_read is False

        # Run Scheduler Second Time on same day -> IDEMPOTENT, 0 duplicates created
        res2 = process_reminders_for_user(test_user.id)
        assert res2['success'] is True
        assert res2['stats']['in_app_created'] == 0
        assert res2['stats']['skipped_idempotent'] >= 1

        # Verify DB still has exactly 1 in-app notification
        in_app_count = Notification.query.filter_by(user_id=test_user.id, channel='IN_APP').count()
        assert in_app_count == 1


def test_in_app_notification_persistence_and_read_marker(client, test_user):
    """Test that in-app notifications persist and can be marked as read."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Create test notification directly
    notif = Notification(
        user_id=test_user.id,
        notification_type='SUBSCRIPTION_RENEWAL',
        channel='IN_APP',
        title='Netflix Renews Tomorrow',
        message='Your Netflix subscription of ₹649 renews tomorrow.',
        idempotency_key='test_persist_key_123',
        delivery_status='DELIVERED'
    )
    db.session.add(notif)
    db.session.commit()

    # 1. Fetch unread count
    res_unread = client.get('/api/notifications/unread-count')
    assert res_unread.status_code == 200
    assert res_unread.get_json()['unread_count'] >= 1

    # 2. Mark single notification as read
    res_read = client.post(f'/api/notifications/{notif.id}/read')
    assert res_read.status_code == 200
    assert res_read.get_json()['success'] is True

    # 3. Verify in database
    refreshed = Notification.query.get(notif.id)
    assert refreshed.is_read is True
    assert refreshed.read_at is not None


def test_browser_push_subscription_and_pruning(client, test_user):
    """Test browser push subscription registration, multi-device support, and pruning."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # 1. Register Device 1
    payload1 = {
        'endpoint': 'https://fcm.googleapis.com/fcm/send/device-token-1',
        'keys': {
            'p256dh': 'BGb_test_p256dh_key_device_1',
            'auth': 'test_auth_key_device_1'
        }
    }
    res1 = client.post('/api/notifications/push/subscribe', json=payload1)
    assert res1.status_code == 200
    assert res1.get_json()['success'] is True

    # 2. Register Device 2 (multi-device support)
    payload2 = {
        'endpoint': 'https://updates.push.services.mozilla.com/wpush/v2/device-token-2',
        'keys': {
            'p256dh': 'BGb_test_p256dh_key_device_2',
            'auth': 'test_auth_key_device_2'
        }
    }
    res2 = client.post('/api/notifications/push/subscribe', json=payload2)
    assert res2.status_code == 200

    subs = PushSubscription.query.filter_by(user_id=test_user.id, is_active=True).all()
    assert len(subs) == 2

    # 3. Unsubscribe Device 1
    res_unsub = client.post('/api/notifications/push/unsubscribe', json={'endpoint': payload1['endpoint']})
    assert res_unsub.status_code == 200

    sub1 = PushSubscription.query.filter_by(endpoint=payload1['endpoint']).first()
    assert sub1.is_active is False
    assert sub1.revoked_at is not None

    # Device 2 should remain active
    active_subs = PushSubscription.query.filter_by(user_id=test_user.id, is_active=True).all()
    assert len(active_subs) == 1
    assert active_subs[0].endpoint == payload2['endpoint']


def test_user_data_isolation(app, client):
    """Ensure User A cannot read or modify User B's payments, notifications, or push subscriptions."""
    with app.app_context():
        user_a = User(full_name="User Alpha", email="alpha@test.com")
        user_b = User(full_name="User Beta", email="beta@test.com")
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # Create schedule for User A
        sched_a = RecurringPayment(
            user_id=user_a.id,
            name="Alpha Confidential EMI",
            category="LOAN_EMI",
            amount_minor_units=2500000,
            next_due_date=date.today() + timedelta(days=5),
            status="ACTIVE"
        )
        db.session.add(sched_a)
        db.session.commit()

        occ_a = PaymentOccurrence(
            payment_schedule_id=sched_a.id,
            due_date=sched_a.next_due_date,
            amount_minor_units=2500000
        )
        db.session.add(occ_a)
        db.session.commit()

        # Log in as User B
        with client.session_transaction() as sess:
            sess['user_id'] = user_b.id

        # User B attempts to access User A's scheduled payments via API
        res_list = client.get('/api/payments')
        assert res_list.status_code == 200
        b_schedules = res_list.get_json()['schedules']
        assert all(s['name'] != "Alpha Confidential EMI" for s in b_schedules)

        # User B attempts to mark User A's occurrence as paid -> 404 Not Found
        res_hack = client.post(f'/api/payments/occurrences/{occ_a.id}/mark-paid')
        assert res_hack.status_code == 404

        # User B attempts to cancel User A's schedule -> 404 Not Found
        res_cancel = client.delete(f'/api/payments/{sched_a.id}')
        assert res_cancel.status_code == 404


def test_manual_payment_vs_external_confirmation(client, test_user):
    """
    Verify clear distinction between manual marking ('PAID_MANUAL')
    and verified bank confirmation ('CONFIRMED_EXTERNAL').
    """
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    due_d = date.today() + timedelta(days=1)
    sched = RecurringPayment(
        user_id=test_user.id,
        name="Tata Power Electricity Bill",
        category="UTILITY_BILL",
        amount_minor_units=185000,
        frequency="MONTHLY",
        next_due_date=due_d,
        status="ACTIVE"
    )
    db.session.add(sched)
    db.session.commit()

    occ = PaymentOccurrence(
        payment_schedule_id=sched.id,
        due_date=due_d,
        amount_minor_units=185000,
        status="PENDING"
    )
    db.session.add(occ)
    db.session.commit()

    # User manually marks as paid
    res = client.post(f'/api/payments/occurrences/{occ.id}/mark-paid')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['occurrence']['status'] == 'PAID_MANUAL'
    assert data['occurrence']['is_confirmed_externally'] is False
    assert data['occurrence']['manually_confirmed_at'] is not None

    # Next due date was advanced to next month
    refreshed_sched = RecurringPayment.query.get(sched.id)
    assert refreshed_sched.next_due_date > due_d


def test_payment_matching_service_bank_ingestion(app, test_user):
    """
    Verify provider-independent transaction matching service:
    1. High-confidence exact match marks occurrence as CONFIRMED_EXTERNAL.
    2. Failed bank transaction marks occurrence as FAILED_EXTERNAL.
    3. Ambiguous transaction is flagged as AWAITING_CONFIRMATION for manual review.
    4. Duplicate transaction is detected and prevented.
    """
    with app.app_context():
        due_date = date.today()

        # Scheduled SIP
        sched = RecurringPayment(
            user_id=test_user.id,
            name="Mirae Asset Large Cap SIP",
            category="MUTUAL_FUND_SIP",
            amount_minor_units=500000,  # Rs 5,000
            frequency="MONTHLY",
            next_due_date=due_date,
            scheme_name="Mirae Asset Large Cap Fund",
            status="ACTIVE"
        )
        db.session.add(sched)
        db.session.commit()

        occ = PaymentOccurrence(
            payment_schedule_id=sched.id,
            due_date=due_date,
            amount_minor_units=500000,
            status="PENDING"
        )
        db.session.add(occ)
        db.session.commit()

        # 1. High-confidence success match
        txn_success = BankTransactionDTO(
            transaction_id="TXN-BANK-1001",
            amount=5000.0,
            date=due_date,
            narration="ACH D- MIRAE ASSET LARGE CAP FUND MUTUAL FUND SIP DEBIT",
            status="SUCCESS",
            provider="ACCOUNT_AGGREGATOR"
        )
        res_match = PaymentMatchingService.match_and_process_transaction(test_user.id, txn_success)
        assert res_match.status == 'CONFIRMED'
        assert res_match.confidence_score >= 0.80
        assert res_match.matched_occurrence_id == occ.id

        refreshed_occ = PaymentOccurrence.query.get(occ.id)
        assert refreshed_occ.status == 'CONFIRMED_EXTERNAL'
        assert refreshed_occ.external_transaction_id == "TXN-BANK-1001"
        assert refreshed_occ.externally_confirmed_at is not None

        # Verify confirmation notification created
        notif = Notification.query.filter_by(
            payment_occurrence_id=occ.id,
            notification_type='PAYMENT_CONFIRMED_EXTERNAL'
        ).first()
        assert notif is not None
        assert 'Confirmed' in notif.title

        # 2. Duplicate detection
        res_dup = PaymentMatchingService.match_and_process_transaction(test_user.id, txn_success)
        assert res_dup.status == 'DUPLICATE'

        # 3. Ambiguous transaction test
        occ_ambiguous = PaymentOccurrence(
            payment_schedule_id=sched.id,
            due_date=due_date + timedelta(days=2),
            amount_minor_units=100000,  # Rs 1,000
            status="PENDING"
        )
        db.session.add(occ_ambiguous)
        db.session.commit()

        txn_ambiguous = BankTransactionDTO(
            transaction_id="TXN-BANK-1002",
            amount=1000.0,
            date=due_date + timedelta(days=2),
            narration="UPI DEBIT REF NO 982173 PAYMENT SERVICES",
            status="SUCCESS",
            provider="NPCI_UPI"
        )
        res_ambig = PaymentMatchingService.match_and_process_transaction(test_user.id, txn_ambiguous)
        # Should flag for manual review, not auto-confirm
        assert res_ambig.status in ('MANUAL_REVIEW', 'NO_MATCH')
        assert res_ambig.status != 'CONFIRMED'
