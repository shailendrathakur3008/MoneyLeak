"""
Transaction Reconciliation and Deduplication Engine.
Prevents double-counting across bank feeds, card feeds, and manual entries,
matching by external UTR/RRN identifiers, exact financial coordinates, and fuzzy heuristics.
"""
from datetime import date, timedelta
from typing import Optional, Tuple, Dict, Any, List
from app.models.transaction import Transaction
from app.models.income import IncomeRecord
from app.models.sync import SyncedTransaction


class TransactionReconciler:
    """Detects duplicates, links manual entries, and prevents double-counting."""

    @staticmethod
    def check_duplicate(
        user_id: int,
        external_id: Optional[str],
        amount_minor_units: int,
        transaction_date: date,
        direction: str,
        normalized_merchant: str
    ) -> Tuple[str, Optional[int], Optional[str]]:
        """
        Check whether an incoming transaction is a duplicate.
        Returns: (status, matched_transaction_id, reason)
        status values:
          - 'DUPLICATE_EXTERNAL_ID': Exact UTR/RRN already imported in SyncedTransaction or Transaction
          - 'EXACT_MATCH': Same amount, date, and merchant already exists in core ledger
          - 'POTENTIAL_DUPLICATE': Same amount, close date (±2 days), similar merchant
          - 'NEW': No match detected, safe to import
        """
        # 1. Exact external reference check (UTR / RRN / Provider Txn ID)
        if external_id:
            ext_clean = str(external_id).strip()
            if len(ext_clean) >= 6:
                existing_synced = SyncedTransaction.query.filter(
                    SyncedTransaction.user_id == user_id,
                    SyncedTransaction.external_id == ext_clean
                ).first()
                if existing_synced:
                    return 'DUPLICATE_EXTERNAL_ID', existing_synced.transaction_id, f"Transaction with reference {ext_clean} has already been imported."

        # 2. Check Core Ledger (Transaction table) for exact coordinate match
        # (Same amount, same date, user_id)
        same_day_txns = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.amount_minor_units == amount_minor_units,
            Transaction.transaction_date == transaction_date
        ).all()

        merchant_lower = normalized_merchant.lower().strip()
        for t in same_day_txns:
            t_desc_lower = (t.description or '').lower()
            t_merch_lower = (t.merchant or '').lower()
            if merchant_lower in t_desc_lower or merchant_lower in t_merch_lower or t_merch_lower in merchant_lower:
                return 'EXACT_MATCH', t.id, f"Matches existing ledger entry: '{t.description}' on {transaction_date.isoformat()}."

        # 3. Check for Fuzzy Match (±2 days window for bank processing lag)
        window_start = transaction_date - timedelta(days=2)
        window_end = transaction_date + timedelta(days=2)

        nearby_txns = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.amount_minor_units == amount_minor_units,
            Transaction.transaction_date >= window_start,
            Transaction.transaction_date <= window_end
        ).all()

        for t in nearby_txns:
            t_desc_lower = (t.description or '').lower()
            t_merch_lower = (t.merchant or '').lower()
            # If merchant partially matches or notes indicate similar payment
            if any(term in t_desc_lower or term in t_merch_lower for term in [merchant_lower[:5], 'upi', 'pos']):
                return 'POTENTIAL_DUPLICATE', t.id, f"Potential match with '{t.description}' on {t.transaction_date.isoformat()} (within 2 days)."

        return 'NEW', None, None

    @staticmethod
    def find_matching_manual_transactions(
        user_id: int,
        amount_minor_units: int,
        transaction_date: date,
        days_window: int = 3
    ) -> List[Dict[str, Any]]:
        """Find existing manual transactions that could match an imported bank transaction."""
        start_date = transaction_date - timedelta(days=days_window)
        end_date = transaction_date + timedelta(days=days_window)

        candidates = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.amount_minor_units == amount_minor_units,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).all()

        results = []
        for c in candidates:
            # Check if this transaction was already linked to another synced transaction
            already_linked = SyncedTransaction.query.filter_by(
                user_id=user_id,
                transaction_id=c.id
            ).first()
            if not already_linked:
                results.append({
                    'id': c.id,
                    'description': c.description,
                    'merchant': c.merchant,
                    'date': c.transaction_date.isoformat(),
                    'amount_minor_units': c.amount_minor_units,
                    'category_name': c.category.name if c.category else 'Uncategorized',
                    'transaction_type': c.transaction_type
                })
        return results
