"""
MoneyLeak Detection Engine — Powered by SpendSense.

Detects spending leaks, recurring subscriptions drain, unusual transactions,
budget overruns, micro-spending, and lifestyle inflation using explainable financial rules.
"""
from typing import List, Dict, Any, Optional
from app.services.spendsense_service import get_spendsense_analysis


def run_leak_detection(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Evaluates SpendSense leak detection rules for the given user and period.
    Generates structured, explainable alert objects and persists new alerts.
    Returns active (non-dismissed) financial alerts for the user.
    """
    analysis = get_spendsense_analysis(user_id, year, month)
    findings = analysis.get('findings', [])
    active_findings = [
        f for f in findings
        if not f.get('is_dismissed') and f.get('status') not in ('DISMISSED', 'NOT_RELEVANT')
    ]
    return active_findings
