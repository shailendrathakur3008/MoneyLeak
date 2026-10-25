from datetime import datetime, date
from app.extensions import db

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    target_amount_minor_units = db.Column(db.BigInteger, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    category_type = db.Column(db.String(50), default='EMERGENCY_FUND')
    # Types: 'EMERGENCY_FUND', 'EDUCATION', 'TRAVEL', 'VEHICLE', 'HOME', 'GADGET', 'OTHER'
    status = db.Column(db.String(20), default='ACTIVE')  # 'ACTIVE', 'COMPLETED', 'PAUSED'
    icon = db.Column(db.String(50), default='piggy-bank')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    contributions = db.relationship('GoalContribution', backref='goal', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_contributed_minor_units(self) -> int:
        return sum(c.amount_minor_units for c in self.contributions)

    def to_dict(self):
        contributed = self.total_contributed_minor_units
        remaining = max(0, self.target_amount_minor_units - contributed)
        progress = (contributed / self.target_amount_minor_units * 100.0) if self.target_amount_minor_units > 0 else 0.0
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'target_amount_minor_units': self.target_amount_minor_units,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'category_type': self.category_type,
            'status': self.status,
            'icon': self.icon,
            'contributed_minor_units': contributed,
            'remaining_minor_units': remaining,
            'progress_percentage': round(min(progress, 100.0), 1),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GoalContribution(db.Model):
    __tablename__ = 'goal_contributions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('savings_goals.id', ondelete='CASCADE'), nullable=False, index=True)
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    contribution_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_id': self.goal_id,
            'amount_minor_units': self.amount_minor_units,
            'contribution_date': self.contribution_date.isoformat() if self.contribution_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
