from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(10), default='INR', nullable=False)
    theme_preference = db.Column(db.String(20), default='system', nullable=False)
    monthly_income_minor_units = db.Column(db.BigInteger, default=4000000)  # Default ₹40,000.00
    income_frequency = db.Column(db.String(20), default='MONTHLY')
    month_start_day = db.Column(db.Integer, default=1)
    onboarding_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    incomes = db.relationship('IncomeRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goals = db.relationship('SavingsGoal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goal_contributions = db.relationship('GoalContribution', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    recurring_payments = db.relationship('RecurringPayment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('FinancialAlert', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'currency': self.currency,
            'theme_preference': self.theme_preference or 'system',
            'monthly_income_minor_units': self.monthly_income_minor_units,
            'income_frequency': self.income_frequency,
            'month_start_day': self.month_start_day,
            'onboarding_completed': self.onboarding_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
