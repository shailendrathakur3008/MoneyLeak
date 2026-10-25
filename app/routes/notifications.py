"""
Notification Center and Push Notification Management Routes for MoneyLeak.

Endpoints:
- GET /notifications: Notification Center web view
- GET /api/notifications: Paginated notifications query with category filtering
- GET /api/notifications/unread-count: Real-time unread badge counter
- POST /api/notifications/<id>/read: Single notification read marker
- POST /api/notifications/mark-all-read: Bulk mark as read
- POST /api/notifications/clear-all: Clear read notifications
- GET /api/notifications/vapid-public-key: Public key for Service Worker subscription
- POST /api/notifications/push/subscribe: Save browser Web Push subscription
- POST /api/notifications/push/unsubscribe: Revoke browser Web Push subscription
- POST /api/notifications/push/test: Test browser push dispatch
- GET /api/notifications/preferences: Get user reminder preferences
- POST /api/notifications/preferences: Save user reminder preferences
"""
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, g, session, send_from_directory, current_app
from app.extensions import db
from app.routes.auth import login_required
from app.models.payment_notification import (
    Notification,
    NotificationPreference,
    PushSubscription
)
from app.services.scheduler_service import get_or_create_user_preference
from app.services.push_service import (
    get_vapid_public_key,
    send_web_push
)

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/sw.js')
def service_worker():
    """Serves the Service Worker from site root with proper Service-Worker-Allowed scope."""
    response = send_from_directory(current_app.static_folder, 'sw.js', mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@notifications_bp.route('/notifications')
@login_required
def view_notifications():
    """Renders the dedicated Notification Center page."""
    user = g.current_user
    pref = get_or_create_user_preference(user.id)
    return render_template(
        'notifications.html',
        user=user,
        preferences=pref.to_dict(),
        vapid_public_key=get_vapid_public_key()
    )


@notifications_bp.route('/api/notifications', methods=['GET'])
@login_required
def api_get_notifications():
    """Retrieve notifications with channel, category, or read status filters."""
    user = g.current_user
    filter_type = request.args.get('filter', 'all').lower()
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(50, max(5, request.args.get('per_page', 20, type=int)))

    query = Notification.query.filter_by(user_id=user.id)

    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'reminders':
        query = query.filter(
            Notification.notification_type.in_([
                'SIP_UPCOMING', 'SIP_DUE_TODAY', 'SUBSCRIPTION_RENEWAL',
                'EMI_DUE', 'BILL_DUE', 'OVERDUE_PAYMENT'
            ])
        )
    elif filter_type == 'updates':
        query = query.filter(
            Notification.notification_type.in_([
                'PAYMENT_PAID_MANUAL', 'PAYMENT_CONFIRMED_EXTERNAL', 'PAYMENT_FAILED_EXTERNAL'
            ])
        )
    elif filter_type == 'system':
        query = query.filter_by(notification_type='SYSTEM')

    total = query.count()
    items = query.order_by(Notification.scheduled_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()

    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'unread_count': unread_count
    })


@notifications_bp.route('/api/notifications/unread-count', methods=['GET'])
@login_required
def api_unread_count():
    """Returns unread notification badge count."""
    user = g.current_user
    count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    return jsonify({'success': True, 'unread_count': count})


@notifications_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def api_mark_single_read(notif_id: int):
    """Mark an individual notification as read."""
    user = g.current_user
    notif = Notification.query.filter_by(id=notif_id, user_id=user.id).first()
    if not notif:
        return jsonify({'success': False, 'error': 'Notification not found.'}), 404

    notif.mark_read()
    db.session.commit()
    return jsonify({'success': True, 'notification': notif.to_dict()})


@notifications_bp.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def api_mark_all_read():
    """Mark all unread notifications as read for current user."""
    user = g.current_user
    now = datetime.utcnow()
    Notification.query.filter_by(user_id=user.id, is_read=False).update(
        {'is_read': True, 'read_at': now},
        synchronize_session=False
    )
    db.session.commit()
    return jsonify({'success': True, 'message': 'All notifications marked as read.'})


@notifications_bp.route('/api/notifications/clear-all', methods=['POST'])
@login_required
def api_clear_read_notifications():
    """Delete all read notifications for current user."""
    user = g.current_user
    Notification.query.filter_by(user_id=user.id, is_read=True).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Read notifications cleared.'})


# -----------------------------------------------------------------------------
# BROWSER WEB PUSH SUBSCRIPTION ENDPOINTS
# -----------------------------------------------------------------------------

@notifications_bp.route('/api/notifications/vapid-public-key', methods=['GET'])
@login_required
def api_vapid_public_key():
    """Returns the base64 URL-safe VAPID application server public key."""
    return jsonify({
        'success': True,
        'public_key': get_vapid_public_key()
    })


@notifications_bp.route('/api/notifications/push/subscribe', methods=['POST'])
@login_required
def api_push_subscribe():
    """Registers a browser PushSubscription with VAPID crypto keys for the user."""
    user = g.current_user
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()
    keys = data.get('keys') or {}
    p256dh = keys.get('p256dh') or data.get('p256dh')
    auth = keys.get('auth') or data.get('auth')

    if not endpoint or not p256dh or not auth:
        return jsonify({'success': False, 'error': 'Invalid push subscription payload.'}), 400

    # User-agent metadata
    ua = request.headers.get('User-Agent', '')[:250]

    sub = PushSubscription.query.filter_by(endpoint=endpoint).first()
    if sub:
        sub.user_id = user.id
        sub.p256dh_key = p256dh
        sub.auth_key = auth
        sub.user_agent = ua
        sub.is_active = True
        sub.revoked_at = None
        sub.last_used_at = datetime.utcnow()
    else:
        sub = PushSubscription(
            user_id=user.id,
            endpoint=endpoint,
            p256dh_key=p256dh,
            auth_key=auth,
            user_agent=ua,
            is_active=True
        )
        db.session.add(sub)

    # Automatically enable browser push in user preferences
    pref = get_or_create_user_preference(user.id)
    pref.browser_push_enabled = True

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Browser push notifications successfully registered and enabled.'
    })


@notifications_bp.route('/api/notifications/push/unsubscribe', methods=['POST'])
@login_required
def api_push_unsubscribe():
    """Revokes an active browser PushSubscription."""
    user = g.current_user
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()

    if endpoint:
        sub = PushSubscription.query.filter_by(endpoint=endpoint, user_id=user.id).first()
        if sub:
            sub.is_active = False
            sub.revoked_at = datetime.utcnow()
            db.session.commit()

    return jsonify({'success': True, 'message': 'Browser push subscription removed.'})


@notifications_bp.route('/api/notifications/push/test', methods=['POST'])
@login_required
def api_push_test():
    """Dispatches a test browser push notification to the user's active devices."""
    user = g.current_user
    subs = PushSubscription.query.filter_by(user_id=user.id, is_active=True).all()

    if not subs:
        return jsonify({
            'success': False,
            'error': 'No active browser push subscription found on this account. Enable notifications first.'
        }), 400

    payload = {
        'title': 'Test Push Notification',
        'body': 'MoneyLeak browser push notifications are active and working!',
        'icon': '/static/icons/icon-192.png',
        'badge': '/static/icons/badge-72.png',
        'data': {'url': '/notifications'}
    }

    results = []
    delivered_any = False
    for sub in subs:
        ok, msg = send_web_push(sub, payload)
        results.append({'endpoint': sub.endpoint[:30] + '...', 'delivered': ok, 'message': msg})
        if ok:
            delivered_any = True

    return jsonify({
        'success': delivered_any,
        'results': results,
        'message': 'Test push dispatched.' if delivered_any else 'Failed to deliver push to registered endpoints.'
    })


# -----------------------------------------------------------------------------
# USER NOTIFICATION PREFERENCES ENDPOINTS
# -----------------------------------------------------------------------------

@notifications_bp.route('/api/notifications/preferences', methods=['GET', 'POST'])
@login_required
def api_notification_preferences():
    """Get or update user notification preferences."""
    user = g.current_user
    pref = get_or_create_user_preference(user.id)

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}

        if 'in_app_enabled' in data:
            pref.in_app_enabled = bool(data['in_app_enabled'])
        if 'email_enabled' in data:
            pref.email_enabled = bool(data['email_enabled'])
        if 'browser_push_enabled' in data:
            pref.browser_push_enabled = bool(data['browser_push_enabled'])

        if 'reminder_days_before' in data:
            pref.reminder_offsets = data['reminder_days_before']
        if 'reminder_on_due_date' in data:
            pref.reminder_on_due_date = bool(data['reminder_on_due_date'])

        if 'quiet_hours_enabled' in data:
            pref.quiet_hours_enabled = bool(data['quiet_hours_enabled'])
        if 'quiet_hours_start' in data:
            pref.quiet_hours_start = str(data['quiet_hours_start'])[:10]
        if 'quiet_hours_end' in data:
            pref.quiet_hours_end = str(data['quiet_hours_end'])[:10]
        if 'timezone' in data:
            pref.timezone = str(data['timezone'])[:50]

        if 'category_sip_enabled' in data:
            pref.category_sip_enabled = bool(data['category_sip_enabled'])
        if 'category_subscription_enabled' in data:
            pref.category_subscription_enabled = bool(data['category_subscription_enabled'])
        if 'category_emi_enabled' in data:
            pref.category_emi_enabled = bool(data['category_emi_enabled'])
        if 'category_bill_enabled' in data:
            pref.category_bill_enabled = bool(data['category_bill_enabled'])
        if 'category_insurance_enabled' in data:
            pref.category_insurance_enabled = bool(data['category_insurance_enabled'])
        if 'category_other_enabled' in data:
            pref.category_other_enabled = bool(data['category_other_enabled'])

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Notification preferences saved.',
            'preferences': pref.to_dict()
        })

    return jsonify({
        'success': True,
        'preferences': pref.to_dict()
    })
