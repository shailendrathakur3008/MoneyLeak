"""
Authentication and User Account routes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from functools import wraps
from app.extensions import db
from app.models.user import User
from app.models.budget import Budget
from app.services.budget_engine import seed_default_categories
from app.services.money import to_minor_units

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            flash('Session expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard.view_dashboard'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        currency = data.get('currency', 'INR').strip().upper()

        # Validation
        if not full_name or not email or not password:
            msg = 'All fields are required.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'danger')
            return render_template('register.html')

        if len(password) < 8:
            msg = 'Password must be at least 8 characters long.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'danger')
            return render_template('register.html')

        if password != confirm_password:
            msg = 'Passwords do not match.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            msg = 'An account with this email already exists.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'danger')
            return render_template('register.html')

        # Create user
        new_user = User(
            full_name=full_name,
            email=email,
            currency=currency or 'INR',
            monthly_income_minor_units=4000000,  # default ₹40,000.00
            onboarding_completed=False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create default budget (50/30/20)
        default_budget = Budget(
            user_id=new_user.id,
            needs_percentage=50.0,
            wants_percentage=30.0,
            savings_percentage=20.0
        )
        db.session.add(default_budget)

        # Seed initial categories
        seed_default_categories(new_user)

        db.session.commit()

        # Auto-login
        session['user_id'] = new_user.id
        session.permanent = True

        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('auth.onboarding')}), 201

        flash('Registration successful! Welcome to MoneyLeak.', 'success')
        return redirect(url_for('auth.onboarding'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard.view_dashboard'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Basic rate limiting counter in session
        fail_key = f'failed_login_{email}'
        fail_count = session.get(fail_key, 0)
        if fail_count >= 6:
            msg = 'Too many failed login attempts. Please wait a minute and try again.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 429
            flash(msg, 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            session[fail_key] = fail_count + 1
            msg = 'Invalid email or password.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 401
            flash(msg, 'danger')
            return render_template('login.html')

        # Reset failed attempts on success
        session.pop(fail_key, None)
        session['user_id'] = user.id
        session.permanent = True

        next_page = request.args.get('next')
        dest = next_page if next_page and next_page.startswith('/') else url_for('dashboard.view_dashboard')

        if not user.onboarding_completed:
            dest = url_for('auth.onboarding')

        if request.is_json:
            return jsonify({'success': True, 'redirect': dest})

        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(dest)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    user = g.current_user
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        currency = data.get('currency', user.currency).strip().upper()
        income_val = data.get('monthly_income', '40000')
        income_freq = data.get('income_frequency', 'MONTHLY')
        needs_pct = float(data.get('needs_percentage', 50.0))
        wants_pct = float(data.get('wants_percentage', 30.0))
        savings_pct = float(data.get('savings_percentage', 20.0))

        # Validate percentages total 100
        if round(needs_pct + wants_pct + savings_pct, 1) != 100.0:
            msg = 'Budget percentages must sum exactly to 100%.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'danger')
            return render_template('onboarding.html', user=user)

        user.currency = currency
        user.monthly_income_minor_units = to_minor_units(income_val, currency)
        user.income_frequency = income_freq
        user.onboarding_completed = True

        # Update budget
        budget = Budget.query.filter_by(user_id=user.id).first()
        if not budget:
            budget = Budget(user_id=user.id)
            db.session.add(budget)
        budget.needs_percentage = needs_pct
        budget.wants_percentage = wants_pct
        budget.savings_percentage = savings_pct

        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('dashboard.view_dashboard')})

        flash('Your profile and 50/30/20 budget framework have been calibrated!', 'success')
        return redirect(url_for('dashboard.view_dashboard'))

    return render_template('onboarding.html', user=user)


# API ME endpoint
@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    user = g.current_user
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })
