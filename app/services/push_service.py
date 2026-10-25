"""
Browser Web Push Notification Service for MoneyLeak.

Supports:
- Web Push with VAPID authentication (RFC 8292)
- Multi-device subscription dispatch per user
- Auto-pruning of expired or revoked endpoints (HTTP 404 / 410 Gone)
- Secure payload formatting (title, body, icon, badge, target URL)
"""
import os
import json
from typing import Dict, Any, Tuple
from app.extensions import db
from app.models.payment_notification import PushSubscription

DEFAULT_VAPID_PUBLIC_KEY = os.environ.get(
    'VAPID_PUBLIC_KEY',
    'BB9Fv5DX6dMJ-lt-7UvR3TKYgDUVpD2uUVN5pg-VuSNrWdx0-fqk2I4DFjATVayrYTvAuQ30cgDOhpWXqxvE2Fs'
)

DEFAULT_VAPID_PRIVATE_KEY = os.environ.get(
    'VAPID_PRIVATE_KEY',
    '-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg+AOR5K9p+potfIHv\nnHuR7DDP8/zpJmY50gr5LOigBIShRANCAAQfRb+Q1+nTCfpbfu1L0d0ymIA1FaQ9\nrlFTeaYPlbkja1ncdPn6pNiOAxYwE1Wsq2E7wLkN9HIAzoaVl6sbxNhb\n-----END PRIVATE KEY-----'
)

DEFAULT_VAPID_CLAIM_EMAIL = os.environ.get(
    'VAPID_CLAIM_EMAIL',
    'admin@moneyleak.app'
)

def get_vapid_public_key() -> str:
    """Return the base64 URL-safe VAPID application server public key for frontend subscription."""
    return os.environ.get('VAPID_PUBLIC_KEY') or DEFAULT_VAPID_PUBLIC_KEY

def get_vapid_private_key() -> str:
    """Return the private key used by the backend to sign web push authorization JWTs."""
    return os.environ.get('VAPID_PRIVATE_KEY') or DEFAULT_VAPID_PRIVATE_KEY

def get_vapid_claims() -> Dict[str, str]:
    claim_email = os.environ.get('VAPID_CLAIM_EMAIL') or DEFAULT_VAPID_CLAIM_EMAIL
    sub = f"mailto:{claim_email}" if not claim_email.startswith('mailto:') else claim_email
    return {"sub": sub}


def send_web_push(subscription: PushSubscription, payload_dict: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Delivers a Web Push notification to a specific browser subscription endpoint.
    Automatically deactivates invalid / expired subscriptions (HTTP 404/410).
    """
    if not subscription or not subscription.is_active:
        return False, "Subscription inactive or missing."

    sub_info = subscription.to_webpush_subscription_info()
    payload_str = json.dumps(payload_dict)

    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        # pywebpush not available in current environment
        return False, "pywebpush library not installed."

    try:
        response = webpush(
            subscription_info=sub_info,
            data=payload_str,
            vapid_private_key=get_vapid_private_key(),
            vapid_claims=get_vapid_claims(),
            timeout=10
        )
        if response and response.status_code in (200, 201, 202):
            return True, f"Delivered (HTTP {response.status_code})"
        return False, f"Unexpected response (HTTP {getattr(response, 'status_code', 'unknown')})"

    except WebPushException as ex:
        status_code = getattr(ex.response, 'status_code', None) if getattr(ex, 'response', None) else None
        
        # 404 Not Found or 410 Gone indicates the browser unsubscribed or the endpoint expired
        if status_code in (404, 410):
            try:
                subscription.is_active = False
                db.session.commit()
                return False, f"Subscription expired or revoked (HTTP {status_code}). Endpoint pruned."
            except Exception:
                pass

        return False, f"WebPushException: {ex}"
    except Exception as e:
        return False, f"Delivery error: {str(e)}"
