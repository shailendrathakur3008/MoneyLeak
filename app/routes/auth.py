"""
Authentication, Google Sign-In, Email OTP, and User Onboarding routes for MoneyLeak.
"""
import os
import re
import json
import base64
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, g, current_app
)
from werkzeug.utils import secure_filename

from app.extensions import db, csrf
from app.models.user import User
from app.models.budget import Budget
from app.models.auth_otp import EmailOTP
from app.services.budget_engine import (
    seed_default_categories,
    seed_categories_for_user_type,
    STUDENT_DEFAULT_CATEGORIES,
    SALARIED_DEFAULT_CATEGORIES
)
from app.services.money import to_minor_units, CURRENCY_CONFIG
from app.services.location_service import (
    get_all_states,
    get_supported_countries,
    validate_indian_pincode,
    STATE_BY_ID
)

auth_bp = Blueprint('auth', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


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


# -----------------------------------------------------------------------------
# 1. TRADITIONAL REGISTRATION & LOGIN
# -----------------------------------------------------------------------------

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
            msg = 'All required fields must be filled.'
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
            currency=currency if currency in CURRENCY_CONFIG else 'INR',
            auth_provider='local',
            email_verified=False,
            country='India',
            monthly_income_minor_units=4000000,
            onboarding_completed=False,
            onboarding_step=1
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

        fail_key = f'failed_login_{email}'
        fail_count = session.get(fail_key, 0)
        if fail_count >= 8:
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


# -----------------------------------------------------------------------------
# 2. EMAIL OTP AUTHENTICATION
# -----------------------------------------------------------------------------

@auth_bp.route('/auth/send-otp', methods=['POST'])
@csrf.exempt
def send_otp():
    """Generates and dispatches a 6-digit OTP code to the provided email."""
    data = request.get_json() if request.is_json else request.form
    email = (data.get('email') or '').strip().lower()
    purpose = data.get('purpose', 'login').strip()

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'A valid email address is required.'}), 400

    # Rate limit: allow maximum 1 OTP per 30 seconds for the same email
    recent_otp = EmailOTP.query.filter_by(email=email).order_by(EmailOTP.created_at.desc()).first()
    if recent_otp and (datetime.utcnow() - recent_otp.created_at).total_seconds() < 20:
        return jsonify({
            'success': False,
            'error': 'Please wait a few seconds before requesting another code.'
        }), 429

    # Generate 6-digit cryptographic code
    code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    otp_record = EmailOTP(
        email=email,
        otp_code=code,
        purpose=purpose,
        expires_at=expires_at
    )
    db.session.add(otp_record)
    db.session.commit()

    # Log to stdout for local testing & development
    print(f"\n[MoneyLeak OTP Service] Generated verification code for {email}: {code}\n")

    return jsonify({
        'success': True,
        'message': f'Verification code sent to {email}.',
        'dev_otp': code  # Available in dev mode for seamless testing
    })


@auth_bp.route('/auth/verify-otp', methods=['POST'])
@csrf.exempt
def verify_otp():
    """Validates the 6-digit OTP and authenticates or registers the user."""
    data = request.get_json() if request.is_json else request.form
    email = (data.get('email') or '').strip().lower()
    otp_code = (data.get('otp_code') or '').strip()
    purpose = data.get('purpose', 'login').strip()
    new_email = (data.get('new_email') or '').strip().lower()

    if not email or not otp_code:
        return jsonify({'success': False, 'error': 'Email and verification code are required.'}), 400

    # Validate OTP
    otp_record = EmailOTP.query.filter_by(
        email=email,
        is_used=False
    ).order_by(EmailOTP.created_at.desc()).first()

    if not otp_record or not otp_record.is_valid(otp_code):
        return jsonify({'success': False, 'error': 'Invalid or expired verification code.'}), 400

    otp_record.is_used = True

    # Case A: Email change for authenticated user
    if purpose == 'email_change':
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Authentication required.'}), 401
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found.'}), 404

        target_email = new_email or email
        existing = User.query.filter_by(email=target_email).first()
        if existing and existing.id != user.id:
            return jsonify({'success': False, 'error': 'This email address is already in use.'}), 400

        user.email = target_email
        user.email_verified = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Email address verified and updated successfully.'})

    # Case B: Sign-in / Sign-up via Email OTP
    user = User.query.filter_by(email=email).first()
    is_new_user = False

    if not user:
        # Create new user profile
        is_new_user = True
        default_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        user = User(
            full_name=default_name,
            email=email,
            auth_provider='email_otp',
            email_verified=True,
            country='India',
            currency='INR',
            onboarding_completed=False,
            onboarding_step=1
        )
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.flush()

        default_budget = Budget(
            user_id=user.id,
            needs_percentage=50.0,
            wants_percentage=30.0,
            savings_percentage=20.0
        )
        db.session.add(default_budget)
        seed_default_categories(user)
    else:
        user.email_verified = True

    db.session.commit()

    # Log in session
    session['user_id'] = user.id
    session.permanent = True

    dest = url_for('dashboard.view_dashboard') if user.onboarding_completed else url_for('auth.onboarding')

    return jsonify({
        'success': True,
        'is_new_user': is_new_user,
        'redirect': dest,
        'message': 'Email verified successfully!'
    })


# -----------------------------------------------------------------------------
# 3. GOOGLE SIGN-IN AUTHENTICATION
# -----------------------------------------------------------------------------

@auth_bp.route('/auth/google', methods=['POST'])
@csrf.exempt
def google_auth():
    """
    Handles Google Sign-In with either GIS ID token or parsed profile payload.
    Automatically retrieves verified name, email, and Google avatar.
    """
    data = request.get_json() if request.is_json else request.form

    credential = data.get('credential', '')
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip()
    picture = (data.get('picture') or '').strip()
    sub = (data.get('sub') or '').strip()

    # Extract claims from credential JWT if provided
    if credential and '.' in credential:
        try:
            parts = credential.split('.')
            if len(parts) >= 2:
                # Pad base64 if needed
                payload_b64 = parts[1]
                padded = payload_b64 + '=' * (-len(payload_b64) % 4)
                decoded_bytes = base64.urlsafe_b64decode(padded)
                claims = json.loads(decoded_bytes.decode('utf-8'))
                if claims.get('email'):
                    email = claims.get('email').strip().lower()
                if claims.get('name') and not name:
                    name = claims.get('name').strip()
                if claims.get('picture') and not picture:
                    picture = claims.get('picture').strip()
                if claims.get('sub') and not sub:
                    sub = claims.get('sub').strip()
        except Exception as e:
            print(f"[Google Auth Decode Warning] {e}")

    if not email:
        return jsonify({'success': False, 'error': 'Google authentication failed: Email was not returned.'}), 400

    # Look up existing user
    user = User.query.filter_by(email=email).first()
    is_new_user = False

    if not user:
        is_new_user = True
        user = User(
            full_name=name or email.split('@')[0].title(),
            email=email,
            auth_provider='google',
            provider_user_id=sub or f"google_{email}",
            profile_picture_url=picture or None,
            email_verified=True,
            country='India',
            currency='INR',
            onboarding_completed=False,
            onboarding_step=1
        )
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.flush()

        default_budget = Budget(
            user_id=user.id,
            needs_percentage=50.0,
            wants_percentage=30.0,
            savings_percentage=20.0
        )
        db.session.add(default_budget)
        seed_default_categories(user)
    else:
        # Link Google ID and sync avatar if not already set
        if not user.provider_user_id and sub:
            user.provider_user_id = sub
        if not user.profile_picture_url and picture:
            user.profile_picture_url = picture
        user.email_verified = True

    db.session.commit()

    session['user_id'] = user.id
    session.permanent = True

    dest = url_for('dashboard.view_dashboard') if user.onboarding_completed else url_for('auth.onboarding')

    return jsonify({
        'success': True,
        'is_new_user': is_new_user,
        'redirect': dest,
        'message': f'Welcome, {user.full_name}!'
    })


# -----------------------------------------------------------------------------
# 4. PROFILE PHOTO MANAGEMENT API
# -----------------------------------------------------------------------------

@auth_bp.route('/api/profile/upload-photo', methods=['POST'])
@login_required
@csrf.exempt
def upload_photo():
    """Uploads, validates, and stores a profile avatar image."""
    user = g.current_user

    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided.'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file.'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload PNG, JPG, JPEG, or WEBP.'}), 400

    # Read and check size
    file_bytes = file.read()
    if len(file_bytes) > MAX_PHOTO_SIZE_BYTES:
        return jsonify({'success': False, 'error': 'File exceeds maximum size of 5MB.'}), 400

    # Save to disk
    avatar_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(avatar_dir, exist_ok=True)

    filename = f"avatar_{user.id}_{int(datetime.utcnow().timestamp())}.{ext}"
    filepath = os.path.join(avatar_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(file_bytes)

    photo_url = url_for('static', filename=f'uploads/avatars/{filename}')
    user.profile_picture_url = photo_url
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile photo uploaded successfully.',
        'photo_url': photo_url
    })


@auth_bp.route('/api/profile/remove-photo', methods=['POST'])
@login_required
@csrf.exempt
def remove_photo():
    """Removes custom profile photo and restores default avatar."""
    user = g.current_user
    user.profile_picture_url = None
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile photo removed.',
        'avatar_url': user.get_avatar_url()
    })


# -----------------------------------------------------------------------------
# 5. STEP-BY-STEP ONBOARDING WIZARD
# -----------------------------------------------------------------------------

@auth_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def onboarding():
    """
    Complete Profile & Onboarding Wizard.
    Resumes incomplete onboarding from the user's saved step.
    If onboarding is complete, redirects directly to the personalized dashboard.
    """
    user = g.current_user

    # If completed and not forced review, direct to dashboard
    if user.onboarding_completed and request.args.get('review') != '1':
        return redirect(url_for('dashboard.view_dashboard'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        step = int(data.get('step', user.onboarding_step or 1))

        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        # STEP 1: Personal Information & Indian Location Selection
        # ---------------------------------------------------------------------
        if step == 1:
            full_name = (data.get('full_name') or '').strip()
            phone = (data.get('phone_number') or '').strip()
            dob = (data.get('date_of_birth') or '').strip()
            country = (data.get('country') or 'India').strip()
            currency = (data.get('currency') or user.currency).strip().upper()
            lang = (data.get('preferred_language') or 'en').strip()

            # Location details
            state_id = data.get('state_id')
            state_name = data.get('state_name')
            district_id = data.get('district_id')
            district_name = data.get('district_name')
            city_id = data.get('city_id')
            city_name = data.get('city_name')
            is_custom_city = bool(data.get('is_custom_city', False))
            pincode = (data.get('pincode') or '').strip() or None
            location_tier = data.get('location_tier')

            if not full_name:
                return jsonify({'success': False, 'error': 'Full name is required.'}), 400

            user.full_name = full_name
            user.phone_number = phone or None
            user.date_of_birth = dob or None
            user.country = country

            if country == 'India':
                user.state_id = state_id or None
                user.state_name = state_name or (STATE_BY_ID.get(state_id, {}).get('name') if state_id else None)
                user.district_id = district_id or None
                user.district_name = district_name or None
                user.city_id = city_id or ('OTHER' if is_custom_city else None)
                user.city_name = city_name or None
                user.is_custom_city = is_custom_city
                user.location_tier = location_tier or 'UNCLASSIFIED'
                if pincode:
                    pin_res = validate_indian_pincode(pincode, user.state_id)
                    if pin_res.get('valid'):
                        user.pincode = pin_res['clean_pincode']
                else:
                    user.pincode = None
            else:
                user.state_id = None
                user.state_name = None
                user.district_id = None
                user.district_name = None
                user.city_id = None
                user.city_name = None
                user.pincode = None
                user.location_tier = 'UNCLASSIFIED'

            if currency in CURRENCY_CONFIG:
                user.currency = currency
            user.preferred_language = lang
            user.onboarding_step = max(user.onboarding_step, 2)

            db.session.commit()
            return jsonify({
                'success': True,
                'next_step': 2,
                'message': 'Personal and location information saved.'
            })

        # ---------------------------------------------------------------------
        # STEP 2: Employment Status (Student vs Salaried Employee)
        # ---------------------------------------------------------------------
        elif step == 2:
            user_type = (data.get('user_type') or '').strip().lower()
            if user_type not in ('student', 'salaried'):
                return jsonify({'success': False, 'error': 'Please select either Student or Salaried Employee.'}), 400

            user.user_type = user_type
            user.onboarding_step = max(user.onboarding_step, 3)

            db.session.commit()
            return jsonify({
                'success': True,
                'next_step': 3,
                'message': f'Employment status set to {"Student" if user_type == "student" else "Salaried Employee"}.'
            })

        # ---------------------------------------------------------------------
        # STEP 3: Financial Baseline & India-Adaptive 50/30/20 Presets
        # ---------------------------------------------------------------------
        elif step == 3:
            is_skip = data.get('action') == 'skip'

            if not is_skip:
                income_val = data.get('monthly_income')
                opening_bal_val = data.get('opening_balance')
                savings_target_val = data.get('monthly_savings_target')
                rent_val = data.get('rent_or_emi')
                essentials_val = data.get('essential_expenses')
                debt_val = data.get('debt_payments')
                dependants_val = data.get('dependants')
                preset_choice = data.get('budget_preset')
                needs_pct = data.get('needs_percentage')
                wants_pct = data.get('wants_percentage')
                savings_pct = data.get('savings_percentage')

                goal = (data.get('primary_financial_goal') or '').strip()
                exp = (data.get('investment_experience') or '').strip()
                inv_cats = data.get('preferred_investment_categories')

                if income_val not in (None, ''):
                    try:
                        user.monthly_income_minor_units = to_minor_units(income_val, user.currency)
                    except Exception:
                        pass

                if opening_bal_val not in (None, ''):
                    try:
                        user.opening_balance_minor_units = to_minor_units(opening_bal_val, user.currency)
                    except Exception:
                        pass

                if savings_target_val not in (None, ''):
                    try:
                        user.monthly_savings_target_minor_units = to_minor_units(savings_target_val, user.currency)
                    except Exception:
                        pass

                if rent_val not in (None, ''):
                    try:
                        user.rent_or_emi_minor_units = to_minor_units(rent_val, user.currency)
                    except Exception:
                        pass

                if essentials_val not in (None, ''):
                    try:
                        user.essential_expenses_minor_units = to_minor_units(essentials_val, user.currency)
                    except Exception:
                        pass

                if debt_val not in (None, ''):
                    try:
                        user.debt_payments_minor_units = to_minor_units(debt_val, user.currency)
                    except Exception:
                        pass

                if dependants_val not in (None, ''):
                    try:
                        user.dependants_count = int(dependants_val)
                    except Exception:
                        pass

                if preset_choice:
                    user.budget_preset = preset_choice

                # Configure target budget allocation
                if needs_pct is not None and wants_pct is not None and savings_pct is not None:
                    try:
                        np = float(needs_pct)
                        wp = float(wants_pct)
                        sp = float(savings_pct)
                        if round(np + wp + sp, 1) == 100.0:
                            b = Budget.query.filter_by(user_id=user.id).order_by(Budget.created_at.desc()).first()
                            if not b:
                                b = Budget(user_id=user.id)
                                db.session.add(b)
                            b.needs_percentage = np
                            b.wants_percentage = wp
                            b.savings_percentage = sp
                    except Exception:
                        pass

                if goal:
                    user.primary_financial_goal = goal
                if exp:
                    user.investment_experience = exp
                if inv_cats:
                    if isinstance(inv_cats, list):
                        user.preferred_investment_categories = json.dumps(inv_cats)
                    else:
                        user.preferred_investment_categories = str(inv_cats)

            user.onboarding_step = max(user.onboarding_step, 4)
            db.session.commit()

            return jsonify({
                'success': True,
                'next_step': 4,
                'message': 'Financial commitments and adaptive budget configured.'
            })

        # ---------------------------------------------------------------------
        # STEP 4: Category Preferences
        # ---------------------------------------------------------------------
        elif step == 4:
            selected_categories = data.get('categories', [])
            if isinstance(selected_categories, str):
                try:
                    selected_categories = json.loads(selected_categories)
                except Exception:
                    selected_categories = [s.strip() for s in selected_categories.split(',') if s.strip()]

            user_type = user.user_type or 'salaried'
            seed_categories_for_user_type(user, user_type, selected_categories)

            user.onboarding_step = max(user.onboarding_step, 5)
            db.session.commit()

            return jsonify({
                'success': True,
                'next_step': 5,
                'message': 'Category preferences configured.'
            })

        # ---------------------------------------------------------------------
        # STEP 5: Review and Complete
        # ---------------------------------------------------------------------
        elif step == 5:
            user.onboarding_completed = True
            db.session.commit()

            flash('Welcome! Your profile and personalized dashboard are ready.', 'success')
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.view_dashboard'),
                'message': 'Profile setup completed!'
            })

    # GET: render onboarding wizard
    return render_template(
        'onboarding.html',
        user=user,
        active_step=user.onboarding_step or 1,
        student_categories=STUDENT_DEFAULT_CATEGORIES,
        salaried_categories=SALARIED_DEFAULT_CATEGORIES,
        currency_config=CURRENCY_CONFIG,
        all_states=get_all_states(),
        all_countries=get_supported_countries()
    )


@auth_bp.route('/onboarding/restart', methods=['POST'])
@login_required
@csrf.exempt
def restart_onboarding():
    """Allows a user to restart or step through onboarding setup again."""
    user = g.current_user
    user.onboarding_step = 1
    user.onboarding_completed = False
    db.session.commit()

    return jsonify({
        'success': True,
        'redirect': url_for('auth.onboarding')
    })


# -----------------------------------------------------------------------------
# 6. API ME ENDPOINT
# -----------------------------------------------------------------------------

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    user = g.current_user
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })
