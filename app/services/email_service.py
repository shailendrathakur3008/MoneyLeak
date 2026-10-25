"""
Real Email & OTP Dispatch Service for MoneyLeak.

Dispatches real OTP verification emails directly using:
1. Supabase Auth Email Delivery (Priority 1 — Direct Supabase Auth & Gmail SMTP)
2. Resend API (HTTP REST fallback)
3. Direct Python SMTP / TLS delivery
"""
import os
import json
import smtplib
import urllib.request
import urllib.error
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional
from flask import render_template

DEFAULT_SUPABASE_URL = 'https://roxyqqtfgzrbwqthvrnt.supabase.co'
DEFAULT_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveHlxcXRmZ3pyYndxdGh2cm50Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTIxNDcxNzQsImV4cCI6MjEwNzcyMzE3NH0.osUI_k9rWSEK2EwzDIbnxMEhrYEmBLe1zLhC1baUAXI'


class EmailDispatchResult(tuple):
    """
    Subclasses tuple (success: bool, message: str) for 100% backwards compatibility,
    while providing rich metadata attributes.
    """
    def __new__(cls, success: bool, message: str, provider: str = '', details: list | None = None, delivered: bool = False):
        return super().__new__(cls, (delivered, message))

    def __init__(self, success: bool, message: str, provider: str = '', details: list | None = None, delivered: bool = False):
        self.success = delivered
        self.delivered = delivered
        self.message = message
        self.provider = provider
        self.details = details or []


def _render_otp_email_body(email: str, otp_code: str) -> tuple[str, str]:
    """Renders the HTML email body and returns (html_body, plain_text_body)."""
    plain_text = (
        f"Your MoneyLeak verification code is: {otp_code}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Never share this code with anyone. MoneyLeak will never ask for your verification code.\n\n"
        f"If you did not request this verification, you can safely disregard this email.\n"
        f"— MoneyLeak Financial Intelligence Platform"
    )

    try:
        html_body = render_template('emails/otp_email.html', otp_code=otp_code, token=otp_code, user_email=email)
    except Exception as e:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails', 'otp_email.html')
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    raw = f.read()
                html_body = raw.replace('{{ otp_code or token or "750130" }}', otp_code)
                html_body = html_body.replace('{{ otp_code }}', otp_code).replace('{{ token }}', otp_code)
                html_body = html_body.replace('{{ .Token }}', otp_code)
            except Exception:
                html_body = None
        else:
            html_body = None

        if not html_body:
            html_body = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 20px auto; padding: 24px; background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.08); text-align: center;">
              <div style="display:inline-block; width: 42px; height: 42px; line-height: 42px; border-radius: 12px; background: #cbf432; font-weight: 800; font-size: 20px; margin-bottom: 12px;">ML</div>
              <h2 style="color: #121614; margin-bottom: 8px;">Verification Code</h2>
              <p style="color: #6e756c; font-size: 14px; margin-bottom: 20px;">Use the code below to access your MoneyLeak workspace:</p>
              <div style="background: #161917; color: #ffffff; padding: 18px; border-radius: 12px; font-size: 32px; letter-spacing: 10px; font-weight: 800; font-family: monospace; margin-bottom: 16px;">{otp_code}</div>
              <p style="color: #959e93; font-size: 12px;">Valid for 10 minutes. If you did not request this, ignore this email.</p>
            </div>
            """

    return html_body, plain_text


def send_real_verification_email(email: str, otp_code: str) -> EmailDispatchResult:
    """
    Sends the OTP verification email to the user's inbox directly via Supabase Auth.
    Delivery Priority:
    1. Supabase Auth OTP Service (Directly sends from connected Gmail SMTP)
    2. Resend API (HTTP REST fallback)
    3. Direct Python SMTP
    """
    email = email.strip().lower()
    delivered = False
    provider_used = ''
    details = []

    # -------------------------------------------------------------------------
    # Priority 1: Supabase Auth OTP Service (Direct from Supabase)
    # -------------------------------------------------------------------------
    supabase_url = (os.environ.get('SUPABASE_URL') or DEFAULT_SUPABASE_URL).rstrip('/')
    supabase_anon = os.environ.get('SUPABASE_ANON_KEY') or DEFAULT_SUPABASE_ANON_KEY

    if supabase_url and supabase_anon:
        try:
            req_url = f"{supabase_url}/auth/v1/otp"
            headers = {
                'apikey': supabase_anon,
                'Authorization': f'Bearer {supabase_anon}',
                'Content-Type': 'application/json'
            }
            payload = json.dumps({'email': email, 'create_user': True}).encode('utf-8')
            req = urllib.request.Request(req_url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status in (200, 201):
                    delivered = True
                    provider_used = 'Supabase'
                    details.append("Supabase Auth OTP")
                    print(f"[EmailService] Successfully triggered OTP email to {email} directly from Supabase")
        except urllib.error.HTTPError as he:
            err_msg = he.read().decode('utf-8', errors='ignore')
            print(f"[EmailService] Supabase OTP dispatch returned {he.code}: {err_msg}")
        except Exception as e:
            print(f"[EmailService] Supabase OTP dispatch attempt: {e}")

    # -------------------------------------------------------------------------
    # Priority 2: Resend API (Fallback if Supabase rate-limited or unconfigured)
    # -------------------------------------------------------------------------
    if not delivered:
        resend_api_key = os.environ.get('RESEND_API_KEY', '').strip()
        if resend_api_key:
            html_body, plain_text = _render_otp_email_body(email, otp_code)
            try:
                resend_url = "https://api.resend.com/emails"
                resend_from = (
                    os.environ.get('MAIL_FROM') or
                    os.environ.get('RESEND_FROM') or
                    'MoneyLeak <onboarding@resend.dev>'
                ).strip()

                payload = json.dumps({
                    'from': resend_from,
                    'to': [email],
                    'subject': f"{otp_code} is your MoneyLeak verification code",
                    'html': html_body,
                    'text': plain_text
                }).encode('utf-8')

                req = urllib.request.Request(
                    resend_url,
                    data=payload,
                    headers={
                        'Authorization': f'Bearer {resend_api_key}',
                        'Content-Type': 'application/json',
                        'User-Agent': 'MoneyLeak-Auth/1.0'
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as res:
                    if res.status in (200, 201):
                        delivered = True
                        provider_used = 'Resend API'
                        details.append("Resend API")
                        print(f"[EmailService] Successfully sent OTP to {email} via Resend API")
            except Exception as e:
                print(f"[EmailService] Resend API attempt failed: {e}")

    # -------------------------------------------------------------------------
    # Priority 3: Direct Python SMTP
    # -------------------------------------------------------------------------
    if not delivered:
        smtp_user = (
            os.environ.get('SMTP_USER') or
            os.environ.get('MAIL_USERNAME') or
            os.environ.get('MAIL_DEFAULT_SENDER') or
            ''
        ).strip()
        smtp_pass = (
            os.environ.get('SMTP_PASS') or
            os.environ.get('MAIL_PASSWORD') or
            ''
        ).strip()

        if smtp_user and smtp_pass:
            html_body, plain_text = _render_otp_email_body(email, otp_code)
            smtp_host = (
                os.environ.get('SMTP_HOST') or
                os.environ.get('MAIL_SERVER') or
                ('smtp.gmail.com' if '@gmail.com' in smtp_user else 'localhost')
            ).strip()
            smtp_port = int(os.environ.get('SMTP_PORT') or os.environ.get('MAIL_PORT') or 587)
            smtp_from = (
                os.environ.get('MAIL_FROM') or
                os.environ.get('SMTP_FROM') or
                f"MoneyLeak <{smtp_user}>"
            ).strip()

            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"{otp_code} is your MoneyLeak verification code"
                msg['From'] = smtp_from
                msg['To'] = email

                msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))

                if smtp_port == 465 or os.environ.get('SMTP_USE_SSL', '').lower() in ('true', '1'):
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12)
                    server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, email, msg.as_string())
                    server.quit()
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=12)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, email, msg.as_string())
                    server.quit()

                delivered = True
                provider_used = f"Direct SMTP ({smtp_host})"
                details.append(f"SMTP ({smtp_host})")
            except Exception as smtp_err:
                print(f"[EmailService] Direct SMTP delivery failed: {smtp_err}")

    # Log summary
    if delivered:
        log_msg = f"[Real OTP Service] Sent verification code to {email} directly from {provider_used}"
        user_msg = f"Verification code sent to {email} from Supabase. Please check your inbox and spam folder."
    else:
        log_msg = f"[Real OTP Service] Could not dispatch email to {email}"
        user_msg = f"Email delivery provider not responding. Use the instant access code below."

    print(f"\n{log_msg}\n")

    return EmailDispatchResult(
        success=delivered,
        message=user_msg,
        provider=provider_used,
        details=details,
        delivered=delivered
    )


def verify_real_otp_token(email: str, otp_code: str) -> tuple[bool, dict | None]:
    """
    Verifies the 6-digit OTP token against Supabase Auth API if available.
    Tests verification token types ('magiclink', 'signup', 'email').
    Returns (True, user_payload) if verified, (False, None) otherwise.
    """
    email = email.strip().lower()
    otp_code = otp_code.strip()

    supabase_url = (os.environ.get('SUPABASE_URL') or DEFAULT_SUPABASE_URL).rstrip('/')
    supabase_anon = os.environ.get('SUPABASE_ANON_KEY') or DEFAULT_SUPABASE_ANON_KEY

    if supabase_url and supabase_anon and len(otp_code) == 6:
        for verify_type in ('magiclink', 'signup', 'email'):
            try:
                req_url = f"{supabase_url}/auth/v1/verify"
                headers = {
                    'apikey': supabase_anon,
                    'Authorization': f'Bearer {supabase_anon}',
                    'Content-Type': 'application/json'
                }
                payload = json.dumps({
                    'type': verify_type,
                    'email': email,
                    'token': otp_code
                }).encode('utf-8')
                req = urllib.request.Request(req_url, data=payload, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as res:
                    if res.status in (200, 201):
                        raw_body = res.read().decode('utf-8')
                        data = json.loads(raw_body) if raw_body else {}
                        print(f"[Supabase Auth] Successfully verified OTP for {email} via {verify_type}")
                        return True, data
            except urllib.error.HTTPError:
                # Token not valid for this type, continue to next
                pass
            except Exception as e:
                print(f"[Supabase Auth Verify Exception] {e}")

    return False, None


def _dispatch_raw_email(to_email: str, subject: str, html_body: str, plain_text: str) -> EmailDispatchResult:
    """
    Core dispatcher sending transactional emails through configured Resend API or SMTP.
    Returns EmailDispatchResult with delivery outcome, provider name, and error details.
    """
    to_email = to_email.strip().lower()
    delivered = False
    provider_used = ''
    details = []

    # 1. Resend API
    resend_api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if resend_api_key:
        try:
            resend_url = "https://api.resend.com/emails"
            resend_from = (
                os.environ.get('MAIL_FROM') or
                os.environ.get('RESEND_FROM') or
                'MoneyLeak <notifications@resend.dev>'
            ).strip()

            payload = json.dumps({
                'from': resend_from,
                'to': [to_email],
                'subject': subject,
                'html': html_body,
                'text': plain_text
            }).encode('utf-8')

            req = urllib.request.Request(
                resend_url,
                data=payload,
                headers={
                    'Authorization': f'Bearer {resend_api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'MoneyLeak-Notifications/1.0'
                }
            )
            with urllib.request.urlopen(req, timeout=12) as res:
                if res.status in (200, 201):
                    delivered = True
                    provider_used = 'Resend API'
                    details.append("Resend API")
        except Exception as e:
            details.append(f"Resend error: {e}")
            print(f"[EmailService] Resend dispatch failed: {e}")

    # 2. Direct SMTP
    if not delivered:
        smtp_user = (
            os.environ.get('SMTP_USER') or
            os.environ.get('MAIL_USERNAME') or
            os.environ.get('MAIL_DEFAULT_SENDER') or
            ''
        ).strip()
        smtp_pass = (
            os.environ.get('SMTP_PASS') or
            os.environ.get('MAIL_PASSWORD') or
            ''
        ).strip()

        if smtp_user and smtp_pass:
            smtp_host = (
                os.environ.get('SMTP_HOST') or
                os.environ.get('MAIL_SERVER') or
                ('smtp.gmail.com' if '@gmail.com' in smtp_user else 'localhost')
            ).strip()
            smtp_port = int(os.environ.get('SMTP_PORT') or os.environ.get('MAIL_PORT') or 587)
            smtp_from = (
                os.environ.get('MAIL_FROM') or
                os.environ.get('SMTP_FROM') or
                f"MoneyLeak <{smtp_user}>"
            ).strip()

            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = smtp_from
                msg['To'] = to_email

                msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))

                if smtp_port == 465 or os.environ.get('SMTP_USE_SSL', '').lower() in ('true', '1'):
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12)
                    server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, to_email, msg.as_string())
                    server.quit()
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=12)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, to_email, msg.as_string())
                    server.quit()

                delivered = True
                provider_used = f"SMTP ({smtp_host})"
                details.append(f"SMTP ({smtp_host})")
            except Exception as smtp_err:
                details.append(f"SMTP error: {smtp_err}")
                print(f"[EmailService] Direct SMTP reminder dispatch failed: {smtp_err}")

    if not provider_used:
        provider_used = 'UNCONFIGURED'

    return EmailDispatchResult(
        success=delivered,
        message="Email sent" if delivered else "Provider unconfigured or delivery failed",
        provider=provider_used,
        details=details,
        delivered=delivered
    )


def send_payment_reminder_email(
    user_email: str,
    user_name: str,
    schedule_data: Any,
    occurrence_data: Any,
    days_before: int,
    content_dict: dict | None = None
) -> EmailDispatchResult:
    """
    Renders and dispatches a transactional payment reminder email using the user's payment data.
    """
    from app.services.reminder_service import generate_reminder_content, format_inr

    content = content_dict or generate_reminder_content(schedule_data, occurrence_data, days_before)
    subject = content.get('email_subject', 'Payment Reminder')

    payment_name = getattr(schedule_data, 'name', '') or getattr(schedule_data, 'payment_name', 'Scheduled Payment')
    scheme_name = getattr(schedule_data, 'scheme_name', None) or payment_name
    category = getattr(schedule_data, 'category', 'CUSTOM')

    amount = getattr(occurrence_data, 'amount', None)
    if amount is None:
        amount_minor = getattr(occurrence_data, 'amount_minor_units', getattr(schedule_data, 'amount_minor_units', 0))
        amount = round(amount_minor / 100.0, 2)
    amount_str = format_inr(amount)

    due_date = getattr(occurrence_data, 'due_date', None) or getattr(schedule_data, 'next_due_date', date.today())
    if isinstance(due_date, datetime):
        due_date = due_date.date()
    due_date_str = due_date.strftime("%d %B %Y") if due_date else "Scheduled Date"

    plain_text = (
        f"Hello {user_name},\n\n"
        f"{content.get('message', '')}\n\n"
        f"Payment: {payment_name}\n"
        f"Investment / Scheme: {scheme_name}\n"
        f"Amount: {amount_str}\n"
        f"Scheduled Date: {due_date_str}\n\n"
        "Please ensure sufficient funds are available in your designated bank account.\n"
        "You can review your upcoming payments from your finance dashboard: https://moneyleak.app/payments\n\n"
        "Important: This is a reminder only. No payment has been initiated by this notification.\n\n"
        "— MoneyLeak Finance Dashboard"
    )

    try:
        html_body = render_template(
            'emails/payment_reminder.html',
            subject=subject,
            user_name=user_name,
            headline=content.get('title', 'Upcoming Scheduled Payment'),
            message_body=content.get('message', ''),
            payment_name=payment_name,
            scheme_name=scheme_name,
            category=category,
            category_label=category.replace('_', ' ').title(),
            due_date_str=due_date_str,
            amount_str=amount_str,
            dashboard_url='/payments'
        )
    except Exception as e:
        print(f"[EmailService] Template render fallback: {e}")
        html_body = f"<p>{plain_text.replace(chr(10), '<br>')}</p>"

    return _dispatch_raw_email(
        to_email=user_email,
        subject=subject,
        html_body=html_body,
        plain_text=plain_text
    )

