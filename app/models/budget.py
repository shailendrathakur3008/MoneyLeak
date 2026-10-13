from datetime import datetime
from app.extensions import db

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    period = db.Column(db.String(20), default='DEFAULT', nullable=False)
    needs_percentage = db.Column(db.Float, default=50.0, nullable=False)
    wants_percentage = db.Column(db.Float, default=30.0, nullable=False)
    savings_percentage = db.Column(db.Float, default=20.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period': self.period,
            'needs_percentage': self.needs_percentage,
            'wants_percentage': self.wants_percentage,
            'savings_percentage': self.savings_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
