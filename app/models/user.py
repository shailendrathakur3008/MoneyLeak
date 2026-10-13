from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    auth_provider = db.Column(db.String(50), default='local', nullable=False)  # 'local', 'google', 'email_otp'
    provider_user_id = db.Column(db.String(255), nullable=True)
    profile_picture_url = db.Column(db.String(500), nullable=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Personal Preferences & Location
    phone_number = db.Column(db.String(30), nullable=True)
    date_of_birth = db.Column(db.String(30), nullable=True)
    country = db.Column(db.String(80), default='India', nullable=False)
    state_id = db.Column(db.String(20), nullable=True)
    state_name = db.Column(db.String(100), nullable=True)
    district_id = db.Column(db.String(50), nullable=True)
    district_name = db.Column(db.String(100), nullable=True)
    city_id = db.Column(db.String(80), nullable=True)
    city_name = db.Column(db.String(120), nullable=True)
    is_custom_city = db.Column(db.Boolean, default=False, nullable=False)
    pincode = db.Column(db.String(10), nullable=True)
    location_tier = db.Column(db.String(50), default='UNCLASSIFIED', nullable=False)  # 'METRO', 'URBAN', 'TOWN', 'RURAL', 'UNCLASSIFIED'
    budget_preset = db.Column(db.String(50), default='standard', nullable=False)      # 'standard', 'metro', 'high_essential', 'lower_cost', 'custom'

    currency = db.Column(db.String(10), default='INR', nullable=False)
    preferred_language = db.Column(db.String(20), default='en', nullable=False)
    theme_preference = db.Column(db.String(20), default='system', nullable=False)

    # Employment & User Type
    user_type = db.Column(db.String(30), nullable=True)  # 'student', 'salaried'

    # Financial Preferences & Household Baseline
    monthly_income_minor_units = db.Column(db.BigInteger, default=4000000)  # Default ₹40,000.00
    income_frequency = db.Column(db.String(20), default='MONTHLY')
    opening_balance_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    monthly_savings_target_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    rent_or_emi_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    essential_expenses_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    debt_payments_minor_units = db.Column(db.BigInteger, default=0, nullable=False)
    dependants_count = db.Column(db.Integer, default=0, nullable=False)

    primary_financial_goal = db.Column(db.String(100), nullable=True)
    investment_experience = db.Column(db.String(50), nullable=True)
    preferred_investment_categories = db.Column(db.Text, nullable=True)
    month_start_day = db.Column(db.Integer, default=1)

    # Onboarding Wizard State
    onboarding_step = db.Column(db.Integer, default=1, nullable=False)  # 1: Personal, 2: Employment, 3: Financial, 4: Categories, 5: Review
    onboarding_completed = db.Column(db.Boolean, default=False, nullable=False)

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
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_avatar_url(self) -> str:
        if self.profile_picture_url:
            return self.profile_picture_url
        return f"https://api.dicebear.com/7.x/initials/svg?seed={self.full_name}&backgroundColor=161917&textColor=cbf432"

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'auth_provider': self.auth_provider,
            'profile_picture_url': self.profile_picture_url,
            'email_verified': self.email_verified,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth,
            'country': self.country,
            'state_id': self.state_id,
            'state_name': self.state_name,
            'district_id': self.district_id,
            'district_name': self.district_name,
            'city_id': self.city_id,
            'city_name': self.city_name,
            'is_custom_city': self.is_custom_city,
            'pincode': self.pincode,
            'location_tier': self.location_tier,
            'budget_preset': self.budget_preset,
            'rent_or_emi_minor_units': self.rent_or_emi_minor_units,
            'essential_expenses_minor_units': self.essential_expenses_minor_units,
            'debt_payments_minor_units': self.debt_payments_minor_units,
            'dependants_count': self.dependants_count,
            'currency': self.currency,
            'preferred_language': self.preferred_language,
            'theme_preference': self.theme_preference or 'system',
            'user_type': self.user_type,
            'monthly_income_minor_units': self.monthly_income_minor_units,
            'income_frequency': self.income_frequency,
            'opening_balance_minor_units': self.opening_balance_minor_units,
            'monthly_savings_target_minor_units': self.monthly_savings_target_minor_units,
            'primary_financial_goal': self.primary_financial_goal,
            'investment_experience': self.investment_experience,
            'preferred_investment_categories': self.preferred_investment_categories,
            'month_start_day': self.month_start_day,
            'onboarding_step': self.onboarding_step,
            'onboarding_completed': self.onboarding_completed,
            'avatar_url': self.get_avatar_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
