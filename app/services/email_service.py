"""
Real Email & OTP Dispatch Service for MoneyLeak.

Dispatches real OTP verification emails using:
1. Resend API (HTTP REST — recommended for Vercel serverless & zero port blocking)
2. Direct Python SMTP / TLS delivery (Gmail App Password, Brevo, SendGrid, custom SMTP)
3. Supabase Auth Email Delivery (with rate limit detection)
"""
import os
import json
import smtplib
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template


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
        # Fallback to direct file read or basic inline card
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
    Sends the 6-digit OTP verification email to the user's inbox.
    Checks delivery providers in priority order:
    1. Resend API (HTTP REST — fastest, highest inbox rate, optimal for Vercel)
    2. Direct SMTP (Gmail App Password, Brevo, SendGrid, custom mail server)
    3. Supabase Auth OTP (built-in auth mailer)
    """
    email = email.strip().lower()
    delivered = False
    provider_used = ''
    details = []

    html_body, plain_text = _render_otp_email_body(email, otp_code)

    # -------------------------------------------------------------------------
    # Option 1: Resend API (Recommended for Vercel Serverless)
    # -------------------------------------------------------------------------
    resend_api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if resend_api_key:
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
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8', errors='ignore')
            print(f"[EmailService] Resend API error ({he.code}): {err_body}")
        except Exception as e:
            print(f"[EmailService] Resend API attempt failed: {e}")

    # -------------------------------------------------------------------------
    # Option 2: Direct Python SMTP (Gmail App Password, Brevo, custom SMTP)
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
            smtp_host = (
                os.environ.get('SMTP_HOST') or
                os.environ.get('MAIL_SERVER') or
                ('smtp.gmail.com' if '@gmail.com' in smtp_user else 'localhost')
            ).strip()
            smtp_port = int(os.environ.get('SMTP_PORT') or os.environ.get('MAIL_PORT') or (465 if smtp_host == 'smtp.gmail.com' and not os.environ.get('SMTP_PORT') else 587))
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
                print(f"[EmailService] Successfully sent OTP to {email} via {smtp_host}")
            except Exception as smtp_err:
                print(f"[EmailService] Direct SMTP delivery failed: {smtp_err}")

    # -------------------------------------------------------------------------
    # Option 3: Supabase Auth OTP Service
    # -------------------------------------------------------------------------
    supabase_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    supabase_anon = os.environ.get('SUPABASE_ANON_KEY', '')

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
                    # Only mark as delivered if neither Resend nor SMTP handled it
                    if not delivered:
                        delivered = True
                        provider_used = 'Supabase Auth OTP'
                    details.append("Supabase Auth OTP")
        except urllib.error.HTTPError as he:
            err_msg = he.read().decode('utf-8', errors='ignore')
            print(f"[EmailService] Supabase OTP dispatch returned {he.code}: {err_msg}")
        except Exception as e:
            print(f"[EmailService] Supabase OTP dispatch attempt: {e}")

    # Log summary
    if delivered:
        log_msg = f"[Real OTP Service] Sent verification code to {email} via {provider_used}"
        user_msg = f"Verification code sent to {email}. Please check your inbox and spam folder."
    else:
        log_msg = f"[Real OTP Service] No configured email delivery provider available for {email}"
        user_msg = f"Email delivery provider not configured. Use the instant access code below."

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
    Verifies the OTP token against Supabase Auth API if available.
    Tests verification token types ('email', 'magiclink', 'signup').
    Returns (True, user_payload) if verified, (False, None) otherwise.
    """
    email = email.strip().lower()
    otp_code = otp_code.strip()

    supabase_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    supabase_anon = os.environ.get('SUPABASE_ANON_KEY', '')

    if supabase_url and supabase_anon and len(otp_code) == 6:
        for verify_type in ('email', 'magiclink', 'signup'):
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
            except urllib.error.HTTPError as e:
                # 403 or 400 means token not valid for this type, continue to next type
                pass
            except Exception as e:
                print(f"[Supabase Auth Verify Exception] {e}")

    return False, None
