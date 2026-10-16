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
        super().__init__(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at,
            is_used=is_used,
            **kwargs
        )

    def is_valid(self, code: str) -> bool:
        if self.is_used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return self.otp_code.strip() == code.strip()
