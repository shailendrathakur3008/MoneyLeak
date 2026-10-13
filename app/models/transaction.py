from datetime import datetime, date
from app.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    transaction_type = db.Column(db.String(30), default='EXPENSE', nullable=False, index=True)
    # Types: 'EXPENSE', 'INCOME', 'REFUND', 'TRANSFER', 'SAVINGS_CONTRIBUTION', 'DEBT_REPAYMENT'
    transaction_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    description = db.Column(db.String(200), nullable=False)
    merchant = db.Column(db.String(120), default='')
    notes = db.Column(db.Text, default='')
    recurring_rule_id = db.Column(db.Integer, db.ForeignKey('recurring_payments.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Uncategorized',
            'budget_group': self.category.budget_group if self.category else 'WANTS',
            'amount_minor_units': self.amount_minor_units,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'description': self.description,
            'merchant': self.merchant,
            'notes': self.notes,
            'recurring_rule_id': self.recurring_rule_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
