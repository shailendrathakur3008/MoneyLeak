from datetime import datetime
from app.extensions import db

class EmailOTP(db.Model):
    __tablename__ = 'email_otps'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(30), default='login')  # 'login', 'register', 'email_change'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    def __init__(
        self,
        email: str | None = None,
        otp_code: str | None = None,
        purpose: str = 'login',
        expires_at: datetime | None = None,
        is_used: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        if email is not None:
            self.email = email
        if otp_code is not None:
            self.otp_code = otp_code
        if purpose is not None:
            self.purpose = purpose
        if expires_at is not None:
            self.expires_at = expires_at
        self.is_used = is_used

    def is_valid(self, code: str) -> bool:
        if self.is_used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return self.otp_code.strip() == code.strip()
