# 🚀 Hosting MoneyLeak on Render (Step-by-Step Guide)

This guide walks you through deploying **MoneyLeak** to **[Render](https://render.com/)** in under 5 minutes with automatic HTTPS, continuous deployment from GitHub, and automated table creation.

---

## 📋 Prerequisites

1. A **[GitHub](https://github.com/)** account.
2. A **[Render](https://render.com/)** account (free tier available, no credit card required).
3. Your MoneyLeak code pushed to a GitHub repository (public or private).

---

## ⚡ Option 1: 1-Click Blueprint Deployment (Recommended)

Because this repository includes a [`render.yaml`](file:///c:/Users/shail/OneDrive/Documents/MoneyLeak/render.yaml) file, Render can configure everything automatically:

1. Log in to **[dashboard.render.com](https://dashboard.render.com/)**.
2. Click **New +** in the top navigation bar and select **Blueprint**.
3. Connect your GitHub repository (`MoneyLeak`).
4. Render will detect `render.yaml` and configure:
   - **Service Name**: `moneyleak`
   - **Environment**: `Python`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Environment Variables**: Automatic secure secret key generation, production flags, and sandbox AA configs.
5. Click **Apply**.
6. Wait 2–3 minutes for the build to finish. Once done, your app will be live at `https://moneyleak-xxxx.onrender.com`!

---

## 🛠️ Option 2: Manual Web Service Setup (Dashboard)

If you prefer creating the Web Service manually from the Render dashboard:

### Step 1: Create Web Service
1. In the Render Dashboard, click **New +** → **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Choose your `MoneyLeak` repository.

### Step 2: Configure Service Details
Fill in the following fields:
* **Name**: `moneyleak` (or any unique name you prefer)
* **Region**: Choose the closest region (e.g. `Singapore` or `Oregon`)
* **Branch**: `main` (or `master`)
* **Root Directory**: Leave blank
* **Runtime**: `Python 3`
* **Build Command**:
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
* **Start Command**:
  ```bash
  gunicorn run:app
  ```
* **Instance Type**: `Free`

### Step 3: Configure Environment Variables
Scroll down to the **Environment Variables** section and add:

| Key | Recommended Value | Note |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Enables production security & caching |
| `SECRET_KEY` | *(Click "Generate" or enter a random 32-char string)* | Session encryption key |
| `SESSION_COOKIE_SECURE` | `true` | Enforces HTTPS session cookies |
| `PYTHON_VERSION` | `3.11.9` | Matches tested runtime |
| `AA_ENVIRONMENT` | `sandbox` | Or `production` if you have Setu API keys |

*(Optional for Account Aggregator production mode: add `SETU_AA_CLIENT_ID`, `SETU_AA_CLIENT_SECRET`, and `SETU_AA_PRODUCT_INSTANCE_ID`).*

### Step 4: Click "Create Web Service"
Render will automatically clone the repository, install dependencies, compile assets, and launch Gunicorn.

---

## 🗄️ Database Configuration Options

### Option A: SQLite (Default — Zero Setup)
* **Status**: Works out of the box immediately.
* On first launch, Flask automatically creates `moneyleak.db` and all database tables via `db.create_all()`.
* *Note on Render Free Tier*: Filesystem changes on free-tier containers are ephemeral when the container restarts (e.g., during a new deploy or after 15 minutes of inactivity).

### Option B: Render Managed PostgreSQL (Persistent & Production-Grade)
For permanent database storage:
1. In the Render Dashboard, click **New +** → **PostgreSQL**.
2. Name it `moneyleak-db`, select `Free` plan, and click **Create Database**.
3. Once created, copy the **Internal Database URL** (e.g., `postgres://user:pass@host/moneyleak_db`).
4. Go to your `moneyleak` Web Service → **Environment** tab.
5. Add/Update:
   - **Key**: `DATABASE_URL`
   - **Value**: *(Paste the Internal Database URL)*
6. MoneyLeak's [`config.py`](file:///c:/Users/shail/OneDrive/Documents/MoneyLeak/config.py) automatically converts `postgres://` to `postgresql://` and creates all tables on startup.

---

## 🧪 Seeding Initial Demo Data (Optional)

If you would like to pre-seed the demo account (`demo@moneyleak.app` / `demo1234`) on your Render deployment:

1. Open your deployed Web Service on Render.
2. Click the **Shell** tab in the left sidebar to open a terminal inside your container.
3. Run:
   ```bash
   python -m app.services.seed_demo
   ```
4. You will see:
   ```text
   Demo user Tanu Sharma (demo@moneyleak.app) initialized with ₹40,000 monthly income and live leak scenarios.
   ```
5. You can now log in at your Render URL with:
   - **Email**: `demo@moneyleak.app`
   - **Password**: `demo1234`

---

## 🔒 Security Best Practices on Render

1. **Free Automated SSL**: Render automatically generates and renews Let's Encrypt SSL certificates for your `*.onrender.com` domain and any custom domains.
2. **CSRF Protection**: All POST endpoints are strictly protected by Flask-WTF CSRF tokens.
3. **HTTP-Only Cookies**: Session cookies are configured with `HttpOnly` and `SameSite=Lax`.
4. **Environment Isolation**: Never commit `.env` or production credentials to GitHub. Render stores environment variables encrypted at rest.
