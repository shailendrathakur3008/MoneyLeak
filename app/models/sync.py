"""
Universal Expense Sync Data Models.
Manages financial connections, synced transactions, merchant categorization preferences,
sync audit logs, and digital receipts.
"""
from datetime import datetime, date
from app.extensions import db


class FinancialConnection(db.Model):
    __tablename__ = 'financial_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    institution_name = db.Column(db.String(120), nullable=False)
    institution_code = db.Column(db.String(50), nullable=False, default='GENERIC')
    account_mask = db.Column(db.String(30), default='•••• ****')
    account_type = db.Column(db.String(40), default='SAVINGS')  # SAVINGS, CURRENT, CREDIT_CARD, UPI_WALLET
    provider = db.Column(db.String(50), default='ACCOUNT_AGGREGATOR')  # ACCOUNT_AGGREGATOR, BANK_FEED, STATEMENT_IMPORT
    consent_id = db.Column(db.String(150), nullable=True, index=True)
    consent_status = db.Column(db.String(40), default='ACTIVE')  # ACTIVE, PENDING, EXPIRED, REVOKED, CONFIG_REQUIRED
    consent_expires_at = db.Column(db.DateTime, nullable=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    sync_cursor = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='CONNECTED')  # CONNECTED, SYNCING, DISCONNECTED, ERROR, CONFIG_REQUIRED
    error_message = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    synced_transactions = db.relationship('SyncedTransaction', backref='connection', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('SyncAuditLog', backref='connection', lazy='dynamic', cascade='all, delete-orphan')

    def is_active(self):
        return self.status == 'CONNECTED' and self.consent_status == 'ACTIVE'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'institution_name': self.institution_name,
            'institution_code': self.institution_code,
            'account_mask': self.account_mask,
            'account_type': self.account_type,
            'provider': self.provider,
            'consent_id': self.consent_id,
            'consent_status': self.consent_status,
            'consent_expires_at': self.consent_expires_at.isoformat() if self.consent_expires_at else None,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_synced': self.synced_transactions.count()
        }


class SyncedTransaction(db.Model):
    __tablename__ = 'synced_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    connection_id = db.Column(db.Integer, db.ForeignKey('financial_connections.id', ondelete='CASCADE'), nullable=True, index=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='SET NULL'), nullable=True, index=True)
    income_id = db.Column(db.Integer, db.ForeignKey('income_records.id', ondelete='SET NULL'), nullable=True, index=True)
    external_id = db.Column(db.String(150), nullable=True, index=True)
    raw_narration = db.Column(db.Text, nullable=False)
    normalized_merchant = db.Column(db.String(120), default='Unknown Merchant')
    amount_minor_units = db.Column(db.BigInteger, nullable=False)
    currency = db.Column(db.String(3), default='INR', nullable=False)
    direction = db.Column(db.String(10), default='DEBIT', nullable=False)  # DEBIT or CREDIT
    transaction_type = db.Column(db.String(30), default='EXPENSE', nullable=False)
    # EXPENSE, INCOME, REFUND, TRANSFER, SAVINGS_CONTRIBUTION, DEBT_REPAYMENT
    payment_method = db.Column(db.String(30), default='UPI')  # UPI, CARD, NET_BANKING, NEFT_RTGS, OTHER
    raw_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    raw_time = db.Column(db.String(20), nullable=True)
    suggested_category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    confidence_score = db.Column(db.Float, default=0.5)  # 0.0 to 1.0
    categorization_reason = db.Column(db.String(255), default='')
    review_status = db.Column(db.String(30), default='PENDING_REVIEW', index=True)
    # PENDING_REVIEW, APPROVED, POTENTIAL_DUPLICATE, REJECTED, LINKED
    duplicate_of_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='SET NULL'), nullable=True)
    matched_receipt_id = db.Column(db.Integer, db.ForeignKey('receipt_records.id', ondelete='SET NULL'), nullable=True)
    source = db.Column(db.String(60), default='AA_SETU')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    suggested_category = db.relationship('Category', foreign_keys=[suggested_category_id])
    imported_transaction = db.relationship('Transaction', foreign_keys=[transaction_id])
    duplicate_transaction = db.relationship('Transaction', foreign_keys=[duplicate_of_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'connection_id': self.connection_id,
            'institution_name': self.connection.institution_name if self.connection else 'Statement Import',
            'transaction_id': self.transaction_id,
            'external_id': self.external_id,
            'raw_narration': self.raw_narration,
            'normalized_merchant': self.normalized_merchant,
            'amount_minor_units': self.amount_minor_units,
            'currency': self.currency,
            'direction': self.direction,
            'transaction_type': self.transaction_type,
            'payment_method': self.payment_method,
            'raw_date': self.raw_date.isoformat() if self.raw_date else None,
            'raw_time': self.raw_time,
            'suggested_category_id': self.suggested_category_id,
            'suggested_category_name': self.suggested_category.name if self.suggested_category else None,
            'budget_group': self.suggested_category.budget_group if self.suggested_category else 'WANTS',
            'confidence_score': round(self.confidence_score, 2),
            'confidence_level': 'HIGH' if self.confidence_score >= 0.85 else ('MEDIUM' if self.confidence_score >= 0.6 else 'LOW'),
            'categorization_reason': self.categorization_reason,
            'review_status': self.review_status,
            'duplicate_of_id': self.duplicate_of_id,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MerchantCategoryPreference(db.Model):
    __tablename__ = 'merchant_category_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    merchant_normalized = db.Column(db.String(120), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.String(30), default='EXPENSE', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'merchant_normalized', name='uq_user_merchant_pref'),
    )

    category = db.relationship('Category', foreign_keys=[category_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'merchant_normalized': self.merchant_normalized,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'transaction_type': self.transaction_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SyncAuditLog(db.Model):
    __tablename__ = 'sync_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    connection_id = db.Column(db.Integer, db.ForeignKey('financial_connections.id', ondelete='SET NULL'), nullable=True, index=True)
    sync_type = db.Column(db.String(50), default='MANUAL_SYNC_NOW')
    status = db.Column(db.String(20), default='SUCCESS')  # SUCCESS, FAILED, PARTIAL
    records_fetched = db.Column(db.Integer, default=0)
    records_imported = db.Column(db.Integer, default=0)
    records_duplicates = db.Column(db.Integer, default=0)
    records_review_required = db.Column(db.Integer, default=0)
    error_details = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'connection_id': self.connection_id,
            'institution_name': self.connection.institution_name if self.connection else 'All Sources / Batch',
            'sync_type': self.sync_type,
            'status': self.status,
            'records_fetched': self.records_fetched,
            'records_imported': self.records_imported,
            'records_duplicates': self.records_duplicates,
            'records_review_required': self.records_review_required,
            'error_details': self.error_details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReceiptRecord(db.Model):
    __tablename__ = 'receipt_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    merchant_name = db.Column(db.String(120), nullable=False)
    order_id = db.Column(db.String(100), nullable=True)
    total_minor_units = db.Column(db.BigInteger, nullable=False)
    receipt_date = db.Column(db.Date, nullable=False, default=date.today)
    file_name = db.Column(db.String(255), default='')
    raw_text = db.Column(db.Text, default='')
    items_json = db.Column(db.Text, default='[]')
    matched_synced_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'merchant_name': self.merchant_name,
            'order_id': self.order_id,
            'total_minor_units': self.total_minor_units,
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else None,
            'file_name': self.file_name,
            'matched_synced_id': self.matched_synced_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
