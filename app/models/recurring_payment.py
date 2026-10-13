from datetime import datetime, date
from app.extensions import db

class RecurringPayment(db.Model):
    __tablename__ = 'recurring_payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    frequency = db.Column(db.String(20), default='MONTHLY', nullable=False)  # 'MONTHLY', 'YEARLY', 'WEEKLY', 'QUARTERLY'
    next_due_date = db.Column(db.Date, nullable=False, default=date.today)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), default='ACTIVE')  # 'ACTIVE', 'PAUSED', 'CANCELLED'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='recurring_rule', lazy='dynamic')

    @property
    def monthly_equivalent_minor_units(self) -> int:
        freq = self.frequency.upper()
        if freq == 'MONTHLY':
            return self.amount_minor_units
        elif freq == 'YEARLY':
            return self.amount_minor_units // 12
        elif freq == 'WEEKLY':
            return int((self.amount_minor_units * 52) / 12)
        elif freq == 'QUARTERLY':
            return self.amount_minor_units // 3
        return self.amount_minor_units

    @property
    def annual_cost_minor_units(self) -> int:
        return self.monthly_equivalent_minor_units * 12

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'amount_minor_units': self.amount_minor_units,
            'frequency': self.frequency,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Uncategorized',
            'status': self.status,
            'monthly_equivalent_minor_units': self.monthly_equivalent_minor_units,
            'annual_cost_minor_units': self.annual_cost_minor_units,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
