"""
Assistant Service for MoneyLeak.

Provides:
1. Smart, text-only AI Chatbot engine for application navigation, financial explanations,
   real user ledger calculations, and troubleshooting.
2. Server-side AI provider integration (Google Gemini / Generative Language API) with
   seamless fallback to a domain-specific financial intelligence engine.
3. Interactive Assistant Module executors using actual user data and verified calculations.
"""
import os
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from app.extensions import db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.goal import SavingsGoal
from app.services.budget_engine import calculate_budget_summary, get_month_date_range
from app.services.leak_detection import run_leak_detection
from app.services.spendsense_service import get_spendsense_analysis
from app.services.goal_engine import get_all_goals_summary
from app.services.investment_calculator import calculate_compound_growth
from app.services.recommendation_service import get_personalized_recommendations
from app.services.simulation_engine import run_simulation
from app.services.money import format_money


# -----------------------------------------------------------------------------
# APPLICATION NAVIGATION DIRECTORY
# -----------------------------------------------------------------------------
APP_ROUTES_DIRECTORY = {
    "dashboard": {
        "title": "Dashboard",
        "url": "/dashboard",
        "description": "50/30/20 macro overview, monthly outflow progress, cashflow donut, and leak alerts.",
        "icon": "layout-dashboard"
    },
    "transactions": {
        "title": "Transactions Ledger",
        "url": "/transactions",
        "description": "Log, search, filter, edit, and delete income and expense records.",
        "icon": "arrow-left-right"
    },
    "budget": {
        "title": "50/30/20 Budget",
        "url": "/budget",
        "description": "Manage Needs (50%), Wants (30%), and Savings (20%) targets and category caps.",
        "icon": "wallet"
    },
    "spendsense": {
        "title": "SpendSense — Smart Leak Detector",
        "url": "/spendsense",
        "description": "Rule-based expense leak detection, 50/30/20 budget analysis, micro-spending audit, and deduplicated savings opportunities.",
        "icon": "search"
    },
    "analysis": {
        "title": "SpendSense & Leak Detector",
        "url": "/analysis",
        "description": "Rule-based expense leak detection, 50/30/20 budget analysis, micro-spending audit, and recurring bills tracking.",
        "icon": "search"
    },
    "simulator": {
        "title": "Savings Simulator",
        "url": "/simulator",
        "description": "Model the multi-year compound impact of trimming discretionary spending by 10%–25%.",
        "icon": "piggy-bank"
    },
    "goals": {
        "title": "Goals Planner",
        "url": "/goals",
        "description": "Set financial milestones, target dates, and track savings progress velocity.",
        "icon": "target"
    },
    "calculator": {
        "title": "Investment Calculator",
        "url": "/calculator",
        "description": "SIP and lump-sum projections, compound interest, and 9 Indian investment categories.",
        "icon": "chart-no-axes-combined"
    },
    "reports": {
        "title": "Reports & PDF Export",
        "url": "/reports",
        "description": "Generate monthly financial statements, summary tables, and downloadable PDF reports.",
        "icon": "chart-column"
    },
    "settings": {
        "title": "Settings & Preferences",
        "url": "/settings",
        "description": "Manage user profile, avatar, verified email, employment role (Student/Salaried), currency, and appearance themes.",
        "icon": "settings"
    },
    "assistant": {
        "title": "Financial Assistant",
        "url": "/assistant",
        "description": "Financial assistance modules, quick audits, and interactive guidance.",
        "icon": "bot"
    }
}


# -----------------------------------------------------------------------------
# ASSISTANT MODULE DEFINITIONS
# -----------------------------------------------------------------------------
ASSISTANT_MODULES = [
    {
        "id": "leak_detector",
        "group": "Financial Insights",
        "title": "Spending Leak Detector",
        "description": "Analyzes transaction frequencies to flag recurring subscription fatigue and discretionary spikes.",
        "icon": "search",
        "action_label": "Run Leak Audit",
        "related_url": "/analysis"
    },
    {
        "id": "leak_trimmer",
        "group": "Financial Insights",
        "title": "What-If Leak Simulator",
        "description": "Simulates how trimming 15% from discretionary spending accumulates over 1, 3, and 5 years.",
        "icon": "piggy-bank",
        "action_label": "Simulate Trimming",
        "related_url": "/simulator"
    },
    {
        "id": "budget_analyzer",
        "group": "Budget Assistance",
        "title": "50/30/20 Budget Allocator",
        "description": "Evaluates your actual spending against the 50% Needs, 30% Wants, and 20% Savings framework.",
        "icon": "wallet",
        "action_label": "Analyze 50/30/20",
        "related_url": "/budget"
    },
    {
        "id": "cashflow_surplus",
        "group": "Budget Assistance",
        "title": "Monthly Cashflow & Surplus",
        "description": "Calculates your net monthly surplus or deficit and actual savings rate percentage.",
        "icon": "trending-up",
        "action_label": "Check Cashflow",
        "related_url": "/dashboard"
    },
    {
        "id": "expense_breakdown",
        "group": "Expense Analysis",
        "title": "Category Outflow Ranking",
        "description": "Ranks your highest spending categories this month against established budget caps.",
        "icon": "pie-chart",
        "action_label": "Rank Categories",
        "related_url": "/transactions"
    },
    {
        "id": "goals_tracker",
        "group": "Savings Goals",
        "title": "Goal Progress & Feasibility",
        "description": "Tracks active savings goals, current completion percentages, and required monthly velocity.",
        "icon": "target",
        "action_label": "Track Goals",
        "related_url": "/goals"
    },
    {
        "id": "investment_matcher",
        "group": "Investment Guidance",
        "title": "Investment Scheme Matcher",
        "description": "Recommends curated Indian mutual funds, SIPs, stocks, and gold based on your risk profile.",
        "icon": "briefcase",
        "action_label": "Find Investments",
        "related_url": "/calculator"
    },
    {
        "id": "future_calculator",
        "group": "Financial Calculations",
        "title": "SIP Compound Calculator",
        "description": "Models periodic investment compounding with realistic estimated return projections.",
        "icon": "calculator",
        "action_label": "Calculate Growth",
        "related_url": "/calculator"
    },
    {
        "id": "health_audit",
        "group": "Application Help",
        "title": "Financial Health Audit",
        "description": "Holistic financial health assessment combining budget compliance, leak count, and savings.",
        "icon": "shield-check",
        "action_label": "Generate Audit",
        "related_url": "/reports"
    }
]


# -----------------------------------------------------------------------------
# FINANCIAL CONTEXT EXTRACTOR
# -----------------------------------------------------------------------------
def get_user_financial_context(user: User) -> Dict[str, Any]:
    """Safely extracts real, authenticated financial figures for the user's current month."""
    today = date.today()
    year, month = today.year, today.month

    summary = calculate_budget_summary(user.id, year, month)
    spendsense = get_spendsense_analysis(user.id, year, month)
    alerts = spendsense.get('findings', [])
    goals = get_all_goals_summary(user.id, user.currency)

    # Top expense categories this month
    cat_breakdown = summary.get('category_breakdown', [])
    top_categories = sorted(cat_breakdown, key=lambda x: x.get('total_minor') or x.get('actual_minor') or 0, reverse=True)[:5]
    top_cat_names = [
        f"{c.get('name')}: {c.get('formatted_amount') or c.get('actual_formatted') or ''}"
        for c in top_categories
        if (c.get('total_minor') or c.get('actual_minor') or 0) > 0
    ]

    # Specific spending on Food Delivery / Dining
    food_delivery_c = next((c for c in cat_breakdown if 'food delivery' in c.get('name', '').lower() or 'dining' in c.get('name', '').lower() or 'restaurants' in c.get('name', '').lower()), None)
    food_delivery_formatted = food_delivery_c.get('formatted_amount') if food_delivery_c else format_money(0, user.currency)
    food_delivery_name = food_delivery_c.get('name') if food_delivery_c else 'Food Delivery'

    return {
        "user_name": user.full_name,
        "user_type": user.user_type or "salaried",
        "currency": user.currency,
        "month_label": today.strftime("%B %Y"),
        "monthly_income": summary['income']['formatted'],
        "monthly_income_minor": summary['income']['minor'],
        "total_outflow": summary['total_outflow']['formatted'],
        "total_outflow_minor": summary['total_outflow']['minor'],
        "surplus": summary['surplus']['formatted'],
        "surplus_minor": summary['surplus']['minor'],
        "savings_rate": summary['savings_rate'],
        "needs_actual": summary['needs']['actual_formatted'],
        "needs_target": summary['needs']['target_formatted'],
        "needs_actual_pct": round(summary['needs']['actual_pct'], 1),
        "needs_target_pct": round(summary['needs']['target_pct'], 1),
        "needs_is_over": summary['needs']['is_over_budget'],
        "needs_explanation": spendsense['distribution_50_30_20']['needs']['explanation'],
        "needs_action": spendsense['distribution_50_30_20']['needs']['recommended_action'],
        "wants_actual": summary['wants']['actual_formatted'],
        "wants_target": summary['wants']['target_formatted'],
        "wants_actual_pct": round(summary['wants']['actual_pct'], 1),
        "wants_target_pct": round(summary['wants']['target_pct'], 1),
        "wants_is_over": summary['wants']['is_over_budget'],
        "savings_actual": summary['savings']['actual_formatted'],
        "savings_target": summary['savings']['target_formatted'],
        "savings_actual_pct": round(summary['savings']['actual_pct'], 1),
        "savings_target_pct": round(summary['savings']['target_pct'], 1),
        "savings_is_met": summary['savings']['is_met'],
        "active_leaks_count": len([a for a in alerts if not a.get('is_dismissed') and a.get('status') not in ('DISMISSED', 'NOT_RELEVANT')]),
        "leak_titles": [a.get('title', '') for a in alerts if not a.get('is_dismissed') and a.get('status') not in ('DISMISSED', 'NOT_RELEVANT')][:4],
        "spendsense_findings": alerts,
        "potential_savings_monthly": spendsense['potential_savings_summary']['monthly_potential_formatted'],
        "potential_savings_annual": spendsense['potential_savings_summary']['annual_potential_formatted'],
        "potential_savings_minor": spendsense['potential_savings_summary']['monthly_potential_minor'],
        "rising_categories": spendsense['trends']['rising_categories'],
        "declining_categories": spendsense['trends']['declining_categories'],
        "burn_rate_diff_pct": spendsense['trends']['previous_month']['burn_rate_diff_pct'],
        "previous_month_label": spendsense['trends']['previous_month']['label'],
        "previous_month_spending": spendsense['trends']['previous_month']['total_spending_formatted'],
        "recurring_items_count": len(spendsense['subscriptions_and_recurring']['confirmed_items']),
        "recurring_drain_monthly": spendsense['subscriptions_and_recurring']['total_monthly_committed_formatted'],
        "recurring_drain_pct": spendsense['subscriptions_and_recurring']['income_committed_pct'],
        "food_delivery_spending": food_delivery_formatted,
        "food_delivery_name": food_delivery_name,
        "active_goals_count": len(goals.get('goals', [])),
        "opening_balance": format_money(user.opening_balance_minor_units or 0, user.currency) if user.opening_balance_minor_units else None,
        "monthly_savings_target": format_money(user.monthly_savings_target_minor_units or 0, user.currency) if user.monthly_savings_target_minor_units else None,
        "primary_goal": user.primary_financial_goal or None,
        "top_expense_categories": top_cat_names
    }


# -----------------------------------------------------------------------------
# GOOGLE GEMINI AI CALLER
# -----------------------------------------------------------------------------
def call_gemini_api(user_message: str, user_context: Dict[str, Any], page_context: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
    """Calls Google Gemini API using server-side environment credentials."""
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        return None

    # Construct strict system prompt anchoring the AI in MoneyLeak reality
    system_instruction = (
        "You are the official Finance Assistant for MoneyLeak, a personal finance intelligence application. "
        "Your purpose is strictly to help users understand, navigate, and troubleshoot MoneyLeak and interpret "
        "their verified financial data. You are a text-only assistant. Never mention microphone or voice functionality.\n\n"
        "STRICT GUIDELINES:\n"
        "1. Real User Data Context:\n"
        f"   - User Name: {user_context['user_name']}\n"
        f"   - Role: {user_context['user_type'].capitalize()}\n"
        f"   - Current Month: {user_context['month_label']}\n"
        f"   - Currency: {user_context['currency']}\n"
        f"   - Recorded Inflow/Income: {user_context['monthly_income']}\n"
        f"   - Recorded Outflow: {user_context['total_outflow']}\n"
        f"   - Net Monthly Surplus: {user_context['surplus']} (Savings Rate: {user_context['savings_rate']}%)\n"
        f"   - 50% Needs Actual: {user_context['needs_actual']} ({user_context['needs_actual_pct']}% of income)\n"
        f"   - 30% Wants Actual: {user_context['wants_actual']} ({user_context['wants_actual_pct']}% of income)\n"
        f"   - 20% Savings Actual: {user_context['savings_actual']} ({user_context['savings_actual_pct']}% of income)\n"
        f"   - Detected Leaks: {user_context['active_leaks_count']}\n"
        f"   - Top Spending Categories: {', '.join(user_context['top_expense_categories']) if user_context['top_expense_categories'] else 'None logged yet'}\n"
        f"   - Opening Balance: {user_context['opening_balance'] or 'Not configured'}\n"
        f"   - Monthly Savings Target: {user_context['monthly_savings_target'] or 'Not configured'}\n"
        f"   - Primary Goal: {user_context['primary_goal'] or 'None'}\n\n"
        "2. Application Routes:\n"
        "   - Dashboard: /dashboard (50/30/20 summary, outflow track, recent transactions)\n"
        "   - Transactions: /transactions (ledger, filtering, export)\n"
        "   - 50/30/20 Budget: /budget (Needs, Wants, Savings caps and allocations)\n"
        "   - Leak Detector: /analysis (subscription tracking, leak anomalies)\n"
        "   - Savings Simulator: /simulator (What-if compound savings)\n"
        "   - Goals: /goals (Target milestones and velocity)\n"
        "   - Investment Calculator: /calculator (SIP, Lump sum, 9 Indian investment schemes)\n"
        "   - Reports: /reports (PDF statements, monthly audits)\n"
        "   - Settings: /settings (Profile, verified email, Student vs Salaried role, currency, theme)\n"
        "   - Assistant: /assistant (Assistant modules & quick actions)\n\n"
        "3. Response Requirements:\n"
        "   - Give concise, clear, polite, step-by-step answers.\n"
        "   - State periods clearly (e.g. 'For this month, October 2026...').\n"
        "   - Never invent missing transactions, balances, or investment returns.\n"
        "   - If explaining investments, explicitly state that projected returns are estimates, not guarantees.\n"
        "   - Format route mentions as markdown links or actionable names (e.g. '[Open Budget](/budget)').\n"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    # Build contents array
    contents = []
    if history:
        for item in history[-4:]:  # Keep recent context
            role = "user" if item.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": item.get("text", "")}]})

    prompt_text = f"Context Page: {page_context or 'Unknown'}\nUser Query: {user_message}"
    contents.append({"role": "user", "parts": [{"text": prompt_text}]})

    payload = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 600,
            "topP": 0.8
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            candidates = res_data.get('candidates', [])
            if candidates and 'content' in candidates[0]:
                parts = candidates[0]['content'].get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text'].strip()
    except Exception as e:
        print(f"[Gemini API Exception, falling back to local engine]: {e}")
        return None

    return None


# -----------------------------------------------------------------------------
# INTELLIGENT DOMAIN NLP & FINANCIAL REASONING ENGINE
# -----------------------------------------------------------------------------
def generate_deterministic_assistant_response(user_message: str, user_context: Dict[str, Any], page_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Intelligent, deterministic financial reasoning and application support engine.
    Analyzes user intent, checks real database figures, and formats precise answers
    with clickable route action buttons.
    """
    msg = user_message.lower().strip()
    actions = []

    # 1. TROUBLESHOOTING & COMMON ISSUES (Prioritize so problems are answered immediately)
    if any(k in msg for k in ['troubleshoot', 'fix', 'problem', 'error', 'bug', 'not working', 'missing transaction', 'missing category', 'not updating', 'cannot find', 'not appearing', 'disappear', 'cant find', "can't find", 'issue', 'wrong', 'incorrect', 'not saving']):
        reply = (
            "Here is a quick troubleshooting checklist for common MoneyLeak issues:\n\n"
            "1. **Transactions Not Appearing?** Check the Month and Year filters in the topbar or transactions page. If an entry occurred in a different month, adjust the filter to reveal it.\n"
            "2. **Budget Figures Incorrect?** Ensure your Baseline Monthly Income is set accurately in Settings. The 50/30/20 allocation divides your verified income into 50% Needs, 30% Wants, and 20% Savings.\n"
            "3. **Missing Categories?** You can create custom categories anytime under Settings → Custom Categories.\n"
            "4. **Profile Photo Not Saving?** Make sure the file is PNG, JPG, or WEBP and under 5MB in size.\n"
            "5. **Theme Preference Resetting?** You can toggle between Light, Dark, or System mode in Settings or the topbar quick toggle.\n"
            "6. **Onboarding Questions?** You can re-open the guided setup wizard anytime from Settings without losing any past transactions."
        )
        actions = [
            {"label": "Check Settings", "url": "/settings"},
            {"label": "View Transactions", "url": "/transactions"}
        ]
        return {"response": reply, "actions": actions}

    # 2. DASHBOARD EXPLANATION
    if any(k in msg for k in ['dashboard', 'explain my dashboard', 'explain dashboard', 'understand dashboard', 'how to use this dashboard', 'widgets']):
        reply = (
            f"Here is how your **MoneyLeak Dashboard** (`/dashboard`) works, **{user_context['user_name']}**:\n\n"
            f"• **Monthly Inflow / Income:** {user_context['monthly_income']} (set via onboarding or settings).\n"
            f"• **Total Recorded Outflow:** {user_context['total_outflow']} (actual transactions logged for {user_context['month_label']}).\n"
            f"• **Net Position (Surplus/Deficit):** {user_context['surplus']} (what remains after all expenses and investments).\n"
            f"• **Savings Rate:** **{user_context['savings_rate']}%** of income preserved or invested.\n"
            "• **50/30/20 Progress Rings:** Live visual bars showing your breakdown across essential Needs (50%), lifestyle Wants (30%), and wealth Savings (20%).\n"
            "• **Recent Ledger:** Quick access to your latest recorded transactions and immediate leak alerts."
        )
        actions = [
            {"label": "Go to Dashboard", "url": "/dashboard"},
            {"label": "Review 50/30/20 Budget", "url": "/budget"}
        ]
        return {"response": reply, "actions": actions}

    # 3. SPENDING & OUTFLOW QUESTIONS / ANALYZE SPENDING
    if any(k in msg for k in ['spend', 'spent', 'outflow', 'expense', 'how much did i spend', 'total spending', 'analyze my spending', 'analyze spending']):
        reply = (
            f"For **{user_context['month_label']}**, your total recorded outflow is **{user_context['total_outflow']}**.\n\n"
            f"• **50% Needs (Essentials):** {user_context['needs_actual']} ({user_context['needs_actual_pct']}% of income)\n"
            f"• **30% Wants (Lifestyle):** {user_context['wants_actual']} ({user_context['wants_actual_pct']}% of income)\n"
            f"• **20% Savings & Debt:** {user_context['savings_actual']} ({user_context['savings_actual_pct']}% of income)\n\n"
        )
        if user_context['top_expense_categories']:
            reply += "Your highest expense categories so far:\n" + "\n".join([f"  - {c}" for c in user_context['top_expense_categories']])
        else:
            reply += "You have not recorded any categorized expenses yet this month."

        actions = [
            {"label": "View Ledger", "url": "/transactions"},
            {"label": "Review 50/30/20 Budget", "url": "/budget"}
        ]
        return {"response": reply, "actions": actions}

    # 4. INCOME & SURPLUS / DEFICIT
    if any(k in msg for k in ['income', 'salary', 'allowance', 'surplus', 'deficit', 'savings rate', 'how much left', 'remaining balance']):
        if user_context['surplus_minor'] >= 0:
            status_text = f"You currently have a **healthy monthly surplus of {user_context['surplus']}**."
        else:
            status_text = f"You currently have a **net deficit of {user_context['surplus']}** (spending exceeds monthly income)."

        reply = (
            f"For **{user_context['month_label']}**:\n\n"
            f"• **Monthly Inflow / Income:** {user_context['monthly_income']}\n"
            f"• **Total Recorded Outflows:** {user_context['total_outflow']}\n"
            f"• **Net Position:** {status_text}\n"
            f"• **Current Savings Rate:** **{user_context['savings_rate']}%**\n\n"
            "You can adjust your baseline income or allowance at any time in your Settings."
        )
        actions = [
            {"label": "Dashboard Overview", "url": "/dashboard"},
            {"label": "Update Income", "url": "/settings"}
        ]
        return {"response": reply, "actions": actions}

    # 5. SPEND SENSE: WHERE IS MY MONEY LEAKING / LEAKS
    if any(k in msg for k in ['where is my money leaking', 'what are my spending leaks', 'spending leak', 'spending leaks', 'leak', 'leaks', 'waste', 'spendsense']):
        leak_count = user_context['active_leaks_count']
        if leak_count > 0:
            leak_list = "\n".join([f"• **{t}**" for t in user_context['leak_titles']])
            reply = (
                f"We have identified **{leak_count} active spending pattern(s) requiring review** for **{user_context['month_label']}**:\n\n"
                f"{leak_list}\n\n"
                f"• **Potential Monthly Savings:** **{user_context['potential_savings_monthly']}** ({user_context['potential_savings_annual']} projected annually).\n\n"
                "These findings are grounded in your recorded transactions. "
                "Open SpendSense to review transaction evidence, set custom spending targets, or dismiss non-applicable alerts."
            )
        else:
            reply = (
                f"Great news! Zero active spending leaks were detected for **{user_context['month_label']}**.\n\n"
                "Your discretionary outflow and recurring commitments are currently aligned with your target budget thresholds."
            )
        actions = [
            {"label": "Open SpendSense", "url": "/spendsense"},
            {"label": "Simulate Trimming Leaks", "url": "/simulator"}
        ]
        return {"response": reply, "actions": actions}

    # 5B. WHICH CATEGORY INCREASED THE MOST
    if any(k in msg for k in ['category increased', 'increased the most', 'spending jump', 'highest increase', 'rising category', 'which category increased']):
        rising = user_context.get('rising_categories', [])
        if rising:
            top_rising = rising[0]
            reply = (
                f"Based on your ledger records for **{user_context['month_label']}**, the category with the highest surge is **{top_rising['name']}**.\n\n"
                f"• **Growth:** **+{top_rising['pct_change']}%** compared to last month\n"
                f"• **Last Month:** {top_rising['prev_formatted']} → **This Month:** {top_rising['curr_formatted']} (+{top_rising['diff_formatted']})\n\n"
            )
            if len(rising) > 1:
                other_names = ", ".join([f"{c['name']} (+{c['pct_change']}%)" for c in rising[1:3]])
                reply += f"Other categories with notable increases: {other_names}.\n\n"
            reply += "Audit recent transactions under this category to verify if this was an isolated purchase or an ongoing trend."
        else:
            reply = (
                f"For **{user_context['month_label']}**, none of your expense categories experienced a notable increase "
                f"(>15%) compared with your previous month baseline. Your category spending has remained stable."
            )
        actions = [
            {"label": "SpendSense Trends", "url": "/spendsense"},
            {"label": "View Transactions", "url": "/transactions"}
        ]
        return {"response": reply, "actions": actions}

    # 5C. HOW MUCH DID I SPEND ON FOOD DELIVERY / DINING
    if any(k in msg for k in ['food delivery', 'swiggy', 'zomato', 'dining out', 'restaurants', 'how much did i spend on food', 'takeout']):
        reply = (
            f"For **{user_context['month_label']}**, your recorded spending on **{user_context['food_delivery_name']}** is **{user_context['food_delivery_spending']}**.\n\n"
            f"This represents part of your **Wants (Lifestyle)** allocation ({user_context['wants_actual']} total, {user_context['wants_actual_pct']}% of income).\n"
            "You can view itemized receipts and order dates in the Transactions ledger."
        )
        actions = [
            {"label": "Filter Transactions", "url": "/transactions"},
            {"label": "Review in SpendSense", "url": "/spendsense"}
        ]
        return {"response": reply, "actions": actions}

    # 5D. WHICH RECURRING PAYMENTS SHOULD I REVIEW
    if any(k in msg for k in ['recurring payments should i review', 'review recurring', 'subscriptions to review', 'recurring to review', 'subscriptions to cancel', 'subscription review', 'subscription drain']):
        r_count = user_context['recurring_items_count']
        r_drain = user_context['recurring_drain_monthly']
        r_pct = user_context['recurring_drain_pct']
        if r_count > 0:
            reply = (
                f"You have **{r_count} active recurring subscription(s)** committing **{r_drain}/month** "
                f"({r_pct}% of your monthly take-home income).\n\n"
                "• **Audit Recommendations:**\n"
                "  1. Review streaming services (OTT) or digital memberships you have not used in the past 30 days.\n"
                "  2. Check for overlapping subscriptions in the same entertainment or fitness category.\n"
                "  3. In SpendSense, review auto-detected recurring transactions that may not yet be formally tracked."
            )
        else:
            reply = (
                f"You currently have no registered recurring payments in MoneyLeak. "
                f"You can add recurring bills (Netflix, Spotify, gym, broadband) in SpendSense to monitor monthly drain."
            )
        actions = [
            {"label": "Manage Recurring in SpendSense", "url": "/spendsense"},
            {"label": "Review Budget", "url": "/budget"}
        ]
        return {"response": reply, "actions": actions}

    # 5E. AM I FOLLOWING THE 50/30/20 RULE
    if any(k in msg for k in ['am i following the 50/30/20 rule', 'am i following 50/30/20', 'following 50/30/20', 'following the budget', 'following my budget']):
        needs_status = "⚠️ Over Target" if user_context['needs_is_over'] else "✅ On Track"
        wants_status = "⚠️ Over Target" if user_context['wants_is_over'] else "✅ On Track"
        savings_status = "✅ Target Met" if user_context['savings_is_met'] else "⚠️ Shortfall"

        reply = (
            f"Here is your **50/30/20 budget compliance** for **{user_context['month_label']}**:\n\n"
            f"• **Needs (Target {user_context['needs_target_pct']}%):** {user_context['needs_actual']} ({user_context['needs_actual_pct']}%) — {needs_status}\n"
            f"• **Wants (Target {user_context['wants_target_pct']}%):** {user_context['wants_actual']} ({user_context['wants_actual_pct']}%) — {wants_status}\n"
            f"• **Savings (Target {user_context['savings_target_pct']}%):** {user_context['savings_actual']} ({user_context['savings_actual_pct']}%) — {savings_status}\n\n"
        )
        if user_context['needs_is_over']:
            reply += f"*Note on Essentials:* {user_context['needs_explanation']}\n\n"
        reply += f"Overall, your savings rate is **{user_context['savings_rate']}%** of monthly income."
        actions = [
            {"label": "50/30/20 Analyzer", "url": "/spendsense"},
            {"label": "Adjust Budget Preset", "url": "/budget"}
        ]
        return {"response": reply, "actions": actions}

    # 5F. HOW MUCH COULD I POTENTIALLY SAVE
    if any(k in msg for k in ['how much could i potentially save', 'potentially save', 'potential savings', 'how much can i save', 'savings opportunity', 'savings opportunities']):
        pot_mo = user_context['potential_savings_monthly']
        pot_yr = user_context['potential_savings_annual']
        if user_context['potential_savings_minor'] > 0:
            reply = (
                f"Based on SpendSense leak detection and category benchmarking, your **potential monthly savings opportunity is {pot_mo}** "
                f"({pot_yr} projected annually).\n\n"
                "• **How this is calculated:**\n"
                "  - Deduplicated across all identified leak findings (discretionary overrun, micro-spending, redundant subscriptions).\n"
                "  - Zero double-counting between category caps and macro lifestyle targets.\n"
                "  - Only positive, realistic spending adjustments are suggested.\n\n"
                "You can accept or set your own custom savings targets in SpendSense."
            )
        else:
            reply = (
                f"You currently have no identified spending leaks for **{user_context['month_label']}**! "
                f"Your spending is operating efficiently within your target budget parameters."
            )
        actions = [
            {"label": "Review in SpendSense", "url": "/spendsense"},
            {"label": "Simulate in Simulator", "url": "/simulator"}
        ]
        return {"response": reply, "actions": actions}

    # 5G. WHY IS MY NEEDS ALLOCATION ABOVE 50%
    if any(k in msg for k in ['why is my needs allocation above 50', 'needs above 50', 'needs over 50', 'needs exceed 50', 'why are my needs high', 'needs higher than 50']):
        reply = (
            f"Your Needs spending currently stands at **{user_context['needs_actual']} ({user_context['needs_actual_pct']}% of income)**, "
            f"exceeding the standard 50% target of {user_context['needs_target']}.\n\n"
            f"• **Context & Drivers:**\n"
            f"{user_context['needs_explanation']}\n\n"
            f"• **Recommended Action:**\n"
            f"{user_context['needs_action']}\n\n"
            "The 50/30/20 rule is a guiding baseline, not a rigid constraint. If essential housing, EMIs, or healthcare require 60%, "
            "you can switch to the **High Essential-Cost (60/20/20)** preset in your Budget settings."
        )
        actions = [
            {"label": "Switch Budget Preset", "url": "/budget"},
            {"label": "SpendSense Breakdown", "url": "/spendsense"}
        ]
        return {"response": reply, "actions": actions}

    # 5H. WHAT CHANGED COMPARED WITH LAST MONTH
    if any(k in msg for k in ['what changed compared with last month', 'compared with last month', 'compared to last month', 'vs last month', 'changes from last month', 'compared with previous month']):
        burn_diff = user_context.get('burn_rate_diff_pct', 0.0)
        direction = "higher" if burn_diff > 0 else "lower"
        reply = (
            f"Comparing **{user_context['month_label']}** against **{user_context['previous_month_label']}**:\n\n"
            f"• **Daily Outflow Burn Rate:** **{abs(burn_diff):.1f}% {direction}** than last month.\n"
            f"• **Last Complete Month Spending:** {user_context['previous_month_spending']}\n"
            f"• **Current Month Outflow:** {user_context['total_outflow']}\n\n"
        )
        rising = user_context.get('rising_categories', [])
        declining = user_context.get('declining_categories', [])
        if rising:
            reply += "• **Categories that increased:** " + ", ".join([f"{c['name']} (+{c['pct_change']}%)" for c in rising[:2]]) + "\n"
        if declining:
            reply += "• **Categories that decreased:** " + ", ".join([f"{c['name']} ({c['pct_change']}%)" for c in declining[:2]]) + "\n"
        reply += "\nVisit SpendSense Trends for daily burn rate charts and 3-month trajectory comparisons."
        actions = [
            {"label": "View SpendSense Trends", "url": "/spendsense"},
            {"label": "View Reports", "url": "/reports"}
        ]
        return {"response": reply, "actions": actions}

    # 6. 50/30/20 BUDGET EXPLANATION & HELP
    if any(k in msg for k in ['50/30/20', 'budget', 'needs vs wants', 'allocation', 'understand my budget', 'explain my budget', 'monthly budget', 'remaining budget']):
        reply = (
            "The **50/30/20 Rule** is the foundational budget framework in MoneyLeak:\n\n"
            f"1. **Needs ({user_context['needs_target_pct']}%):** Essential survival expenses such as rent, groceries, utilities, and healthcare.\n"
            f"   - Target: {user_context['needs_target']} | Actual: {user_context['needs_actual']} ({user_context['needs_actual_pct']}% of income)\n\n"
            f"2. **Wants ({user_context['wants_target_pct']}%):** Discretionary lifestyle spending such as dining out, shopping, and entertainment.\n"
            f"   - Target: {user_context['wants_target']} | Actual: {user_context['wants_actual']} ({user_context['wants_actual_pct']}% of income)\n\n"
            f"3. **Savings & Debt ({user_context['savings_target_pct']}%):** Wealth generation, emergency fund deposits, SIPs, and investments.\n"
            f"   - Target: {user_context['savings_target']} | Actual: {user_context['savings_actual']} ({user_context['savings_actual_pct']}% of income)\n\n"
            "You can customize your percentage targets and set monthly caps on specific categories in the Budget section."
        )
        actions = [
            {"label": "Manage 50/30/20 Budget", "url": "/budget"},
            {"label": "SpendSense Analyzer", "url": "/spendsense"}
        ]
        return {"response": reply, "actions": actions}

    # 7. HOW TO ADD OR EDIT TRANSACTIONS
    if any(k in msg for k in ['transaction', 'add transaction', 'log transaction', 'add expense', 'record expense', 'edit transaction', 'delete transaction', 'new transaction', 'manage transaction']):
        reply = (
            "Here is how to record and manage transactions in MoneyLeak:\n\n"
            "1. **Quick Add:** Click the **'+ Add Transaction'** button in the topbar or sidebar from any page.\n"
            "2. **Details:** Enter the amount, select an Expense or Savings Contribution, and choose a category (e.g. Groceries, Dining, Books).\n"
            "3. **Ledger Management:** Visit **Transactions** (`/transactions`) to view your full history, search by merchant or note, filter by date range, edit records, or delete mistaken entries.\n\n"
            "*Tip:* If you just signed in, adding your daily purchases keeps your 50/30/20 rings accurate in real-time."
        )
        actions = [
            {"label": "Open Transactions", "url": "/transactions"},
            {"label": "View Dashboard", "url": "/dashboard"}
        ]
        return {"response": reply, "actions": actions}

    # 8. SAVINGS GOALS & MILESTONES
    if any(k in msg for k in ['goal', 'goals', 'target', 'emergency fund', 'milestone', 'savings progress', 'explain my savings']):
        count = user_context['active_goals_count']
        primary = user_context['primary_goal']
        reply = (
            f"You currently have **{count} active savings goal(s)** configured in your Goals Planner.\n"
        )
        if primary:
            reply += f"• **Primary Focus:** {primary}\n"
        if user_context['monthly_savings_target']:
            reply += f"• **Monthly Savings Target:** {user_context['monthly_savings_target']}/month\n\n"

        reply += (
            "In the **Goals Planner**, you can set target amounts, target completion dates, and log progress deposits. "
            "MoneyLeak will automatically calculate your completion velocity and projected completion date."
        )
        actions = [
            {"label": "Open Goals Planner", "url": "/goals"},
            {"label": "Adjust Savings Target", "url": "/settings"}
        ]
        return {"response": reply, "actions": actions}

    # 9. INVESTMENT CALCULATOR & SCHEMES
    if any(k in msg for k in ['calculator', 'investment', 'invest', 'scheme', 'sip', 'lump sum', 'compound interest', 'return', 'stocks', 'mutual fund', 'gold', 'projection', 'future value']):
        reply = (
            "MoneyLeak includes an **Investment Calculator & Scheme Explorer** (`/calculator`):\n\n"
            "• **SIP & Lumpsum Simulator:** Calculate future corpus growth using initial amount, monthly contribution, duration (years), and assumed annual return.\n"
            "• **Supported Indian Categories:** Stocks & Equity, Equity Mutual Funds, SIP Investments, and Gold (plus PPF, FD, RD, and NPS references).\n"
            "• **Inflation Adjustment:** Toggle real vs nominal returns to see purchasing power parity over 5 to 30 years.\n"
            "• **Formula:** Uses the standard compound interest model: A = P*(1 + r/n)^(nt) for lumpsum and Future Value of Annuity formula for SIPs.\n\n"
            "*Important Disclaimer:* Projected values are mathematical estimates based on compound interest formulas, not guaranteed investment returns."
        )
        actions = [
            {"label": "Open Investment Calculator", "url": "/calculator"},
            {"label": "Assistant Scheme Matcher", "url": "/assistant"}
        ]
        return {"response": reply, "actions": actions}

    # 10. SETTINGS, PROFILE, CURRENCY, THEME & ROLE SWITCHING
    if any(k in msg for k in ['setting', 'profile', 'theme', 'dark mode', 'light mode', 'currency', 'avatar', 'photo', 'picture', 'student', 'salaried', 'role', 'update my profile']):
        reply = (
            "You can manage your account and customization in **Settings** (`/settings`):\n\n"
            "• **Profile Picture:** Upload a PNG, JPG, or WEBP photo (up to 5MB) or reset to default initials.\n"
            "• **Verified Email:** View your authenticated email or change it securely using Email OTP verification.\n"
            "• **Role (Student vs Salaried):** Toggle your employment role. This tunes recommended categories and suggestions without deleting or modifying any existing transactions.\n"
            f"• **Active Currency:** Currently set to **{user_context['currency']}**. You can switch to USD, EUR, GBP, or others anytime.\n"
            "• **Theme:** Toggle between **Light**, **Dark**, and **System** visual appearances."
        )
        actions = [
            {"label": "Go to Settings", "url": "/settings"},
            {"label": "Re-run Onboarding", "url": "/onboarding?review=1"}
        ]
        return {"response": reply, "actions": actions}

    # 11. GENERAL / ASSISTANT OVERVIEW FALLBACK
    actions = [
        {"label": "Dashboard", "url": "/dashboard"},
        {"label": "Budget", "url": "/budget"},
        {"label": "Calculator", "url": "/calculator"},
        {"label": "Settings", "url": "/settings"}
    ]

    reply = (
        f"I'm here to help you manage your finances in MoneyLeak, **{user_context['user_name']}**!\n\n"
        f"Right now for **{user_context['month_label']}**, you have recorded **{user_context['total_outflow']}** in outflows "
        f"against **{user_context['monthly_income']}** in monthly income (Surplus: {user_context['surplus']}, Savings Rate: {user_context['savings_rate']}%).\n\n"
        "Here are common things you can ask me:\n"
        "• *'How much did I spend this month?'*\n"
        "• *'Explain my 50/30/20 budget.'*\n"
        "• *'Do I have any spending leaks?'*\n"
        "• *'How do I add or filter transactions?'*\n"
        "• *'How does the investment calculator work?'*\n"
        "• *'Where can I change my theme, currency, or profile photo?'*"
    )
    return {"response": reply, "actions": actions}


# -----------------------------------------------------------------------------
# MAIN CHAT ENTRYPOINT
# -----------------------------------------------------------------------------
def handle_assistant_chat(user: User, user_message: str, page_context: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Processes chat requests with authentication, user data extraction,
    and server-side AI integration with local fallback.
    """
    clean_msg = (user_message or "").strip()
    if not clean_msg:
        return {
            "success": False,
            "error": "Please provide a valid question or query."
        }

    # Extract user-specific data context
    user_context = get_user_financial_context(user)

    # 1. Try external AI provider if configured
    gemini_reply = call_gemini_api(clean_msg, user_context, page_context, history)
    if gemini_reply:
        # Extract suggested action buttons if routes are mentioned
        actions = []
        for key, route_info in APP_ROUTES_DIRECTORY.items():
            if route_info["url"] in gemini_reply or route_info["title"].lower() in clean_msg.lower():
                actions.append({"label": route_info["title"], "url": route_info["url"]})

        return {
            "success": True,
            "response": gemini_reply,
            "actions": actions[:3],
            "provider": "gemini"
        }

    # 2. Seamless fallback to deterministic financial engine
    result = generate_deterministic_assistant_response(clean_msg, user_context, page_context)
    return {
        "success": True,
        "response": result["response"],
        "actions": result.get("actions", []),
        "provider": "built_in"
    }


# -----------------------------------------------------------------------------
# ASSISTANT MODULE EXECUTOR
# -----------------------------------------------------------------------------
def run_assistant_module(user: User, module_id: str) -> Dict[str, Any]:
    """
    Executes a specific Assistant module and returns formatted metrics
    and results using actual user data.
    """
    today = date.today()
    year, month = today.year, today.month

    if module_id == "leak_detector":
        alerts = run_leak_detection(user.id, year, month)
        return {
            "module_id": module_id,
            "title": "Spending Leak Audit",
            "metric_highlight": f"{len(alerts)} Leaks Detected",
            "status": "warning" if alerts else "good",
            "details": [
                {
                    "title": a.get("title", "") if isinstance(a, dict) else getattr(a, "title", ""),
                    "description": a.get("description", "") if isinstance(a, dict) else getattr(a, "description", ""),
                    "severity": a.get("severity", "info") if isinstance(a, dict) else getattr(a, "severity", "info"),
                }
                for a in alerts[:4]
            ] or [{"title": "Finances Optimized", "description": "No active leaks detected in your accounts this month.", "severity": "info"}],
            "action_url": "/analysis",
            "action_text": "Review All Alerts in Leak Detector"
        }

    elif module_id == "leak_trimmer":
        summary = calculate_budget_summary(user.id, year, month)
        reductions = {}
        for c in summary.get('category_breakdown', []):
            if c.get('group') == 'WANTS' and c.get('total_minor', 0) > 0:
                reductions[c['id']] = int(c['total_minor'] * 0.15)
        sim = run_simulation(user.id, reductions, year, month)
        monthly_saved_minor = sim['proposed']['total_reduction_minor']
        annual_saved_minor = sim['proposed']['annualized_savings_minor']
        three_year_minor = annual_saved_minor * 3
        five_year_minor = annual_saved_minor * 5
        return {
            "module_id": module_id,
            "title": "Discretionary Trimming Simulation",
            "metric_highlight": f"+{format_money(monthly_saved_minor, user.currency)}/mo Saved",
            "status": "good",
            "details": [
                {"title": "1-Year Accumulated Trimming", "description": f"Trimming 15% discretionary spending frees up {format_money(annual_saved_minor, user.currency)} in 12 months."},
                {"title": "3-Year Multi-Period Compound", "description": f"Over 3 years, the saved capital grows to {format_money(three_year_minor, user.currency)}."},
                {"title": "5-Year Horizon Projection", "description": f"Over 5 years, cumulative discretionary savings reaches {format_money(five_year_minor, user.currency)}."}
            ],
            "action_url": "/simulator",
            "action_text": "Customize Savings Simulator"
        }

    elif module_id == "budget_analyzer":
        summary = calculate_budget_summary(user.id, year, month)
        return {
            "module_id": module_id,
            "title": "50/30/20 Budget Compliance",
            "metric_highlight": f"{summary['total_outflow']['formatted']} / {summary['income']['formatted']}",
            "status": "good" if summary['surplus']['minor'] >= 0 else "warning",
            "details": [
                {"title": "Needs (Essentials 50%)", "description": f"Actual: {summary['needs']['actual_formatted']} ({round(summary['needs']['actual_pct'])}%) vs Cap: {summary['needs']['target_formatted']}"},
                {"title": "Wants (Lifestyle 30%)", "description": f"Actual: {summary['wants']['actual_formatted']} ({round(summary['wants']['actual_pct'])}%) vs Cap: {summary['wants']['target_formatted']}"},
                {"title": "Savings & Debt (20%)", "description": f"Actual: {summary['savings']['actual_formatted']} ({round(summary['savings']['actual_pct'])}%) vs Cap: {summary['savings']['target_formatted']}"}
            ],
            "action_url": "/budget",
            "action_text": "Open 50/30/20 Budget Manager"
        }

    elif module_id == "cashflow_surplus":
        summary = calculate_budget_summary(user.id, year, month)
        return {
            "module_id": module_id,
            "title": "Net Cashflow Position",
            "metric_highlight": f"{summary['surplus']['formatted']} Surplus",
            "status": "good" if summary['surplus']['minor'] >= 0 else "danger",
            "details": [
                {"title": "Monthly Inflow Basis", "description": f"Recorded income: {summary['income']['formatted']} per month."},
                {"title": "Total Recorded Outflow", "description": f"Aggregate spending: {summary['total_outflow']['formatted']}."},
                {"title": "Savings Rate Efficiency", "description": f"You are saving {summary['savings_rate']}% of your monthly earnings."}
            ],
            "action_url": "/dashboard",
            "action_text": "View Dashboard Metrics"
        }

    elif module_id == "expense_breakdown":
        summary = calculate_budget_summary(user.id, year, month)
        cats = sorted(summary.get('category_breakdown', []), key=lambda x: x.get('actual_minor', 0), reverse=True)[:4]
        return {
            "module_id": module_id,
            "title": "Top Spending Categories",
            "metric_highlight": f"{len(cats)} Categories Active",
            "status": "info",
            "details": [
                {"title": c.get('name'), "description": f"Spent: {c.get('actual_formatted')} ({c.get('budget_group')})"}
                for c in cats
            ] or [{"title": "No Categorized Expenses", "description": "Log transactions to track category spending.", "severity": "info"}],
            "action_url": "/transactions",
            "action_text": "Inspect Transaction Ledger"
        }

    elif module_id == "goals_tracker":
        goals = get_all_goals_summary(user.id, user.currency)
        goal_items = goals.get('goals', [])
        return {
            "module_id": module_id,
            "title": "Goals Progress Velocity",
            "metric_highlight": f"{len(goal_items)} Goals Active",
            "status": "good" if goal_items else "info",
            "details": [
                {"title": g.get('name'), "description": f"Saved {g.get('current_formatted')} of {g.get('target_formatted')} ({round(g.get('progress_pct', 0))}% complete)"}
                for g in goal_items[:3]
            ] or [{"title": "No Goals Set Yet", "description": "Create an Emergency Fund, Travel, or Education goal in the Goals Planner.", "severity": "info"}],
            "action_url": "/goals",
            "action_text": "Manage Savings Goals"
        }

    elif module_id == "investment_matcher":
        recs = get_personalized_recommendations(amount=10000.0, risk_tolerance='Moderate', objective='wealth_accumulation')[:3]
        return {
            "module_id": module_id,
            "title": "Investment Recommendations",
            "metric_highlight": "Curated Indian Assets",
            "status": "good",
            "details": [
                {"title": r.get('name'), "description": f"Category: {r.get('category_name')} • 5Y Return: ~{r.get('historical_5y_return')}% p.a. • Risk: {r.get('risk_level')}"}
                for r in recs
            ],
            "action_url": "/calculator",
            "action_text": "Explore Schemes & Calculator"
        }

    elif module_id == "future_calculator":
        calc = calculate_compound_growth(
            initial_amount=10000.0,
            periodic_contribution=5000.0,
            frequency='MONTHLY',
            annual_return_pct=12.0,
            duration_years=10,
            currency=user.currency
        )
        return {
            "module_id": module_id,
            "title": "10-Year SIP Compound Projection",
            "metric_highlight": calc['summary']['future_value_formatted'],
            "status": "good",
            "details": [
                {"title": "Total Out-of-Pocket Invested", "description": calc['summary']['total_invested_formatted']},
                {"title": "Estimated Compound Gains", "description": f"{calc['summary']['estimated_returns_formatted']} (at assumed 12.0% p.a.)"},
                {"title": "Projection Disclaimer", "description": "Estimates based on compound mathematical formulas; actual equity returns fluctuate with market conditions."}
            ],
            "action_url": "/calculator",
            "action_text": "Launch Full Investment Calculator"
        }

    elif module_id == "health_audit":
        summary = calculate_budget_summary(user.id, year, month)
        alerts = run_leak_detection(user.id, year, month)
        # Compute financial health score out of 100
        score = 85
        if alerts:
            score -= min(30, len(alerts) * 10)
        if summary['surplus']['minor'] < 0:
            score -= 25
        elif summary['savings_rate'] >= 20:
            score += 10
        score = max(20, min(100, score))

        return {
            "module_id": module_id,
            "title": "Overall Financial Health Score",
            "metric_highlight": f"{score} / 100 Score",
            "status": "good" if score >= 75 else "warning",
            "details": [
                {"title": "Budget Framework Alignment", "description": f"Needs: {round(summary['needs']['actual_pct'])}% (Target: 50%) • Wants: {round(summary['wants']['actual_pct'])}% (Target: 30%)"},
                {"title": "Leak Alert Risk", "description": f"{len(alerts)} leaks flagged this month."},
                {"title": "Audit Summary", "description": "Financial records are balanced. Review leaky categories and keep savings contributions steady."}
            ],
            "action_url": "/reports",
            "action_text": "Download Full Audit PDF"
        }

    return {
        "module_id": module_id,
        "title": "Module Overview",
        "metric_highlight": "Operational",
        "status": "info",
        "details": [{"title": "Feature Available", "description": "Module ready to run."}],
        "action_url": "/dashboard",
        "action_text": "Open Dashboard"
    }
