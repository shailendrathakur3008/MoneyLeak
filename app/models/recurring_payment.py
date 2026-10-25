from datetime import datetime, date
from app.extensions import db

class RecurringPayment(db.Model):
    """
    Scheduled payment / recurring rule representing recurring obligations:
    SIPs, Subscriptions, EMIs, Utility Bills, Credit Cards, Insurance, Rent, Education, etc.
    """
    __tablename__ = 'recurring_payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    currency = db.Column(db.String(10), default='INR', nullable=False)
    frequency = db.Column(db.String(20), default='MONTHLY', nullable=False)  # 'ONCE', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY'
    next_due_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)

    category = db.Column(db.String(50), default='CUSTOM', nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), default='ACTIVE', nullable=False, index=True)  # 'ACTIVE', 'PAUSED', 'CANCELLED', 'COMPLETED'

    scheme_name = db.Column(db.String(200), nullable=True)
    scheme_id = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    reminder_preferences_override = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='recurring_rule', lazy='dynamic')
    occurrences = db.relationship('PaymentOccurrence', backref='schedule', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='schedule', lazy='dynamic')

    def __init__(self, **kwargs):
        # Support payment_name and amount kwargs
        if 'payment_name' in kwargs and 'name' not in kwargs:
            kwargs['name'] = kwargs.pop('payment_name')
        if 'amount' in kwargs and 'amount_minor_units' not in kwargs:
            kwargs['amount_minor_units'] = int(round(float(kwargs.pop('amount')) * 100))
        super().__init__(**kwargs)

    @property
    def payment_name(self) -> str:
        return self.name

    @payment_name.setter
    def payment_name(self, val: str):
        self.name = val

    @property
    def amount(self) -> float:
        return round(self.amount_minor_units / 100.0, 2)

    @amount.setter
    def amount(self, val: float):
        self.amount_minor_units = int(round(float(val) * 100))

    @property
    def monthly_equivalent_minor_units(self) -> int:
        freq = (self.frequency or 'MONTHLY').upper()
        if freq == 'MONTHLY':
            return self.amount_minor_units
        elif freq == 'YEARLY':
            return self.amount_minor_units // 12
        elif freq == 'WEEKLY':
            return int((self.amount_minor_units * 52) / 12)
        elif freq == 'QUARTERLY':
            return self.amount_minor_units // 3
        elif freq == 'ONCE':
            return self.amount_minor_units
        return self.amount_minor_units

    @property
    def annual_cost_minor_units(self) -> int:
        return self.monthly_equivalent_minor_units * 12

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'payment_name': self.name,
            'category': self.category or 'CUSTOM',
            'amount': self.amount,
            'amount_minor_units': self.amount_minor_units,
            'currency': self.currency or 'INR',
            'frequency': self.frequency,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'category_id': self.category_id,
            'category_name': self.category_rel.name if getattr(self, 'category_rel', None) else (self.category.name if getattr(self, 'category', None) and hasattr(self.category, 'name') else self.category),
            'status': self.status,
            'scheme_name': self.scheme_name,
            'scheme_id': self.scheme_id,
            'notes': self.notes,
            'monthly_equivalent_minor_units': self.monthly_equivalent_minor_units,
            'annual_cost_minor_units': self.annual_cost_minor_units,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Architectural alias: PaymentSchedule and RecurringPayment refer to the same unified schedule model
PaymentSchedule = RecurringPayment
