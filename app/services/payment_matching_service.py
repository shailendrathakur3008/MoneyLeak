"""
Provider-Independent Bank & Investment Transaction Matching Service.

Architected to ingest authorized bank transaction streams (e.g. Account Aggregator,
CAMS/KFintech mutual fund feeds, UPI mandates, or simulated statements)
and match them against scheduled payments with strict confidence verification.

Security & Integrity Principles:
- Never marks a payment successful based solely on an amount or scheduled date.
- Requires high-confidence corroboration (amount + date window + narration tokens).
- Distinguishes manual user marking ('PAID_MANUAL') from verified bank evidence ('CONFIRMED_EXTERNAL').
- Preserves external confirmation timestamps and reference IDs.
- Flags ambiguous matches for user manual review ('AWAITING_CONFIRMATION').
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
import re
from app.extensions import db
from app.models.recurring_payment import RecurringPayment, PaymentSchedule
from app.models.payment_notification import PaymentOccurrence, Notification
from app.services.reminder_service import format_inr, advance_due_date


@dataclass
class BankTransactionDTO:
    """Standardized Data Transfer Object for external bank or mutual fund transactions."""
    transaction_id: str
    amount: float
    date: date
    narration: str
    status: str = 'SUCCESS'  # 'SUCCESS', 'PENDING', 'FAILED', 'REVERSED'
    reference_number: Optional[str] = None
    account_masked: Optional[str] = None
    provider: str = 'ACCOUNT_AGGREGATOR'  # 'ACCOUNT_AGGREGATOR', 'CAMSONLINE', 'KFINTECH', 'NPCI_UPI', 'STATEMENT_IMPORT'
    transaction_type: str = 'DEBIT'       # 'DEBIT', 'CREDIT'


@dataclass
class PaymentMatchResult:
    """Result returned by the payment matching engine."""
    status: str  # 'CONFIRMED', 'FAILED', 'MANUAL_REVIEW', 'DUPLICATE', 'NO_MATCH'
    confidence_score: float
    matched_occurrence_id: Optional[int]
    matched_schedule_id: Optional[int]
    reason: str


class PaymentMatchingService:
    """
    Evaluates incoming bank transactions against active user payment schedules and occurrences.
    """

    @staticmethod
    def is_bank_integration_active() -> bool:
        """
        Returns False in baseline implementation, indicating live bank connection awaits configuration.
        """
        return False

    @classmethod
    def match_and_process_transaction(
        cls,
        user_id: int,
        txn: BankTransactionDTO
    ) -> PaymentMatchResult:
        """
        Attempts to match an external bank transaction to a pending PaymentOccurrence.
        Updates occurrence status only when sufficient corroborating evidence exists.
        """
        if txn.transaction_type.upper() != 'DEBIT':
            return PaymentMatchResult(
                status='NO_MATCH',
                confidence_score=0.0,
                matched_occurrence_id=None,
                matched_schedule_id=None,
                reason="Only debit transactions correspond to scheduled payment obligations."
            )

        # 1. Check for duplicate transaction processing
        existing_occ = PaymentOccurrence.query.filter_by(
            external_transaction_id=txn.transaction_id
        ).first()
        if existing_occ:
            return PaymentMatchResult(
                status='DUPLICATE',
                confidence_score=1.0,
                matched_occurrence_id=existing_occ.id,
                matched_schedule_id=existing_occ.payment_schedule_id,
                reason=f"Transaction {txn.transaction_id} already confirmed against occurrence #{existing_occ.id}."
            )

        # 2. Find candidate occurrences for this user in +/- 3 day window
        min_date = txn.date - timedelta(days=3)
        max_date = txn.date + timedelta(days=3)

        candidates = (
            PaymentOccurrence.query
            .join(RecurringPayment, PaymentOccurrence.payment_schedule_id == RecurringPayment.id)
            .filter(
                RecurringPayment.user_id == user_id,
                PaymentOccurrence.due_date >= min_date,
                PaymentOccurrence.due_date <= max_date,
                PaymentOccurrence.status.in_(['PENDING', 'AWAITING_CONFIRMATION', 'OVERDUE', 'PAID_MANUAL'])
            )
            .all()
        )

        if not candidates:
            return PaymentMatchResult(
                status='NO_MATCH',
                confidence_score=0.0,
                matched_occurrence_id=None,
                matched_schedule_id=None,
                reason="No scheduled payment occurrences within +/- 3 days of transaction date."
            )

        best_candidate: Optional[PaymentOccurrence] = None
        best_score = 0.0
        best_reason = ""

        txn_narration_lower = txn.narration.lower()
        txn_minor = int(round(txn.amount * 100))

        for cand in candidates:
            score = 0.0
            reasons = []
            sched = cand.schedule

            # Factor A: Exact Amount Match (Weight: 40%)
            if cand.amount_minor_units == txn_minor:
                score += 0.40
                reasons.append("Exact amount match")
            elif abs(cand.amount_minor_units - txn_minor) / max(cand.amount_minor_units, 1) < 0.02:
                # Within 2% tolerance (e.g. minor tax or fee variance)
                score += 0.20
                reasons.append("Close amount match (<2% variance)")
            else:
                # Amount mismatch is disqualifying
                continue

            # Factor B: Narration / Payee Token Matching (Weight: 45%)
            search_tokens = []
            if sched.scheme_name:
                search_tokens.extend(re.findall(r'[a-zA-Z0-9]+', sched.scheme_name.lower()))
            if sched.name:
                search_tokens.extend(re.findall(r'[a-zA-Z0-9]+', sched.name.lower()))

            # Filter out common stop-words
            stopwords = {'ltd', 'limited', 'fund', 'fund', 'india', 'regular', 'plan', 'growth', 'direct', 'payment', 'bill', 'emi'}
            meaningful_tokens = [t for t in search_tokens if len(t) > 2 and t not in stopwords]

            matched_tokens = [t for t in meaningful_tokens if t in txn_narration_lower]
            if meaningful_tokens:
                token_ratio = len(matched_tokens) / len(meaningful_tokens)
                if token_ratio >= 0.5:
                    score += 0.45
                    reasons.append(f"Strong narration match ({', '.join(matched_tokens[:3])})")
                elif token_ratio > 0:
                    score += 0.25
                    reasons.append(f"Partial narration match ({', '.join(matched_tokens[:2])})")
            else:
                # Fallback check for category keyword
                cat_kw = sched.category.lower().split('_')[0]
                if cat_kw in txn_narration_lower:
                    score += 0.20
                    reasons.append(f"Category keyword match '{cat_kw}'")

            # Factor C: Date Proximity (Weight: 15%)
            diff_days = abs((cand.due_date - txn.date).days)
            if diff_days == 0:
                score += 0.15
                reasons.append("Exact date match")
            elif diff_days == 1:
                score += 0.10
                reasons.append("1 day date proximity")
            else:
                score += 0.05
                reasons.append(f"{diff_days} days date proximity")

            if score > best_score:
                best_score = score
                best_candidate = cand
                best_reason = "; ".join(reasons)

        if not best_candidate:
            return PaymentMatchResult(
                status='NO_MATCH',
                confidence_score=0.0,
                matched_occurrence_id=None,
                matched_schedule_id=None,
                reason="No candidate satisfied minimal matching requirements."
            )

        # ---------------------------------------------------------------------
        # Evaluation Thresholds
        # ---------------------------------------------------------------------
        # 1. High Confidence Match (>= 0.80) -> Verified Confirmation
        if best_score >= 0.80:
            sched = best_candidate.schedule

            if txn.status.upper() == 'SUCCESS':
                best_candidate.status = 'CONFIRMED_EXTERNAL'
                best_candidate.externally_confirmed_at = datetime.utcnow()
                best_candidate.external_transaction_id = txn.transaction_id
                best_candidate.external_provider = txn.provider

                # Advance schedule's next_due_date to next cycle if this was for current due date
                if sched.next_due_date <= best_candidate.due_date:
                    sched.next_due_date = advance_due_date(best_candidate.due_date, sched.frequency)

                # Send verification notification
                notif = Notification(
                    user_id=user_id,
                    payment_occurrence_id=best_candidate.id,
                    payment_schedule_id=sched.id,
                    notification_type='PAYMENT_CONFIRMED_EXTERNAL',
                    channel='IN_APP',
                    title=f"Payment Confirmed: {format_inr(txn.amount)} for {sched.name}",
                    message=(
                        f"Verified bank debit of {format_inr(txn.amount)} for {sched.name} "
                        f"confirmed on {txn.date.strftime('%d %b %Y')} via {txn.provider} "
                        f"(Ref: {txn.reference_number or txn.transaction_id[:12]})."
                    ),
                    link_url='/payments',
                    idempotency_key=f"ext_conf_{best_candidate.id}_{txn.transaction_id}",
                    delivery_status='DELIVERED',
                    sent_at=datetime.utcnow()
                )
                db.session.add(notif)
                db.session.commit()

                return PaymentMatchResult(
                    status='CONFIRMED',
                    confidence_score=round(best_score, 2),
                    matched_occurrence_id=best_candidate.id,
                    matched_schedule_id=sched.id,
                    reason=f"High-confidence match ({int(best_score*100)}%): {best_reason}."
                )

            elif txn.status.upper() == 'FAILED':
                best_candidate.status = 'FAILED_EXTERNAL'
                best_candidate.external_transaction_id = txn.transaction_id
                best_candidate.external_provider = txn.provider

                notif = Notification(
                    user_id=user_id,
                    payment_occurrence_id=best_candidate.id,
                    payment_schedule_id=sched.id,
                    notification_type='PAYMENT_FAILED_EXTERNAL',
                    channel='IN_APP',
                    title=f"Payment Failed: {sched.name}",
                    message=(
                        f"Scheduled debit of {format_inr(txn.amount)} for {sched.name} failed "
                        f"via {txn.provider}. Please verify bank balance and retry manually."
                    ),
                    link_url='/payments',
                    idempotency_key=f"ext_fail_{best_candidate.id}_{txn.transaction_id}",
                    delivery_status='DELIVERED',
                    sent_at=datetime.utcnow()
                )
                db.session.add(notif)
                db.session.commit()

                return PaymentMatchResult(
                    status='FAILED',
                    confidence_score=round(best_score, 2),
                    matched_occurrence_id=best_candidate.id,
                    matched_schedule_id=sched.id,
                    reason=f"Failed transaction verified ({int(best_score*100)}%): {best_reason}."
                )

        # 2. Ambiguous Match (0.50 - 0.79) -> Flag for Manual Review
        elif best_score >= 0.50:
            best_candidate.status = 'AWAITING_CONFIRMATION'
            db.session.commit()

            return PaymentMatchResult(
                status='MANUAL_REVIEW',
                confidence_score=round(best_score, 2),
                matched_occurrence_id=best_candidate.id,
                matched_schedule_id=best_candidate.payment_schedule_id,
                reason=(
                    f"Ambiguous match ({int(best_score*100)}%): {best_reason}. "
                    "Marked as 'Awaiting Confirmation' for manual user review."
                )
            )

        # 3. Low Confidence (< 0.50) -> No Match
        return PaymentMatchResult(
            status='NO_MATCH',
            confidence_score=round(best_score, 2),
            matched_occurrence_id=None,
            matched_schedule_id=None,
            reason=f"Confidence below threshold ({int(best_score*100)}%): {best_reason}."
        )
