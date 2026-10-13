from datetime import datetime
from app.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    name = db.Column(db.String(80), nullable=False)
    budget_group = db.Column(db.String(20), nullable=False)  # 'NEEDS', 'WANTS', 'SAVINGS', 'INCOME'
    transaction_type = db.Column(db.String(30), default='EXPENSE', nullable=False, index=True)
    # Supported: 'EXPENSE', 'INCOME', 'SAVINGS_CONTRIBUTION', 'TRANSFER', 'DEBT_REPAYMENT', 'REFUND', 'ALL'
    description = db.Column(db.String(255), default='')
    icon = db.Column(db.String(50), default='tag')
    color = db.Column(db.String(20), default='#161917')
    monthly_budget_minor_units = db.Column(db.BigInteger, nullable=True)  # Optional category cap
    is_active = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    recurring_payments = db.relationship('RecurringPayment', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'budget_group': self.budget_group,
            'transaction_type': self.transaction_type or 'EXPENSE',
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'monthly_budget_minor_units': self.monthly_budget_minor_units,
            'is_active': self.is_active,
            'is_pinned': self.is_pinned,
            'display_order': self.display_order,
            'is_default': self.is_default,
            'is_archived': self.is_archived,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_system': self.user_id is None
        }


class CategoryPreference(db.Model):
    __tablename__ = 'category_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_type = db.Column(db.String(30), nullable=False, index=True)
    default_category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'transaction_type', name='uq_user_txn_pref'),
    )

    # Relationship
    default_category = db.relationship('Category', foreign_keys=[default_category_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'default_category_id': self.default_category_id
        }
