import os
from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from config import config_by_name
from app.extensions import db, migrate, csrf
from app.routes import register_blueprints
from app.services.money import format_money, from_minor_units, get_currency_symbol, get_currency_decimals


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Jinja filters and context processors
    @app.template_filter('format_money')
    def format_money_filter(minor_units, currency='INR', include_symbol=True):
        return format_money(minor_units, currency, include_symbol=include_symbol)

    @app.template_filter('to_major')
    def to_major_filter(minor_units, currency='INR'):
        return from_minor_units(minor_units, currency)

    @app.template_filter('currency_symbol')
    def currency_symbol_filter(currency='INR'):
        return get_currency_symbol(currency)

    @app.template_filter('currency_decimals')
    def currency_decimals_filter(currency='INR'):
        return get_currency_decimals(currency)

    @app.context_processor
    def inject_context_helpers():
        return dict(
            csrf_token=generate_csrf,
            get_currency_symbol=get_currency_symbol,
            get_currency_decimals=get_currency_decimals
        )

    # CSRF error handler for clean AJAX / API responses
    @app.errorhandler(400)
    def handle_bad_request(e):
        if 'CSRF' in str(e):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'CSRF token missing or invalid.'}), 400
        return e

    # Ensure avatar upload folder exists
    try:
        os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'avatars'), exist_ok=True)
    except OSError:
        pass

    # Import models for db.create_all()
    from app.models.auth_otp import EmailOTP  # noqa: F401
    from app.models.trip import Trip  # noqa: F401
    from app.models.sync import (  # noqa: F401
        FinancialConnection,
        SyncedTransaction,
        MerchantCategoryPreference,
        SyncAuditLog,
        ReceiptRecord
    )

    # Create tables automatically for local & production setup
    with app.app_context():
        db.create_all()
        try:
            if db.engine.dialect.name == 'sqlite':
                with db.engine.connect() as conn:
                    # Check categories table
                    res = conn.execute(db.text("PRAGMA table_info(categories)")).fetchall()
                existing_cols = {row[1] for row in res}
                cols_to_add = [
                    ('transaction_type', "VARCHAR(30) DEFAULT 'EXPENSE' NOT NULL"),
                    ('is_pinned', "BOOLEAN DEFAULT 0 NOT NULL"),
                    ('display_order', "INTEGER DEFAULT 0 NOT NULL"),
                    ('is_default', "BOOLEAN DEFAULT 0 NOT NULL"),
                    ('is_archived', "BOOLEAN DEFAULT 0 NOT NULL"),
                    ('last_used_at', "DATETIME")
                ]
                for col_name, col_def in cols_to_add:
                    if col_name not in existing_cols:
                        conn.execute(db.text(f"ALTER TABLE categories ADD COLUMN {col_name} {col_def}"))

                # Check transactions table columns
                res_t = conn.execute(db.text("PRAGMA table_info(transactions)")).fetchall()
                txn_cols = {row[1] for row in res_t}
                if 'trip_id' not in txn_cols:
                    conn.execute(db.text("ALTER TABLE transactions ADD COLUMN trip_id INTEGER"))

                # Check users table columns
                res_u = conn.execute(db.text("PRAGMA table_info(users)")).fetchall()
                user_cols = {row[1] for row in res_u}
                user_cols_to_add = [
                    ('theme_preference', "VARCHAR(20) DEFAULT 'system' NOT NULL"),
                    ('auth_provider', "VARCHAR(50) DEFAULT 'local' NOT NULL"),
                    ('provider_user_id', "VARCHAR(255)"),
                    ('profile_picture_url', "VARCHAR(500)"),
                    ('email_verified', "BOOLEAN DEFAULT 0 NOT NULL"),
                    ('phone_number', "VARCHAR(30)"),
                    ('date_of_birth', "VARCHAR(30)"),
                    ('country', "VARCHAR(80) DEFAULT 'India' NOT NULL"),
                    ('state_id', "VARCHAR(20)"),
                    ('state_name', "VARCHAR(100)"),
                    ('district_id', "VARCHAR(50)"),
                    ('district_name', "VARCHAR(100)"),
                    ('city_id', "VARCHAR(80)"),
                    ('city_name', "VARCHAR(120)"),
                    ('is_custom_city', "BOOLEAN DEFAULT 0 NOT NULL"),
                    ('pincode', "VARCHAR(10)"),
                    ('location_tier', "VARCHAR(50) DEFAULT 'UNCLASSIFIED' NOT NULL"),
                    ('budget_preset', "VARCHAR(50) DEFAULT 'standard' NOT NULL"),
                    ('rent_or_emi_minor_units', "BIGINT DEFAULT 0 NOT NULL"),
                    ('essential_expenses_minor_units', "BIGINT DEFAULT 0 NOT NULL"),
                    ('debt_payments_minor_units', "BIGINT DEFAULT 0 NOT NULL"),
                    ('dependants_count', "INTEGER DEFAULT 0 NOT NULL"),
                    ('preferred_language', "VARCHAR(20) DEFAULT 'en' NOT NULL"),
                    ('user_type', "VARCHAR(30)"),
                    ('opening_balance_minor_units', "BIGINT DEFAULT 0 NOT NULL"),
                    ('monthly_savings_target_minor_units', "BIGINT DEFAULT 0 NOT NULL"),
                    ('primary_financial_goal', "VARCHAR(100)"),
                    ('investment_experience', "VARCHAR(50)"),
                    ('preferred_investment_categories', "TEXT"),
                    ('onboarding_step', "INTEGER DEFAULT 1 NOT NULL")
                ]
                for col_name, col_def in user_cols_to_add:
                    if col_name not in user_cols:
                        conn.execute(db.text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))

                conn.commit()
        except Exception:
            pass

    return app
