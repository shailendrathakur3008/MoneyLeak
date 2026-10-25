from datetime import datetime
import json
from app.extensions import db

class Simulation(db.Model):
    __tablename__ = 'simulations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    baseline_period = db.Column(db.String(20), default='CURRENT')
    scenario_data_json = db.Column(db.Text, nullable=False, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def scenario_data(self):
        try:
            return json.loads(self.scenario_data_json or '{}')
        except Exception:
            return {}

    @scenario_data.setter
    def scenario_data(self, val):
        self.scenario_data_json = json.dumps(val or {})

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'baseline_period': self.baseline_period,
            'scenario_data': self.scenario_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
