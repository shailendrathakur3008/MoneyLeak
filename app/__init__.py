import os
from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import generate_csrf
from config import config_by_name
from app.extensions import db, migrate, csrf
from app.routes import register_blueprints
from app.services.money import format_money, from_minor_units


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

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # CSRF error handler for clean AJAX / API responses
    @app.errorhandler(400)
    def handle_bad_request(e):
        if 'CSRF' in str(e):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'CSRF token missing or invalid.'}), 400
        return e

    # Create tables automatically for local setup
    with app.app_context():
        db.create_all()
        try:
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

                # Check users table for theme_preference
                res_u = conn.execute(db.text("PRAGMA table_info(users)")).fetchall()
                user_cols = {row[1] for row in res_u}
                if 'theme_preference' not in user_cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN theme_preference VARCHAR(20) DEFAULT 'system' NOT NULL"))

                conn.commit()
        except Exception:
            pass

    return app
