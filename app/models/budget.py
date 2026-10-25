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

    def __init__(
        self,
        user_id: int | None = None,
        period: str = 'DEFAULT',
        needs_percentage: float = 50.0,
        wants_percentage: float = 30.0,
        savings_percentage: float = 20.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        self.period = period
        self.needs_percentage = needs_percentage
        self.wants_percentage = wants_percentage
        self.savings_percentage = savings_percentage

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


class MonthlyBudget(db.Model):
    """
    Monthly Budget Record.
    Stores the permanent history of monthly budget allocations for a user.
    Enforces a strict unique constraint on (user_id, year, month).
    Carries forward previous months' budgets without automatic alteration.
    """
    __tablename__ = 'monthly_budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    budget_amount_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    source_month = db.Column(db.String(20), nullable=True)  # e.g. "2026-10" if carried forward
    is_manually_set = db.Column(db.Boolean, default=False, nullable=False)
    confirmation_status = db.Column(db.String(30), default='pending', nullable=False)
    # Allowed statuses: 'pending', 'confirmed_new', 'confirmed_retained', 'postponed', 'dismissed'
    prompt_shown_at = db.Column(db.DateTime, nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'year', 'month', name='uq_user_monthly_budget'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'year': self.year,
            'month': self.month,
            'budget_amount_minor_units': self.budget_amount_minor_units,
            'budget_amount': self.budget_amount_minor_units / 100.0,
            'source_month': self.source_month,
            'is_manually_set': self.is_manually_set,
            'confirmation_status': self.confirmation_status,
            'prompt_shown_at': self.prompt_shown_at.isoformat() if self.prompt_shown_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

