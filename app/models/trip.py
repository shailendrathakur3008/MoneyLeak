from datetime import datetime, date
import json
from app.extensions import db


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    starting_city = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    duration_days = db.Column(db.Integer, default=1, nullable=False)
    travellers_count = db.Column(db.Integer, default=1, nullable=False)

    # Style and preferences
    travel_style = db.Column(db.String(30), default='STANDARD', nullable=False)  # 'BUDGET', 'STANDARD', 'PREMIUM'
    transport_mode = db.Column(db.String(30), default='TRAIN', nullable=False)   # 'TRAIN', 'BUS', 'FLIGHT', 'CAR', 'TWO_WHEELER'
    accommodation_type = db.Column(db.String(50), default='STANDARD_HOTEL', nullable=False)
    trip_nature = db.Column(db.String(30), default='PLANNED', nullable=False)    # 'SPONTANEOUS', 'PLANNED'

    # Financial figures
    total_budget_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    custom_budget_target_minor_units = db.Column(db.BigInteger, nullable=True)

    # Serialized JSON dictionary of category estimates
    category_estimates_json = db.Column(db.Text, default='{}', nullable=False)

    status = db.Column(db.String(20), default='PLANNING', nullable=False)  # 'PLANNING', 'ACTIVE', 'COMPLETED', 'CANCELLED'
    notes = db.Column(db.Text, default='')
    booking_links = db.Column(db.Text, default='')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to transactions
    transactions = db.relationship('Transaction', backref='trip', lazy=True)

    @property
    def category_estimates(self) -> dict:
        try:
            return json.loads(self.category_estimates_json or '{}')
        except Exception:
            return {}

    @category_estimates.setter
    def category_estimates(self, val: dict):
        self.category_estimates_json = json.dumps(val or {})

    @property
    def actual_spending_minor_units(self) -> int:
        """Sum of linked expense transactions minus refunds."""
        total = 0
        for txn in self.transactions:
            t_type = (txn.transaction_type or '').upper()
            if t_type == 'EXPENSE':
                total += txn.amount_minor_units
            elif t_type == 'REFUND':
                total -= txn.amount_minor_units
        return max(0, total)

    @property
    def remaining_budget_minor_units(self) -> int:
        """Remaining budget in minor units."""
        return max(0, self.total_budget_minor_units - self.actual_spending_minor_units)

    @property
    def budget_progress_pct(self) -> float:
        """Percentage of budget spent."""
        if self.total_budget_minor_units <= 0:
            return 0.0
        return round(min(100.0, (self.actual_spending_minor_units / self.total_budget_minor_units) * 100.0), 1)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'starting_city': self.starting_city,
            'destination': self.destination,
            'departure_date': self.departure_date.isoformat() if self.departure_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'duration_days': self.duration_days,
            'travellers_count': self.travellers_count,
            'travel_style': self.travel_style,
            'transport_mode': self.transport_mode,
            'accommodation_type': self.accommodation_type,
            'trip_nature': self.trip_nature,
            'total_budget_minor_units': self.total_budget_minor_units,
            'custom_budget_target_minor_units': self.custom_budget_target_minor_units,
            'category_estimates': self.category_estimates,
            'actual_spending_minor_units': self.actual_spending_minor_units,
            'remaining_budget_minor_units': self.remaining_budget_minor_units,
            'budget_progress_pct': self.budget_progress_pct,
            'status': self.status,
            'notes': self.notes,
            'booking_links': self.booking_links,
            'linked_transactions_count': len(self.transactions),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
