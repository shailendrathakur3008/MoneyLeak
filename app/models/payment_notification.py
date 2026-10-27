from datetime import datetime, date
import json
from app.extensions import db

class PaymentOccurrence(db.Model):
    """
    Tracks individual scheduled installments or payment occurrences for a PaymentSchedule / RecurringPayment.
    Enables tracking of due dates, manual confirmation, external bank confirmation, and delivery status.
    """
    __tablename__ = 'payment_occurrences'

    id = db.Column(db.Integer, primary_key=True)
    payment_schedule_id = db.Column(
        db.Integer,
        db.ForeignKey('recurring_payments.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    due_date = db.Column(db.Date, nullable=False, index=True)
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    status = db.Column(
        db.String(30),
        default='PENDING',
        nullable=False,
        index=True
    )  # 'PENDING', 'AWAITING_CONFIRMATION', 'PAID_MANUAL', 'CONFIRMED_EXTERNAL', 'FAILED_EXTERNAL', 'OVERDUE', 'CANCELLED'

    manually_confirmed_at = db.Column(db.DateTime, nullable=True)
    externally_confirmed_at = db.Column(db.DateTime, nullable=True)
    external_transaction_id = db.Column(db.String(150), nullable=True)
    external_provider = db.Column(db.String(80), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notifications = db.relationship('Notification', backref='occurrence', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def amount(self) -> float:
        return round(self.amount_minor_units / 100.0, 2)

    @amount.setter
    def amount(self, val: float):
        self.amount_minor_units = int(round(float(val) * 100))

    @property
    def is_paid(self) -> bool:
        return self.status in ('PAID_MANUAL', 'CONFIRMED_EXTERNAL')

    @property
    def is_confirmed_externally(self) -> bool:
        return self.status == 'CONFIRMED_EXTERNAL'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        sched = self.schedule
        return {
            'id': self.id,
            'payment_schedule_id': self.payment_schedule_id,
            'payment_name': sched.name if sched else 'Scheduled Payment',
            'category': sched.category if sched else 'CUSTOM',
            'scheme_name': sched.scheme_name if sched else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'amount': self.amount,
            'amount_minor_units': self.amount_minor_units,
            'currency': sched.currency if sched else 'INR',
            'status': self.status,
            'is_paid': self.is_paid,
            'is_confirmed_externally': self.is_confirmed_externally,
            'manually_confirmed_at': self.manually_confirmed_at.isoformat() if self.manually_confirmed_at else None,
            'externally_confirmed_at': self.externally_confirmed_at.isoformat() if self.externally_confirmed_at else None,
            'external_transaction_id': self.external_transaction_id,
            'external_provider': self.external_provider,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Notification(db.Model):
    """
    Stores multi-channel reminders and updates across In-App, Email, and Browser Push channels.
    Enforces idempotency keys to completely eliminate duplicate notifications.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    payment_occurrence_id = db.Column(
        db.Integer,
        db.ForeignKey('payment_occurrences.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    payment_schedule_id = db.Column(
        db.Integer,
        db.ForeignKey('recurring_payments.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    notification_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )  # 'SIP_UPCOMING', 'SIP_DUE_TODAY', 'SUBSCRIPTION_RENEWAL', 'EMI_DUE', 'BILL_DUE', 'OVERDUE_PAYMENT', 'PAYMENT_PAID_MANUAL', 'PAYMENT_CONFIRMED_EXTERNAL', 'PAYMENT_FAILED_EXTERNAL', 'SYSTEM'

    channel = db.Column(db.String(30), default='IN_APP', nullable=False)  # 'IN_APP', 'EMAIL', 'BROWSER_PUSH'
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(255), nullable=True)

    scheduled_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)

    delivery_status = db.Column(
        db.String(50),
        default='PENDING',
        nullable=False,
        index=True
    )  # 'PENDING', 'DELIVERED', 'FAILED', 'PROVIDER_NOT_CONFIGURED', 'SKIPPED_QUIET_HOURS'

    provider_message_id = db.Column(db.String(255), nullable=True)
    error_details = db.Column(db.Text, nullable=True)
    idempotency_key = db.Column(db.String(255), unique=True, nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def mark_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'payment_occurrence_id': self.payment_occurrence_id,
            'payment_schedule_id': self.payment_schedule_id,
            'notification_type': self.notification_type,
            'channel': self.channel,
            'title': self.title,
            'message': self.message,
            'link_url': self.link_url or '/payments',
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_read': self.is_read,
            'delivery_status': self.delivery_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NotificationPreference(db.Model):
    """
    Stores user notification preferences across channels, reminder day timings, quiet hours, and categories.
    """
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        index=True
    )

    # Channels
    in_app_enabled = db.Column(db.Boolean, default=True, nullable=False)
    email_enabled = db.Column(db.Boolean, default=True, nullable=False)
    browser_push_enabled = db.Column(db.Boolean, default=True, nullable=False)

    # Timing: JSON list of integer days before due date to remind (e.g., [7, 3, 1])
    reminder_days_before = db.Column(db.String(100), default='[3, 1]', nullable=False)
    reminder_on_due_date = db.Column(db.Boolean, default=True, nullable=False)

    # Quiet Hours & Timezone
    quiet_hours_enabled = db.Column(db.Boolean, default=False, nullable=False)
    quiet_hours_start = db.Column(db.String(10), default='22:00', nullable=False)
    quiet_hours_end = db.Column(db.String(10), default='08:00', nullable=False)
    timezone = db.Column(db.String(50), default='Asia/Kolkata', nullable=False)

    # Category filters
    category_sip_enabled = db.Column(db.Boolean, default=True, nullable=False)
    category_subscription_enabled = db.Column(db.Boolean, default=True, nullable=False)
    category_emi_enabled = db.Column(db.Boolean, default=True, nullable=False)
    category_bill_enabled = db.Column(db.Boolean, default=True, nullable=False)
    category_insurance_enabled = db.Column(db.Boolean, default=True, nullable=False)
    category_other_enabled = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('notification_preference', uselist=False, cascade='all, delete-orphan'))

    @property
    def reminder_offsets(self) -> list[int]:
        try:
            return json.loads(self.reminder_days_before or '[3, 1]')
        except Exception:
            return [3, 1]

    @reminder_offsets.setter
    def reminder_offsets(self, offsets: list[int]):
        cleaned = sorted(list(set(int(x) for x in offsets if isinstance(x, (int, str)) and str(x).isdigit())), reverse=True)
        self.reminder_days_before = json.dumps(cleaned)

    def is_category_enabled(self, category: str) -> bool:
        cat_upper = (category or 'CUSTOM').upper()
        if 'SIP' in cat_upper or 'INVESTMENT' in cat_upper:
            return self.category_sip_enabled
        if 'SUBSCRIPTION' in cat_upper:
            return self.category_subscription_enabled
        if 'EMI' in cat_upper or 'LOAN' in cat_upper:
            return self.category_emi_enabled
        if 'BILL' in cat_upper or 'UTILITY' in cat_upper or 'TELECOM' in cat_upper or 'RENT' in cat_upper:
            return self.category_bill_enabled
        if 'INSURANCE' in cat_upper:
            return self.category_insurance_enabled
        return self.category_other_enabled

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'in_app_enabled': self.in_app_enabled,
            'email_enabled': self.email_enabled,
            'browser_push_enabled': self.browser_push_enabled,
            'reminder_days_before': self.reminder_offsets,
            'reminder_on_due_date': self.reminder_on_due_date,
            'quiet_hours_enabled': self.quiet_hours_enabled,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'timezone': self.timezone,
            'category_sip_enabled': self.category_sip_enabled,
            'category_subscription_enabled': self.category_subscription_enabled,
            'category_emi_enabled': self.category_emi_enabled,
            'category_bill_enabled': self.category_bill_enabled,
            'category_insurance_enabled': self.category_insurance_enabled,
            'category_other_enabled': self.category_other_enabled
        }


class PushSubscription(db.Model):
    """
    Stores browser push subscription endpoints and VAPID crypto keys per device/browser for a user.
    """
    __tablename__ = 'push_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    endpoint = db.Column(db.Text, unique=True, nullable=False)
    p256dh_key = db.Column(db.String(255), nullable=False)
    auth_key = db.Column(db.String(255), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)

    # Relationship
    user = db.relationship('User', backref=db.backref('push_subscriptions', lazy='dynamic', cascade='all, delete-orphan'))

    def to_webpush_subscription_info(self) -> dict:
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh_key,
                'auth': self.auth_key
            }
        }
