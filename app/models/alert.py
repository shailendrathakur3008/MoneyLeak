from datetime import datetime
import json
from app.extensions import db

class FinancialAlert(db.Model):
    __tablename__ = 'financial_alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'BUDGET_OVERRUN', 'SPENDING_INCREASE', 'RECURRING_DRAIN', 'UNUSUAL_TRANSACTION', 'SAVINGS_GAP', 'LIFESTYLE_INFLATION'
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='WARNING')  # 'INFO', 'WARNING', 'DANGER'
    supporting_data_json = db.Column(db.Text, default='{}')
    is_dismissed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    dismissed_at = db.Column(db.DateTime, nullable=True)

    @property
    def supporting_data(self):
        try:
            return json.loads(self.supporting_data_json or '{}')
        except Exception:
            return {}

    @supporting_data.setter
    def supporting_data(self, val):
        self.supporting_data_json = json.dumps(val or {})

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'supporting_data': self.supporting_data,
            'is_dismissed': self.is_dismissed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None
        }
