"""
Universal Expense Sync Orchestrator Engine.
Coordinates data retrieval, categorizer, reconciler, ledger persistence,
audit logging, and user review actions.
"""
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from app.extensions import db
from app.models.transaction import Transaction
from app.models.income import IncomeRecord
from app.models.category import Category
from app.models.user import User
from app.models.sync import (
    FinancialConnection,
    SyncedTransaction,
    MerchantCategoryPreference,
    SyncAuditLog
)
from app.services.sync.categorizer import MerchantCategorizer
from app.services.sync.reconciler import TransactionReconciler
from app.services.sync.aa_client import AccountAggregatorClient

logger = logging.getLogger(__name__)


class SyncEngine:
    """Central orchestrator for Universal Expense Sync."""

    @staticmethod
    def get_sync_overview(user_id: int) -> Dict[str, Any]:
        """Aggregate high-level synchronization metrics for dashboard KPIs."""
        user = db.session.get(User, user_id)
        if not user:
            return {}

        connections = FinancialConnection.query.filter_by(user_id=user_id).all()
        active_connections = [c for c in connections if c.status == 'CONNECTED']

        total_synced = SyncedTransaction.query.filter_by(user_id=user_id).count()
        pending_review = SyncedTransaction.query.filter(
            SyncedTransaction.user_id == user_id,
            SyncedTransaction.review_status.in_(['PENDING_REVIEW', 'POTENTIAL_DUPLICATE'])
        ).count()
        potential_duplicates = SyncedTransaction.query.filter_by(
            user_id=user_id,
            review_status='POTENTIAL_DUPLICATE'
        ).count()

        # Last sync across any connection
        last_sync = None
        for c in connections:
            if c.last_sync_at:
                if last_sync is None or c.last_sync_at > last_sync:
                    last_sync = c.last_sync_at

        aa_client = AccountAggregatorClient()
        provider_info = aa_client.get_provider_status()

        has_live_connections = any(not c.is_simulated for c in active_connections)
        if has_live_connections:
            overall_status = 'ACTIVE'
        elif active_connections:
            overall_status = 'SIMULATED_ACTIVE'
        elif aa_client.is_production() and not aa_client.is_configured():
            overall_status = 'CONFIG_REQUIRED'
        elif not aa_client.is_configured():
            overall_status = 'SANDBOX_READY'
        else:
            overall_status = 'IDLE'

        return {
            'active_connections_count': len(active_connections),
            'total_connections_count': len(connections),
            'has_live_connections': has_live_connections,
            'total_synced_transactions': total_synced,
            'pending_review_count': pending_review,
            'potential_duplicates_count': potential_duplicates,
            'last_sync_at': last_sync.isoformat() if last_sync else None,
            'provider_info': provider_info,
            'overall_status': overall_status
        }

    @staticmethod
    def sync_connection(
        user_id: int,
        connection_id: int,
        sync_type: str = 'MANUAL_SYNC_NOW'
    ) -> Dict[str, Any]:
        """Synchronize a specific financial connection."""
        conn = FinancialConnection.query.filter_by(id=connection_id, user_id=user_id).first()
        if not conn:
            return {'success': False, 'error': 'Financial connection not found.'}

        if conn.status == 'DISCONNECTED':
            return {'success': False, 'error': 'Cannot synchronize a disconnected institution. Reconnect first.'}

        conn.status = 'SYNCING'
        db.session.commit()

        try:
            aa_client = AccountAggregatorClient()

            # Prevent generating fake transactions in live production when provider credentials are missing
            if aa_client.is_production() and not aa_client.is_configured():
                conn.status = 'CONNECTED'
                db.session.commit()
                return {
                    'success': False,
                    'error': f"Live sync unavailable for {conn.institution_name}: Setu Account Aggregator credentials (SETU_AA_CLIENT_ID, SETU_AA_CLIENT_SECRET, SETU_AA_PRODUCT_INSTANCE_ID) are required in production to sync genuine transactions.",
                    'imported_count': 0,
                    'duplicate_count': 0,
                    'review_count': 0,
                    'is_simulated': conn.is_simulated
                }

            raw_records = aa_client.fetch_transactions(
                consent_id=conn.consent_id or 'dummy',
                fip_code=conn.institution_code,
                days_back=30
            )

            results = SyncEngine.process_raw_transactions(
                user_id=user_id,
                connection_id=conn.id,
                raw_records=raw_records,
                source=f"AA_{conn.institution_code}"
            )

            conn.status = 'CONNECTED'
            conn.last_sync_at = datetime.utcnow()
            conn.error_message = ''

            # Create Audit Log
            audit = SyncAuditLog(
                user_id=user_id,
                connection_id=conn.id,
                sync_type=sync_type,
                status='SUCCESS',
                records_fetched=len(raw_records),
                records_imported=results['imported_count'],
                records_duplicates=results['duplicate_count'],
                records_review_required=results['review_count'],
                error_details=''
            )
            db.session.add(audit)
            db.session.commit()

            return {
                'success': True,
                'connection_id': conn.id,
                'institution_name': conn.institution_name,
                'records_fetched': len(raw_records),
                'imported_count': results['imported_count'],
                'duplicate_count': results['duplicate_count'],
                'review_count': results['review_count']
            }

        except Exception as e:
            db.session.rollback()
            conn = FinancialConnection.query.filter_by(id=connection_id, user_id=user_id).first()
            if conn:
                conn.status = 'ERROR'
                conn.error_message = str(e)

            audit = SyncAuditLog(
                user_id=user_id,
                connection_id=connection_id,
                sync_type=sync_type,
                status='FAILED',
                records_fetched=0,
                records_imported=0,
                records_duplicates=0,
                records_review_required=0,
                error_details=str(e)
            )
            db.session.add(audit)
            db.session.commit()
            return {'success': False, 'error': f"Sync failed: {str(e)}"}

    @staticmethod
    def sync_all_connections(user_id: int) -> Dict[str, Any]:
        """Trigger synchronization across all active financial connections for a user."""
        connections = FinancialConnection.query.filter_by(
            user_id=user_id,
            status='CONNECTED'
        ).all()

        if not connections:
            return {'success': False, 'error': 'No active financial connections found to synchronize.'}

        total_imported = 0
        total_duplicates = 0
        total_review = 0
        errors = []

        for c in connections:
            res = SyncEngine.sync_connection(user_id, c.id, sync_type='AUTOMATIC')
            if res['success']:
                total_imported += res.get('imported_count', 0)
                total_duplicates += res.get('duplicate_count', 0)
                total_review += res.get('review_count', 0)
            else:
                errors.append(f"{c.institution_name}: {res.get('error')}")

        return {
            'success': True,
            'connections_synced': len(connections),
            'total_imported': total_imported,
            'total_duplicates': total_duplicates,
            'total_review': total_review,
            'errors': errors
        }

    @staticmethod
    def process_raw_transactions(
        user_id: int,
        connection_id: Optional[int],
        raw_records: List[Dict[str, Any]],
        source: str = 'AA_SETU'
    ) -> Dict[str, Any]:
        """
        Deduplicate, categorize, and stage/commit raw incoming bank records.
        Returns:
          { 'imported_count': int, 'duplicate_count': int, 'review_count': int, 'staged_ids': list }
        """
        imported_count = 0
        duplicate_count = 0
        review_count = 0
        staged_ids = []

        import hashlib

        for item in raw_records:
            ext_id = item.get('external_id')
            raw_narration = item.get('narration') or item.get('description') or 'Unknown'
            amt_minor = item.get('amount_minor_units', 0)
            txn_date = item.get('date') or date.today()
            direction = item.get('direction', 'DEBIT').upper()

            # Deterministic SHA-256 fingerprint for strict idempotency
            date_str = txn_date.isoformat() if hasattr(txn_date, 'isoformat') else str(txn_date)
            fp_raw = f"{user_id}:{ext_id or ''}:{amt_minor}:{date_str}:{raw_narration[:80]}:{direction}"
            source_fingerprint = hashlib.sha256(fp_raw.encode('utf-8')).hexdigest()

            # Fast check against existing fingerprint
            existing_fp = SyncedTransaction.query.filter_by(
                user_id=user_id,
                source_fingerprint=source_fingerprint
            ).first()
            if existing_fp:
                duplicate_count += 1
                continue

            # 1. Categorization
            cat_result = MerchantCategorizer.categorize_transaction(
                user_id=user_id,
                raw_narration=raw_narration,
                direction=direction,
                amount_minor_units=amt_minor
            )

            # 2. Deduplication & Reconciliation check
            dup_status, matched_txn_id, dup_reason = TransactionReconciler.check_duplicate(
                user_id=user_id,
                external_id=ext_id,
                amount_minor_units=amt_minor,
                transaction_date=txn_date,
                direction=direction,
                normalized_merchant=cat_result['normalized_merchant']
            )

            if dup_status == 'DUPLICATE_EXTERNAL_ID':
                # Already imported and in database, skip strictly to remain idempotent
                duplicate_count += 1
                continue

            # Determine initial review status
            initial_status = 'PENDING_REVIEW'
            duplicate_of = None

            if dup_status in ('EXACT_MATCH', 'POTENTIAL_DUPLICATE'):
                initial_status = 'POTENTIAL_DUPLICATE'
                duplicate_of = matched_txn_id
                review_count += 1
            elif cat_result['confidence_score'] >= 0.85:
                # High confidence and no duplicate conflict -> Auto-approve & import
                initial_status = 'APPROVED'
                imported_count += 1
            else:
                initial_status = 'PENDING_REVIEW'
                review_count += 1

            is_transfer = cat_result['transaction_type'] == 'TRANSFER'
            is_refund = cat_result['transaction_type'] == 'REFUND'
            is_reversal = 'reversal' in raw_narration.lower()

            # Create SyncedTransaction staging record
            synced_txn = SyncedTransaction(
                user_id=user_id,
                connection_id=connection_id,
                external_id=ext_id,
                source_fingerprint=source_fingerprint,
                raw_narration=raw_narration,
                normalized_merchant=cat_result['normalized_merchant'],
                amount_minor_units=amt_minor,
                currency=item.get('currency', 'INR'),
                direction=direction,
                transaction_type=cat_result['transaction_type'],
                payment_method=cat_result['payment_method'],
                is_transfer=is_transfer,
                is_refund=is_refund,
                is_reversal=is_reversal,
                raw_date=txn_date,
                suggested_category_id=cat_result['category_id'],
                confidence_score=cat_result['confidence_score'],
                categorization_reason=cat_result['reason'],
                review_status=initial_status,
                duplicate_of_id=duplicate_of,
                source=source
            )
            db.session.add(synced_txn)
            db.session.flush()

            # If auto-approved, immediately persist to Core Ledger
            if initial_status == 'APPROVED':
                SyncEngine._commit_to_core_ledger(synced_txn)

            staged_ids.append(synced_txn.id)

        db.session.commit()
        return {
            'imported_count': imported_count,
            'duplicate_count': duplicate_count,
            'review_count': review_count,
            'staged_ids': staged_ids
        }

    @staticmethod
    def _commit_to_core_ledger(synced_txn: SyncedTransaction):
        """Create or update corresponding entry in Transaction and/or IncomeRecord tables."""
        user = db.session.get(User, synced_txn.user_id)
        if not user:
            return

        t_type = synced_txn.transaction_type.upper()

        if t_type == 'INCOME':
            # Create IncomeRecord for recognized income/salary
            income_rec = IncomeRecord(
                user_id=synced_txn.user_id,
                amount_minor_units=synced_txn.amount_minor_units,
                income_source=synced_txn.normalized_merchant,
                received_date=synced_txn.raw_date,
                notes=f"Auto-synced via {synced_txn.source}. Ref: {synced_txn.external_id or 'N/A'}"
            )
            db.session.add(income_rec)
            db.session.flush()
            synced_txn.income_id = income_rec.id

        # Also create Transaction entry (for ledger visibility and category tracking)
        # Note: If it's INCOME, Transaction.transaction_type='INCOME' is recorded in the ledger
        core_txn = Transaction(
            user_id=synced_txn.user_id,
            category_id=synced_txn.suggested_category_id,
            amount_minor_units=synced_txn.amount_minor_units,
            transaction_type=t_type,
            transaction_date=synced_txn.raw_date,
            description=f"{synced_txn.normalized_merchant} ({synced_txn.payment_method})",
            merchant=synced_txn.normalized_merchant,
            notes=f"Source: {synced_txn.source} | Raw: {synced_txn.raw_narration}"
        )
        db.session.add(core_txn)
        db.session.flush()
        synced_txn.transaction_id = core_txn.id

    @staticmethod
    def approve_transaction(
        user_id: int,
        synced_txn_id: int,
        category_id: Optional[int] = None,
        save_preference: bool = False
    ) -> Dict[str, Any]:
        """Approve and import a transaction from review queue into core ledger."""
        synced = SyncedTransaction.query.filter_by(id=synced_txn_id, user_id=user_id).first()
        if not synced:
            return {'success': False, 'error': 'Synced transaction not found.'}

        if category_id:
            cat = Category.query.filter(
                Category.id == category_id,
                (Category.user_id == user_id) | (Category.user_id.is_(None))
            ).first()
            if cat:
                synced.suggested_category_id = cat.id

        # Save user preference if requested
        if save_preference and synced.normalized_merchant and synced.suggested_category_id:
            merchant_key = synced.normalized_merchant.lower().strip()
            pref = MerchantCategoryPreference.query.filter_by(
                user_id=user_id,
                merchant_normalized=merchant_key
            ).first()
            if not pref:
                pref = MerchantCategoryPreference(
                    user_id=user_id,
                    merchant_normalized=merchant_key,
                    category_id=synced.suggested_category_id,
                    transaction_type=synced.transaction_type
                )
                db.session.add(pref)
            else:
                pref.category_id = synced.suggested_category_id
                pref.transaction_type = synced.transaction_type

        # If not already committed, commit to core ledger
        if not synced.transaction_id:
            SyncEngine._commit_to_core_ledger(synced)

        synced.review_status = 'APPROVED'
        db.session.commit()
        return {'success': True, 'message': 'Transaction successfully approved and imported.'}

    @staticmethod
    def link_transaction_to_existing(
        user_id: int,
        synced_txn_id: int,
        existing_txn_id: int
    ) -> Dict[str, Any]:
        """Link a synced transaction to an existing manual transaction to prevent duplication."""
        synced = SyncedTransaction.query.filter_by(id=synced_txn_id, user_id=user_id).first()
        existing = Transaction.query.filter_by(id=existing_txn_id, user_id=user_id).first()

        if not synced or not existing:
            return {'success': False, 'error': 'Transaction record not found.'}

        synced.transaction_id = existing.id
        synced.review_status = 'LINKED'
        existing.notes = f"{existing.notes or ''} [Linked with {synced.source}: {synced.raw_narration}]".strip()

        db.session.commit()
        return {'success': True, 'message': 'Successfully linked to existing transaction.'}

    @staticmethod
    def reject_transaction(user_id: int, synced_txn_id: int) -> Dict[str, Any]:
        """Reject and exclude a synced transaction."""
        synced = SyncedTransaction.query.filter_by(id=synced_txn_id, user_id=user_id).first()
        if not synced:
            return {'success': False, 'error': 'Transaction not found.'}

        # If it was committed, remove from core ledger
        if synced.transaction_id:
            core_txn = db.session.get(Transaction, synced.transaction_id)
            if core_txn:
                db.session.delete(core_txn)
            synced.transaction_id = None

        if synced.income_id:
            inc = db.session.get(IncomeRecord, synced.income_id)
            if inc:
                db.session.delete(inc)
            synced.income_id = None

        synced.review_status = 'REJECTED'
        db.session.commit()
        return {'success': True, 'message': 'Transaction rejected and excluded.'}

    @staticmethod
    def bulk_approve_high_confidence(user_id: int) -> Dict[str, Any]:
        """Approve all pending transactions that have high confidence score."""
        pending_high = SyncedTransaction.query.filter(
            SyncedTransaction.user_id == user_id,
            SyncedTransaction.review_status == 'PENDING_REVIEW',
            SyncedTransaction.confidence_score >= 0.70
        ).all()

        count = 0
        for st in pending_high:
            if not st.transaction_id:
                SyncEngine._commit_to_core_ledger(st)
            st.review_status = 'APPROVED'
            count += 1

        db.session.commit()
        return {'success': True, 'approved_count': count}

    @staticmethod
    def disconnect_connection(user_id: int, connection_id: int, delete_data: bool = False) -> Dict[str, Any]:
        """Disconnect institution, revoke consent, and optionally purge imported transactions."""
        conn = FinancialConnection.query.filter_by(id=connection_id, user_id=user_id).first()
        if not conn:
            return {'success': False, 'error': 'Connection not found.'}

        # Revoke consent token with active banking provider
        try:
            if conn.consent_id:
                aa_client = AccountAggregatorClient()
                aa_client.revoke_consent(conn.consent_id)
        except Exception as e:
            logger.warning(f"Provider consent revocation notice failed: {e}")

        if delete_data:
            # Delete corresponding core transactions first
            synced_txns = SyncedTransaction.query.filter_by(connection_id=conn.id, user_id=user_id).all()
            for st in synced_txns:
                if st.transaction_id:
                    ctxn = db.session.get(Transaction, st.transaction_id)
                    if ctxn:
                        db.session.delete(ctxn)
                if st.income_id:
                    inc = db.session.get(IncomeRecord, st.income_id)
                    if inc:
                        db.session.delete(inc)

            db.session.delete(conn)
        else:
            conn.status = 'DISCONNECTED'
            conn.consent_status = 'REVOKED'

        db.session.commit()
        return {'success': True, 'message': 'Institution successfully disconnected and consent revoked.'}
