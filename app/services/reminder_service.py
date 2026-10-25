"""
Smart Payment Reminder Calculation & Content Engine for MoneyLeak.

Handles:
- Dynamic reminder scheduling (e.g. 7, 3, 1, 0 days before, overdue)
- Precise month-end date transitions and leap-year frequency arithmetic
- Category-specific, dynamic reminder copy for SIPs, EMIs, Bills, Subscriptions, Rent, etc.
- Safe cancellation of future reminders upon schedule cancellation or due date modification
"""
import calendar
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

def advance_due_date(current_date: date, frequency: str) -> date:
    """
    Calculates the subsequent due date with accurate month-end clamping
    and leap-year handling across all supported payment frequencies.
    """
    freq = (frequency or 'MONTHLY').upper()
    if freq == 'ONCE':
        return current_date

    year = current_date.year
    month = current_date.month
    day = current_date.day

    if freq == 'WEEKLY':
        return current_date + timedelta(days=7)

    elif freq == 'MONTHLY':
        if month == 12:
            new_year = year + 1
            new_month = 1
        else:
            new_year = year
            new_month = month + 1

        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(day, max_day)
        return date(new_year, new_month, new_day)

    elif freq == 'QUARTERLY':
        new_month = month + 3
        new_year = year
        if new_month > 12:
            new_year += 1
            new_month -= 12

        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(day, max_day)
        return date(new_year, new_month, new_day)

    elif freq == 'YEARLY':
        new_year = year + 1
        # Handle leap year Feb 29 -> Feb 28
        max_day = calendar.monthrange(new_year, month)[1]
        new_day = min(day, max_day)
        return date(new_year, month, new_day)

    # Fallback to monthly
    return advance_due_date(current_date, 'MONTHLY')


def format_inr(amount_val: float) -> str:
    """Format numeric amount into standard INR currency string e.g. ₹5,000 or ₹1,250.50"""
    try:
        val = float(amount_val)
        if val.is_integer():
            return f"₹{int(val):,}"
        return f"₹{val:,.2f}"
    except Exception:
        return f"₹{amount_val}"


def generate_reminder_content(
    schedule_data: Any,
    occurrence_data: Any,
    days_before: int
) -> Dict[str, str]:
    """
    Generates dynamic reminder copy, email subject lines, push payloads,
    and notification types based on the payment category and timing.
    """
    # Extract attributes safely
    name = getattr(schedule_data, 'name', '') or getattr(schedule_data, 'payment_name', 'Scheduled Payment')
    category = (getattr(schedule_data, 'category', '') or 'CUSTOM').upper()
    scheme_name = getattr(schedule_data, 'scheme_name', None) or name
    amount = getattr(occurrence_data, 'amount', None)
    if amount is None:
        amount_minor = getattr(occurrence_data, 'amount_minor_units', getattr(schedule_data, 'amount_minor_units', 0))
        amount = round(amount_minor / 100.0, 2)
    
    amount_str = format_inr(amount)
    due_date = getattr(occurrence_data, 'due_date', None) or getattr(schedule_data, 'next_due_date', date.today())
    if isinstance(due_date, datetime):
        due_date = due_date.date()
    
    date_formatted = due_date.strftime("%d %B %Y") if due_date else "the scheduled date"
    date_short = due_date.strftime("%d %b") if due_date else "soon"

    # -------------------------------------------------------------------------
    # 1. MUTUAL FUND SIPS & INVESTMENTS
    # -------------------------------------------------------------------------
    if 'SIP' in category or 'INVESTMENT' in category or 'RECURRING_DEPOSIT' in category:
        if days_before > 1:
            title = f"Upcoming SIP: {amount_str} for {scheme_name}"
            message = (
                f"Your {amount_str} SIP for {scheme_name} is scheduled for {date_formatted}. "
                "Please ensure sufficient funds are available in your bank account."
            )
            email_subject = f"Upcoming SIP Reminder: {amount_str} scheduled for {date_short}"
            push_body = f"Upcoming SIP: {amount_str} for {scheme_name} is scheduled for {date_short}. Please prepare your funds."
            notif_type = 'SIP_UPCOMING'
        elif days_before == 1:
            title = f"Reminder: SIP Due Tomorrow ({amount_str})"
            message = (
                f"Reminder: Your {amount_str} SIP for {scheme_name} is scheduled for tomorrow. "
                "Please maintain sufficient funds in your account for the auto-debit."
            )
            email_subject = f"Your SIP Payment of {amount_str} Is Due Tomorrow"
            push_body = f"Reminder: Your {amount_str} SIP for {scheme_name} is due tomorrow. Please verify account balance."
            notif_type = 'SIP_UPCOMING'
        elif days_before == 0:
            title = f"SIP Installment Due Today ({amount_str})"
            message = (
                f"Your {amount_str} SIP installment for {scheme_name} is due today. "
                "Please ensure sufficient funds are available for the scheduled debit."
            )
            email_subject = f"Action Required: Your {amount_str} SIP for {scheme_name} is Due Today"
            push_body = f"Your {amount_str} SIP for {scheme_name} is due today. Ensure sufficient funds are available."
            notif_type = 'SIP_DUE_TODAY'
        else:  # Overdue (days_before < 0)
            title = f"SIP Verification Pending: {amount_str}"
            message = (
                f"Your {amount_str} SIP for {scheme_name} was due on {date_formatted}. "
                "Please check your bank statement and mark as paid once debited."
            )
            email_subject = f"Verification Pending: Your {amount_str} SIP for {scheme_name}"
            push_body = f"Your {amount_str} SIP was due on {date_short}. Check your payments dashboard."
            notif_type = 'OVERDUE_PAYMENT'

    # -------------------------------------------------------------------------
    # 2. RECURRING SUBSCRIPTIONS
    # -------------------------------------------------------------------------
    elif 'SUBSCRIPTION' in category:
        if days_before > 1:
            title = f"Upcoming Subscription Renewal: {name}"
            message = f"Your subscription for {name} ({amount_str}) will renew on {date_formatted}."
            email_subject = f"Subscription Renewal in {days_before} Days: {name}"
            push_body = f"{name} ({amount_str}) renews on {date_short}. Check your upcoming payments."
            notif_type = 'SUBSCRIPTION_RENEWAL'
        elif days_before == 1:
            title = f"Subscription Renews Tomorrow: {name}"
            message = f"Your {name} subscription ({amount_str}) renews tomorrow ({date_formatted})."
            email_subject = f"Your {name} Subscription Renews Tomorrow"
            push_body = f"Your {name} subscription renews tomorrow. Check your upcoming payments."
            notif_type = 'SUBSCRIPTION_RENEWAL'
        elif days_before == 0:
            title = f"Subscription Renewal Due Today: {name}"
            message = f"Your {name} subscription renewal of {amount_str} is due today."
            email_subject = f"Due Today: {name} Subscription Renewal ({amount_str})"
            push_body = f"Your {name} subscription of {amount_str} is scheduled for renewal today."
            notif_type = 'SUBSCRIPTION_RENEWAL'
        else:
            title = f"Subscription Status Check: {name}"
            message = f"Your {name} subscription ({amount_str}) was due on {date_formatted}. Mark as paid if renewed."
            email_subject = f"Update Status: {name} Subscription ({amount_str})"
            push_body = f"Check status of {name} subscription ({amount_str}) due on {date_short}."
            notif_type = 'OVERDUE_PAYMENT'

    # -------------------------------------------------------------------------
    # 3. LOAN EMIS
    # -------------------------------------------------------------------------
    elif 'EMI' in category or 'LOAN' in category:
        if days_before > 1:
            title = f"Upcoming EMI: {amount_str} for {name}"
            message = f"Your {amount_str} loan EMI for {name} is due on {date_formatted}. Please keep your account funded."
            email_subject = f"Upcoming EMI Reminder: {amount_str} due on {date_short}"
            push_body = f"Upcoming EMI: {amount_str} for {name} is due on {date_short}. Please ensure sufficient balance."
            notif_type = 'EMI_DUE'
        elif days_before == 1:
            title = f"EMI Due Tomorrow: {amount_str}"
            message = f"Reminder: Your {amount_str} EMI for {name} is due tomorrow. Avoid bounce charges by maintaining sufficient funds."
            email_subject = f"Important: Your {amount_str} EMI for {name} is Due Tomorrow"
            push_body = f"Reminder: Your {amount_str} EMI for {name} is due tomorrow. Please verify account balance."
            notif_type = 'EMI_DUE'
        elif days_before == 0:
            title = f"EMI Payment Due Today: {amount_str}"
            message = f"Your {amount_str} EMI for {name} is scheduled for debit today. Keep sufficient balance ready."
            email_subject = f"Payment Due Today: {amount_str} EMI for {name}"
            push_body = f"Your {amount_str} EMI for {name} is due today. Ensure funds are available for auto-debit."
            notif_type = 'EMI_DUE'
        else:
            title = f"Overdue EMI Alert: {name}"
            message = f"Your {amount_str} EMI for {name} was due on {date_formatted}. Please verify payment to prevent penalty charges."
            email_subject = f"Overdue Alert: Your {amount_str} EMI for {name}"
            push_body = f"Overdue: {name} EMI ({amount_str}) was due on {date_short}. Update status now."
            notif_type = 'OVERDUE_PAYMENT'

    # -------------------------------------------------------------------------
    # 4. BILLS, RENT, UTILITIES, CREDIT CARDS, INSURANCE, FEES, OTHER
    # -------------------------------------------------------------------------
    else:
        label = "Bill"
        if 'CREDIT_CARD' in category:
            label = "Credit Card Bill"
        elif 'INSURANCE' in category:
            label = "Insurance Premium"
        elif 'RENT' in category:
            label = "Rent Payment"
        elif 'EDUCATION' in category:
            label = "Education Fee"
        elif 'UTILITY' in category:
            label = "Utility Bill"
        elif 'TELECOM' in category:
            label = "Mobile/Internet Bill"

        if days_before > 1:
            title = f"Upcoming {label}: {amount_str} for {name}"
            message = f"Your {label.lower()} for {name} ({amount_str}) is due on {date_formatted}."
            email_subject = f"Upcoming {label} Reminder: {name} ({amount_str})"
            push_body = f"Upcoming {label}: {amount_str} for {name} is due on {date_short}."
            notif_type = 'BILL_DUE'
        elif days_before == 1:
            title = f"{label} Due Tomorrow: {amount_str}"
            message = f"Reminder: Your {label.lower()} for {name} ({amount_str}) is due tomorrow ({date_formatted})."
            email_subject = f"Due Tomorrow: {label} for {name} ({amount_str})"
            push_body = f"Reminder: {name} {label.lower()} ({amount_str}) is due tomorrow."
            notif_type = 'BILL_DUE'
        elif days_before == 0:
            title = f"{label} Due Today: {amount_str}"
            message = f"Your {label.lower()} of {amount_str} for {name} is due today. Complete your payment to avoid late fees."
            email_subject = f"Due Today: {label} for {name} ({amount_str})"
            push_body = f"Your {name} {label.lower()} of {amount_str} is due today."
            notif_type = 'BILL_DUE'
        else:
            title = f"Overdue {label}: {name}"
            message = f"Your {label.lower()} of {amount_str} for {name} was due on {date_formatted}. Please complete payment."
            email_subject = f"Overdue Reminder: {label} for {name} ({amount_str})"
            push_body = f"Overdue: {name} {label.lower()} ({amount_str}) was due on {date_short}."
            notif_type = 'OVERDUE_PAYMENT'

    return {
        'title': title,
        'message': message,
        'email_subject': email_subject,
        'push_body': push_body,
        'notification_type': notif_type,
        'amount_str': amount_str,
        'date_formatted': date_formatted
    }
