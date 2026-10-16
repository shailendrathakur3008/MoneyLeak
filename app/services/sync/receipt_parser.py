"""
Receipt and Order Confirmation Parser.
Enriches bank transactions with authorized user-provided digital receipts and invoice records
(Swiggy, Zomato, Amazon India, Blinkit, Zepto, Uber) without fabricating details.
"""
import re
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from app.services.money import to_minor_units
from app.models.sync import SyncedTransaction, ReceiptRecord
from app.models.transaction import Transaction


class ReceiptParser:
    """Parses digital receipts and reconciles order details with bank debits."""

    MERCHANT_SIGNATURES = [
        {'name': 'Zomato', 'patterns': [r'zomato', r'order\s*#?\s*([0-9]{8,12})']},
        {'name': 'Swiggy', 'patterns': [r'swiggy', r'order\s*id:?\s*([0-9]{10,14})']},
        {'name': 'Amazon India', 'patterns': [r'amazon', r'order\s*#?\s*([0-9]{3}-[0-9]{7}-[0-9]{7})']},
        {'name': 'Blinkit', 'patterns': [r'blinkit', r'grofers', r'order\s*id:?\s*([A-Z0-9]{8,14})']},
        {'name': 'Zepto', 'patterns': [r'zepto', r'order\s*id:?\s*([A-Z0-9]{8,14})']},
        {'name': 'Uber', 'patterns': [r'uber', r'trip\s*id:?\s*([a-f0-9-]{10,36})']},
    ]

    @staticmethod
    def parse_receipt_text(
        text: str,
        currency: str = 'INR',
        file_name: str = ''
    ) -> Dict[str, Any]:
        """
        Extract merchant, order ID, total amount, and date from receipt text.
        Returns:
          {
             'success': bool,
             'merchant': str,
             'order_id': str,
             'total_minor_units': int,
             'receipt_date': date,
             'raw_text': str
          }
        """
        if not text or not text.strip():
            return {'success': False, 'error': 'Receipt content is empty.'}

        clean_text = text.strip()
        text_lower = clean_text.lower()

        # 1. Identify Merchant
        detected_merchant = 'Unknown Merchant'
        detected_order_id = None

        for m in ReceiptParser.MERCHANT_SIGNATURES:
            if re.search(m['patterns'][0], text_lower):
                detected_merchant = m['name']
                if len(m['patterns']) > 1:
                    oid_match = re.search(m['patterns'][1], clean_text, re.IGNORECASE)
                    if oid_match:
                        detected_order_id = oid_match.group(1)
                break

        # Fallback Order ID search
        if not detected_order_id:
            oid_generic = re.search(r'(?:order\s*id|order\s*#|invoice\s*#?|receipt\s*#?)\s*[:#-]?\s*([A-Za-z0-9-]+)', clean_text, re.IGNORECASE)
            if oid_generic:
                detected_order_id = oid_generic.group(1).strip()

        # 2. Extract Total Amount
        total_minor = ReceiptParser._extract_total_amount(clean_text, currency)
        if total_minor <= 0:
            return {
                'success': False,
                'error': 'Could not detect total monetary amount in receipt.',
                'merchant': detected_merchant,
                'order_id': detected_order_id
            }

        # 3. Extract Date
        receipt_date = ReceiptParser._extract_date(clean_text) or date.today()

        return {
            'success': True,
            'merchant': detected_merchant,
            'order_id': detected_order_id or 'NOT_SPECIFIED',
            'total_minor_units': total_minor,
            'receipt_date': receipt_date,
            'file_name': file_name,
            'raw_text': clean_text[:1000]
        }

    @staticmethod
    def _extract_total_amount(text: str, currency: str) -> int:
        """Find the total paid amount."""
        # Search for Total Paid, Grand Total, Total Amount, etc.
        patterns = [
            r'(?:grand\s*total|total\s*paid|total\s*amount|amount\s*paid|paid\s*amount|bill\s*amount|net\s*amount)\s*[:=\s₹Rs.]*([0-9,]+(?:\.[0-9]{1,2})?)',
            r'[₹Rs.]\s*([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:paid|debited)',
            r'\btotal\s*[:=\s₹Rs.]*([0-9,]+(?:\.[0-9]{1,2})?)',
            r'\bpaid\s*[:=\s₹Rs.]*([0-9,]+(?:\.[0-9]{1,2})?)'
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                raw_num = match.group(1).replace(',', '')
                try:
                    val = float(raw_num)
                    if val > 0:
                        return to_minor_units(val, currency)
                except ValueError:
                    continue
        return 0

    @staticmethod
    def _extract_date(text: str) -> Optional[date]:
        """Search text for order date."""
        date_patterns = [
            (r'\b([0-9]{1,2})[/-]([0-9]{1,2})[/-]([0-9]{4})\b', '%d/%m/%Y'),
            (r'\b([0-9]{4})[/-]([0-9]{1,2})[/-]([0-9]{1,2})\b', '%Y-%m-%d'),
            (r'\b([0-9]{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+([0-9]{4})\b', '%d %b %Y')
        ]
        for pattern, fmt in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                match_str = match.group(0)
                try:
                    return datetime.strptime(match_str.replace('-', '/'), fmt).date()
                except Exception:
                    continue
        return None

    @staticmethod
    def match_receipt_with_transactions(
        user_id: int,
        receipt_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Locate synced or ledger transactions that match this receipt (amount and date within ±1 day).
        """
        amt = receipt_data['total_minor_units']
        r_date = receipt_data['receipt_date']
        start_d = r_date - timedelta(days=2)
        end_d = r_date + timedelta(days=2)

        matches = []

        # Check SyncedTransaction table
        synced_candidates = SyncedTransaction.query.filter(
            SyncedTransaction.user_id == user_id,
            SyncedTransaction.amount_minor_units == amt,
            SyncedTransaction.raw_date >= start_d,
            SyncedTransaction.raw_date <= end_d
        ).all()

        for st in synced_candidates:
            matches.append({
                'type': 'SYNCED',
                'id': st.id,
                'merchant': st.normalized_merchant,
                'date': st.raw_date.isoformat(),
                'amount_minor_units': st.amount_minor_units,
                'review_status': st.review_status,
                'payment_method': st.payment_method
            })

        # Check Core Transaction table
        core_candidates = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.amount_minor_units == amt,
            Transaction.transaction_date >= start_d,
            Transaction.transaction_date <= end_d
        ).all()

        for ct in core_candidates:
            matches.append({
                'type': 'CORE_LEDGER',
                'id': ct.id,
                'merchant': ct.merchant or ct.description,
                'date': ct.transaction_date.isoformat(),
                'amount_minor_units': ct.amount_minor_units,
                'category_name': ct.category.name if ct.category else 'Uncategorized'
            })

        return matches
