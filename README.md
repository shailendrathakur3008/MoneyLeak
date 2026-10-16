# MoneyLeak 💸

### Personal Finance Analytics, Budget Intelligence & Savings Optimization Platform

MoneyLeak is a full-stack personal finance web application built for students, salaried professionals, and young earners. It replaces guesswork with **explainable financial analytics**, enforces a customizable **50/30/20 budget distribution framework**, detects recurring subscription drains and lifestyle inflation, simulates non-destructive savings scenarios, and generates exportable monthly audit reports (CSV and PDF).

---

## 🎨 UI/UX Design System (Extracted from Reference Aesthetic)

The visual direction follows a modern fintech and habit-tracking design language:

* **Canvas & Surfaces**: Serene off-white canvas (`#f4f6f2`) paired with clean white cards and deep carbon cards (`#161917`).
* **Vibrant Accent**: Electric lime / chartreuse (`#cbf432`) for active states, savings progress, and interactive focal points.
* **Hero 50/30/20 Macro Card**: High-contrast dark card featuring **3 concentric SVG macro rings** (Needs 50%, Wants 30%, Savings 20%) alongside total monthly outflow gauges.
* **Pastel Quick-Stat KPI Cards**: Soft peach (`#fff4ec`) for active leak alerts, soft mint (`#ebf8ed`) for surplus & savings rates, and soft ice-blue (`#edf5fe`) for committed subscriptions.
* **Motivational Banner**: Bright chartreuse gradient (`linear-gradient(135deg, #d4f938 0%, #b8f020 100%)`) with one-click navigation to the Savings Simulator.
* **Donut & Progress Visualizations**: Segmented Chart.js donut breakdown with central outflow metrics and smooth curved trend charts.
* **Mobile-First Responsive Dock**: Bottom floating navigation dock with a prominent circular quick-add button for immediate logging on mobile devices, transforming into a sleek sidebar on desktop screens.

---

## 🏛️ System Architecture

```text
MoneyLeak/
├── app/
│   ├── __init__.py                # Flask app factory, CSRF handlers, Jinja money filters
│   ├── extensions.py              # SQLAlchemy, Migrate, CSRFProtect
│   ├── models/                    # Normalized Relational Data Models
│   │   ├── user.py                # User credentials, currency, monthly baseline
│   │   ├── category.py            # Needs, Wants, Savings groups + caps
│   │   ├── income.py              # Recognized income in integer minor units
│   │   ├── transaction.py         # Outflow transactions with strict accounting types
│   │   ├── budget.py              # User-customizable 50/30/20 percentages
│   │   ├── goal.py                # Savings goals & separate contributions ledger
│   │   ├── recurring_payment.py   # Subscriptions, billing frequencies, annual costs
│   │   ├── alert.py               # Deterministic leak detection alerts
│   │   └── simulation.py          # What-if scenario savings records
│   ├── routes/                    # Modular Flask Blueprints (View + REST APIs)
│   │   ├── auth.py                # Register, login, onboarding, session security
│   │   ├── dashboard.py           # Real-time summaries, trend APIs
│   │   ├── transactions.py        # Transaction CRUD, search, filter, pagination
│   │   ├── income.py              # Income CRUD
│   │   ├── categories.py          # Category management & monthly caps
│   │   ├── budget.py              # 50/30/20 calibration & reset
│   │   ├── analysis.py            # MoneyLeak detection & recurring bills
│   │   ├── simulations.py         # What-if calculation engine
│   │   ├── goals.py               # Milestones & synchronized savings contributions
│   │   ├── reports.py             # CSV export & ReportLab PDF download
│   │   ├── settings.py            # Profile, password, currency, account deletion
│   │   └── tools.py               # Investment compound interest calculator
│   ├── services/                  # Authoritative Financial Services
│   │   ├── money.py               # Integer minor units math & multi-currency formatting
│   │   ├── budget_engine.py       # Central 50/30/20 calculation source of truth
│   │   ├── leak_detection.py      # Rules 1-8 explainable leak detector
│   │   ├── simulation_engine.py   # Non-destructive what-if scenario calculator
│   │   ├── goal_engine.py         # Milestone pace & required monthly contributions
│   │   ├── investment_calculator.py# SIP compound interest math & risk disclosures
│   │   ├── report_service.py      # CSV buffers & ReportLab PDF generator
│   │   └── seed_demo.py           # Demo account populator (Tanu Sharma)
│   ├── static/                    # Custom CSS & Vanilla JavaScript
│   └── templates/                 # Jinja2 HTML5 semantic templates
├── config.py                      # Development, Testing, Production configurations
├── requirements.txt               # Locked dependencies
├── run.py                         # Application launcher
└── tests/                         # Pytest test suite (100% passing)
```

---

## 📐 Financial Correctness & Accounting Rules

1. **Integer Minor Units**: Monetary values are stored authoritatively as integer minor units (paise for INR, cents for USD, yen for JPY). Floating-point values are never used for database storage or balance equations.
2. **Unified Calculation Engine**: `app.services.budget_engine` is the single source of truth. The dashboard, reports, alerts, and simulator invoke the exact same calculation pipeline.
3. **Accounting Types**:
   - `EXPENSE`: Consumption outflow categorized under Needs, Wants, or Savings.
   - `REFUND`: Reimburses outflow and offsets consumption in the matching category.
   - `SAVINGS_CONTRIBUTION`: Transfer to investments or emergency cushions. Recognized as realized savings, **never as a consumption expense**.
   - `DEBT_REPAYMENT`: Minimum contractual EMIs count in Needs; additional debt prepayments count toward Savings.
   - `TRANSFER`: Neutral movement between own accounts (zero impact on surplus).
4. **50/30/20 Formulas**:
   - $\text{Needs Target} = \text{Recognized Income} \times (\text{Needs } \% / 100)$
   - $\text{Wants Target} = \text{Recognized Income} \times (\text{Wants } \% / 100)$
   - $\text{Savings Target} = \text{Recognized Income} \times (\text{Savings } \% / 100)$
   - $\text{Monthly Surplus} = \text{Recognized Income} - (\text{Consumption Outflow} + \text{Savings Contributions})$
   - $\text{Savings Rate} = (\text{Actual Savings} / \text{Recognized Income}) \times 100$

---

## 🔍 MoneyLeak Detection Engine (Rules 1 – 8)

* **Rule 1 (Budget Overrun)**: Flags when actual discretionary Wants spending exceeds target caps, providing the exact excess amount and top category contributors.
* **Rule 2 (MoM Spending Surge)**: Compares current month with previous month to detect surges $>25\%$ against established spending baselines.
* **Rule 3 (Subscription Drain)**: Normalizes weekly, monthly, and annual commitments (Netflix, Spotify, Gym) to highlight annualized drain.
* **Rule 4 (Unusual Spending Outliers)**: Transparent statistical threshold flagging individual transactions $>2.5\times$ the historical category average.
* **Rule 5 (Savings Gap)**: Identifies shortfalls between realized savings and the user's calibrated savings target.
* **Rule 6 (Potential Savings Scenario)**: Suggests a 15–20% discretionary trim to retain cashflow and compound wealth.
* **Rule 7 (Lifestyle Inflation)**: Detects when discretionary spending expansion significantly outpaces income growth across consecutive periods.
* **Rule 8 (Explainable Alert Lifecycle)**: Every alert includes supporting financial evidence, severity tags (`INFO`, `WARNING`, `DANGER`), actionable tips, and dismissal functionality without database alert spamming.

---

## ⚡ Universal Expense Sync (Account Aggregator & Bank Feeds)

MoneyLeak provides **Universal Expense Sync**, a secure automatic transaction-tracking system compliant with India's **Account Aggregator (AA)** ecosystem (RBI NBFC-AA framework regulated via Sahamati standards / Setu AA):

* **Multi-App UPI & Card Ingestion**: Captures transactions across Google Pay, PhonePe, Paytm, BHIM, Debit/Credit Cards, and Net Banking by normalizing underlying bank account narrations.
* **Deterministic Merchant Normalization**: Classifies merchants across Food & Dining (Swiggy, Zomato), Groceries (Blinkit, Zepto, BigBasket), Shopping (Amazon, Flipkart, Myntra), Commute (Uber, Ola, Rapido), Utilities, and Subscriptions.
* **Intelligent Accounting**:
  - `REFUND`: Automatically linked to original spending to offset category consumption.
  - `TRANSFER`: Self-account transfers and credit card bill payments (CRED, Cheq) are recognized as liability settlements, preventing double-counting.
  - `SAVINGS_CONTRIBUTION`: Mutual fund SIPs (Zerodha, Groww) are credited to savings, never inflated as consumption expenses.
* **Robust Deduplication**: Prevents duplicate records across bank feeds and manual entries using external UTR/RRN hashing, exact coordinates, and $\pm 2$ day fuzzy window detection.
* **Review Queue & User Preference Memory**: Low-confidence transactions and potential duplicates are staged in a dedicated review queue. Category adjustments are remembered for future syncs.
* **Multi-Bank Statement Fallback**: High-fidelity CSV statement parser supporting HDFC Bank, SBI, ICICI Bank, Axis Bank, and Generic CSV formats with full preview and validation.
* **Smart Digital Receipt Matcher**: Extracts order metadata from Swiggy, Zomato, Amazon, Blinkit, Zepto, and Uber receipts to enrich bank debits without fabricating line items.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.11+
* pip

### 1. Clone & Enter Project
```bash
cd MoneyLeak
```

### 2. Create & Activate Virtual Environment (Optional)
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file (or use `.env.example` defaults):
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secure-random-secret-key
DATABASE_URL=sqlite:///instance/moneyleak.db
```

### 5. Seed Demo Data (Optional but Recommended)
Populate a pre-configured account with ₹40,000 salary, 50/30/20 data, subscriptions, goals, and triggered leak alerts:
```bash
python -m app.services.seed_demo
```
* **Demo Email**: `demo@moneyleak.app`
* **Demo Password**: `demo1234`

### 6. Run the Application
```bash
python run.py
```
Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Automated Testing

MoneyLeak includes a comprehensive automated test suite testing financial correctness, multi-currency conversions, transaction CRUD, 50/30/20 math, savings simulations, and multi-tenant security isolation.

Run tests:
```bash
python -m pytest -v
```

All 11 automated test suites execute and pass:
* `test_unauthenticated_access_rejected`: Verifies route & API protection.
* `test_user_data_isolation`: Confirms User A cannot read or delete User B's records.
* `test_standard_50_30_20_targets`: Verifies ₹20,000 Needs, ₹12,000 Wants, ₹8,000 Savings targets for ₹40,000 income.
* `test_budget_actuals_and_refunds`: Verifies refund deductions and savings rate math.
* `test_zero_income_safe_handling`: Verifies zero-division safety.
* `test_goal_metrics_and_monthly_required`: Confirms goal pace calculations.
* `test_minor_unit_conversions`: Tests integer minor unit conversions across currencies.
* `test_money_formatting`: Validates Indian numbering system (`₹1,00,000.00`) and standard decimal formats.
* `test_savings_simulator_calculation`: Validates ₹3,000 expense trim resulting in ₹8,000 surplus and ₹36,000 annualized savings without mutating live transactions.
* `test_transaction_crud_api`: Tests create, read, update, delete operations.
* `test_transaction_validation_errors`: Validates negative amounts and invalid types rejection.

---

## 🔐 Security & Privacy Practices

* **Password Hashing**: Salted hashing with Werkzeug (`scrypt` / `pbkdf2`).
* **CSRF Protection**: All state-changing endpoints (POST, PUT, PATCH, DELETE) validate CSRF tokens via `Flask-WTF` and `X-CSRFToken` headers.
* **Tenant Isolation**: Every database query verifies `user_id = g.current_user.id`. No client can modify another user's transactions by spoofing IDs.
* **Rate Limiting**: Failed login attempt tracking prevents brute-force credential stuffing.
* **Data Sanitization**: HTML escaping and SQLAlchemy parameterized queries prevent SQL injection and XSS.
* **Permanent Account Erasure**: The Danger Zone in Settings allows users to permanently delete their account and all associated financial records.

---

## 🚢 Production Deployment

For production environments:

1. **Set Environment Variables**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY="long-random-production-secret"
   export DATABASE_URL="postgresql://user:password@localhost:5432/moneyleak"
   export SESSION_COOKIE_SECURE=True
   ```
2. **Run Migrations**:
   ```bash
   flask db upgrade
   ```
3. **Launch Production WSGI Server (Gunicorn)**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

### Backup and Recovery
* **Database Backup (SQLite)**:
  ```bash
  cp instance/moneyleak.db backups/moneyleak_$(date +%Y%m%d_%H%M%S).db
  ```
* **Database Backup (PostgreSQL)**:
  ```bash
  pg_dump -U username moneyleak > backups/moneyleak_$(date +%Y%m%d_%H%M%S).sql
  ```
