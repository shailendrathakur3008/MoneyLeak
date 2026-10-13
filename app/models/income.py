from datetime import datetime, date
from app.extensions import db

class IncomeRecord(db.Model):
    __tablename__ = 'income_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    income_source = db.Column(db.String(120), nullable=False)
    received_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount_minor_units': self.amount_minor_units,
            'income_source': self.income_source,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
