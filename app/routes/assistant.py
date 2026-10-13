"""
Financial Assistant routes and Smart Chatbot API for MoneyLeak.
"""
from datetime import date
from flask import Blueprint, render_template, request, jsonify, g
from app.extensions import db, csrf
from app.routes.auth import login_required
from app.services.assistant_service import (
    ASSISTANT_MODULES,
    APP_ROUTES_DIRECTORY,
    handle_assistant_chat,
    run_assistant_module,
    get_user_financial_context
)
from app.services.budget_engine import calculate_budget_summary
from app.services.leak_detection import run_leak_detection
from app.services.goal_engine import get_all_goals_summary

assistant_bp = Blueprint('assistant', __name__)

QUICK_ACTIONS = [
    {
        "id": "qa_dashboard",
        "title": "Explain my dashboard",
        "description": "Understand your monthly outflow, cashflow rings, and budget progress.",
        "icon": "layout-dashboard",
        "prompt": "Can you explain my current dashboard and what the numbers mean?"
    },
    {
        "id": "qa_budget",
        "title": "Help me understand my budget",
        "description": "Review your 50/30/20 allocation across Needs, Wants, and Savings.",
        "icon": "wallet",
        "prompt": "How does my 50/30/20 budget breakdown look for this month?"
    },
    {
        "id": "qa_spending",
        "title": "Analyze my spending",
        "description": "Examine your highest expense categories and monthly outflows.",
        "icon": "pie-chart",
        "prompt": "Analyze my spending this month and show my top expense categories."
    },
    {
        "id": "qa_savings",
        "title": "Explain my savings progress",
        "description": "Review your savings rate %, surplus, and active savings goals.",
        "icon": "target",
        "prompt": "What is my current savings rate and how are my goals progressing?"
    },
    {
        "id": "qa_calculator",
        "title": "Help me use the calculator",
        "description": "Understand SIP contributions, compound interest, and return assumptions.",
        "icon": "calculator",
        "prompt": "How does the investment calculator work and what are the return assumptions?"
    },
    {
        "id": "qa_schemes",
        "title": "Explain investment schemes",
        "description": "Explore curated Indian stocks, equity mutual funds, SIPs, and gold.",
        "icon": "briefcase",
        "prompt": "What investment schemes does MoneyLeak support and what are their risk levels?"
    },
    {
        "id": "qa_transactions",
        "title": "Help me manage transactions",
        "description": "Learn how to record expenses, filter dates, and manage custom categories.",
        "icon": "arrow-left-right",
        "prompt": "How do I add, search, and manage my transactions?"
    },
    {
        "id": "qa_profile",
        "title": "Update profile or settings",
        "description": "Change your Student/Salaried role, currency, avatar, or appearance theme.",
        "icon": "settings",
        "prompt": "How do I update my profile, change my currency, or switch my role?"
    }
]


@assistant_bp.route('/assistant')
@login_required
def view_assistant():
    """Renders the redesigned Financial Assistant landing page."""
    user = g.current_user
    today = date.today()
    summary = calculate_budget_summary(user.id, today.year, today.month)
    alerts = run_leak_detection(user.id, today.year, today.month)
    goals_data = get_all_goals_summary(user.id, user.currency)
    user_context = get_user_financial_context(user)

    # Organize modules by groups
    grouped_modules = {}
    for mod in ASSISTANT_MODULES:
        grp = mod["group"]
        if grp not in grouped_modules:
            grouped_modules[grp] = []
        grouped_modules[grp].append(mod)

    return render_template(
        'assistant.html',
        user=user,
        modules=ASSISTANT_MODULES,
        grouped_modules=grouped_modules,
        quick_actions=QUICK_ACTIONS,
        user_context=user_context,
        summary=summary,
        alerts=alerts,
        goals_data=goals_data
    )


@assistant_bp.route('/api/assistant/chat', methods=['POST'])
@login_required
@csrf.exempt
def api_chat():
    """
    Handles user chat queries with authenticated financial data access,
    contextual route mapping, and AI provider integration.
    """
    user = g.current_user
    data = request.get_json() or {}

    message = (data.get('message') or '').strip()
    page_context = (data.get('page_context') or '').strip()
    history = data.get('history') or []

    if not message:
        return jsonify({'success': False, 'error': 'Message content cannot be empty.'}), 400

    if len(message) > 1000:
        return jsonify({'success': False, 'error': 'Message exceeds maximum length of 1,000 characters.'}), 400

    result = handle_assistant_chat(user, message, page_context=page_context, history=history)
    return jsonify(result)


@assistant_bp.route('/api/assistant/module/<module_id>/run', methods=['POST'])
@login_required
@csrf.exempt
def api_run_module(module_id):
    """Executes a specific Assistant module and returns formatted metrics."""
    user = g.current_user
    result = run_assistant_module(user, module_id)
    return jsonify({'success': True, 'result': result})
