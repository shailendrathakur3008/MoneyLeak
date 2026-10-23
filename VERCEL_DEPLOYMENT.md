# ⚡ Deploying MoneyLeak to Vercel (Step-by-Step Guide)

This guide walks you through deploying **MoneyLeak** to **[Vercel](https://vercel.com/)** as a serverless Python web application with instant global CDN, automatic HTTPS, and zero server maintenance.

---

## 🏗️ Architecture on Vercel

* **Entrypoint**: [`api/index.py`](file:///c:/Users/shail/OneDrive/Documents/MoneyLeak/api/index.py) (Vercel Serverless Function exporting Flask `app`).
* **Routing**: [`vercel.json`](file:///c:/Users/shail/OneDrive/Documents/MoneyLeak/vercel.json) rewrites all incoming traffic `/(.*)` to the serverless function.
* **Database**:
  * **Default (Sandbox / Demo)**: In-memory/temporary SQLite at `/tmp/moneyleak.db` (created automatically).
  * **Production (Permanent Data)**: Connects to any cloud PostgreSQL database via the `DATABASE_URL` environment variable (e.g. **Vercel Postgres**, **Neon**, or **Supabase**).

---

## 🚀 Quick Deployment in 3 Steps

### Step 1: Push your code to GitHub
Run the following in your local terminal:
```bash
git add .
git commit -m "Configure Vercel serverless deployment"
git push origin main
```

---

### Step 2: Import into Vercel

1. Log in to **[vercel.com](https://vercel.com/)** and navigate to your Dashboard.
2. Click **Add New...** (top right) → **Project**.
3. Locate your **`MoneyLeak`** repository and click **Import**.
4. In the **Configure Project** screen:
   * **Project Name**: `moneyleak` (or your preferred name)
   * **Framework Preset**: Select **`Other`**
   * **Root Directory**: Leave as `./` (default)
   * **Build and Output Settings**: Leave defaults (Vercel uses `vercel.json`)
5. Expand **Environment Variables** and add:

| Key | Value | Purpose |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Production mode |
| `SECRET_KEY` | *(Enter a random 32-character string)* | Session encryption key |
| `SESSION_COOKIE_SECURE` | `true` | Secure HTTPS cookies |
| `AA_ENVIRONMENT` | `sandbox` | Universal Sync test mode |
| `RESEND_API_KEY` | *(Optional, e.g. `re_...`)* | **Real Email Delivery** via Resend (3,000 free emails/mo) |
| `SMTP_USER` | *(Optional, e.g. `yourname@gmail.com`)* | Direct SMTP username |
| `SMTP_PASS` | *(Optional, Google App Password)* | 16-character Google App Password |
| `SHOW_DEV_OTP` | `true` | Instant access code on screen when email unconfigured |

### ✉️ Setting Up Real Email OTP Delivery on Vercel

To ensure users receive OTP verification emails directly in their inbox:

#### Option 1: Resend (Recommended for Vercel — 100% Free, 3,000 emails/mo)
1. Sign up for free at **[resend.com](https://resend.com/)**.
2. Create an API Key in your Resend Dashboard.
3. In your Vercel Project Settings → **Environment Variables**, add:
   - **Key**: `RESEND_API_KEY`
   - **Value**: `re_your_api_key_here`
4. Redeploy. Resend delivers emails directly via HTTP REST API with zero SMTP timeout or firewall issues!

#### Option 2: Gmail SMTP (Using Google App Password)
1. Go to **[Google Account Security](https://myaccount.google.com/security)** and ensure 2-Step Verification is ON.
2. Go to **[App Passwords](https://myaccount.google.com/apppasswords)**.
3. Generate a 16-character password (e.g., `abcd efgh ijkl mnop`).
4. In your Vercel Project Settings → **Environment Variables**, add:
   - `SMTP_HOST`: `smtp.gmail.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USER`: `your_email@gmail.com`
   - `SMTP_PASS`: `your 16-character app password`

6. Click **Deploy**.

Vercel will install dependencies, compile the serverless function, and give you your live URL (e.g. `https://moneyleak.vercel.app`) in ~60 seconds!

---

## 🗄️ Setting Up Persistent Database (Vercel Postgres / Neon / Supabase)

Because Vercel runs on stateless serverless functions, the local container filesystem outside `/tmp` is read-only and ephemeral. For permanent database persistence:

### Option 1: Vercel Postgres (Built-in)
1. On your Vercel project page, click the **Storage** tab.
2. Click **Create Database** → **Postgres**.
3. Select the free tier and click **Create**.
4. Once created, click **Connect to Project** and choose `moneyleak`.
5. Vercel will automatically inject `DATABASE_URL` into your project's Environment Variables.
6. Trigger a redeploy. MoneyLeak's [`config.py`](file:///c:/Users/shail/OneDrive/Documents/MoneyLeak/config.py) automatically connects to Postgres and auto-creates all tables!

### Option 2: Neon (Free Serverless PostgreSQL)
1. Sign up at **[neon.tech](https://neon.tech/)** (generous free tier).
2. Create a project and copy your connection string (e.g. `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`).
3. In your Vercel Project Settings → **Environment Variables**, add:
   * **Key**: `DATABASE_URL`
   * **Value**: *(Your Neon connection string)*
4. Redeploy.

---

## 🧪 Seeding Initial Demo Account

If using a remote database (Vercel Postgres / Neon), you can seed demo data locally by temporarily pointing `DATABASE_URL` in your local `.env` to the remote database URL, and running:
```bash
python -m app.services.seed_demo
```
This populates the demo account (`demo@moneyleak.app` / `demo1234`) with full 50/30/20 data, subscriptions, and leak alerts.
