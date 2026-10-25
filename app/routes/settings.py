"""
Settings and User Preferences routes.
"""
from flask import Blueprint, render_template, request, jsonify, g, flash, redirect, url_for, session
from app.extensions import db
from app.routes.auth import login_required
from app.models.user import User
from app.models.category import Category
from app.services.money import CURRENCY_CONFIG, to_minor_units

settings_bp = Blueprint('settings', __name__)

from app.services.location_service import (
    get_all_states,
    get_supported_countries,
    validate_indian_pincode,
    STATE_BY_ID,
    DISTRICTS_BY_STATE,
    CITIES_DATA
)

@settings_bp.route('/settings')
@login_required
def view_settings():
    user = g.current_user
    from datetime import date
    from app.services.persistent_budget_service import get_or_create_monthly_budget
    today = date.today()
    mb = get_or_create_monthly_budget(user.id, today.year, today.month)
    active_budget_minor = mb.budget_amount_minor_units if (mb and mb.budget_amount_minor_units > 0) else (user.monthly_budget_minor_units or 0)
    categories = Category.query.filter_by(user_id=user.id).all()
    system_categories = Category.query.filter(Category.user_id.is_(None)).all()
    return render_template(
        'settings.html',
        user=user,
        active_budget_minor=active_budget_minor,
        categories=categories,
        system_categories=system_categories,
        currency_config=CURRENCY_CONFIG,
        all_states=get_all_states(),
        all_countries=get_supported_countries()
    )


from app.services.budget_engine import seed_categories_for_user_type

@settings_bp.route('/api/settings/profile', methods=['POST'])
@login_required
def update_profile():
    user = g.current_user
    data = request.get_json() or {}

    full_name = (data.get('full_name') or '').strip()
    country = (data.get('country') or '').strip()
    currency = (data.get('currency') or user.currency).strip().upper()
    lang = (data.get('preferred_language') or '').strip()
    phone = (data.get('phone_number') or '').strip()
    dob = (data.get('date_of_birth') or '').strip()
    user_type = (data.get('user_type') or '').strip().lower()

    # Location preferences
    state_id = data.get('state_id')
    state_name = data.get('state_name')
    district_id = data.get('district_id')
    district_name = data.get('district_name')
    city_id = data.get('city_id')
    city_name = data.get('city_name')
    is_custom_city = bool(data.get('is_custom_city', False))
    pincode = (data.get('pincode') or '').strip() or None
    location_tier = data.get('location_tier')

    # Household commitments
    rent_raw = data.get('rent_or_emi')
    essentials_raw = data.get('essential_expenses')
    debt_raw = data.get('debt_payments')
    dependants_val = data.get('dependants')

    income_raw = data.get('monthly_income')
    opening_bal_raw = data.get('opening_balance')
    savings_target_raw = data.get('monthly_savings_target')
    goal = (data.get('primary_financial_goal') or '').strip()
    exp = (data.get('investment_experience') or '').strip()
    inv_cats = data.get('preferred_investment_categories')

    if full_name:
        user.full_name = full_name
    if country:
        user.country = country
        if country != 'India':
            # Clear Indian state/district/city if moved to international
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
    if lang:
        user.preferred_language = lang
    if phone is not None:
        user.phone_number = phone or None
    if dob is not None:
        user.date_of_birth = dob or None

    # Apply Indian location if provided
    if country == 'India' or (not country and user.country == 'India'):
        if state_id is not None:
            # If state changed, check if district belongs to new state
            if user.state_id and user.state_id != state_id:
                user.district_id = None
                user.district_name = None
                user.city_id = None
                user.city_name = None
            user.state_id = state_id or None
            user.state_name = state_name or (STATE_BY_ID.get(state_id, {}).get('name') if state_id else None)

        if district_id is not None:
            user.district_id = district_id or None
            user.district_name = district_name or None

        if city_name is not None:
            user.city_name = city_name or None
            user.city_id = city_id or ('OTHER' if is_custom_city else None)
            user.is_custom_city = is_custom_city

        if location_tier is not None:
            user.location_tier = location_tier or 'UNCLASSIFIED'

        if pincode is not None:
            if pincode:
                # Validate format
                pin_res = validate_indian_pincode(pincode, user.state_id)
                if pin_res.get('valid'):
                    user.pincode = pin_res['clean_pincode']
            else:
                user.pincode = None

    # Update household commitments
    if rent_raw not in (None, ''):
        try:
            user.rent_or_emi_minor_units = to_minor_units(rent_raw, user.currency)
        except Exception:
            pass
    if essentials_raw not in (None, ''):
        try:
            user.essential_expenses_minor_units = to_minor_units(essentials_raw, user.currency)
        except Exception:
            pass
    if debt_raw not in (None, ''):
        try:
            user.debt_payments_minor_units = to_minor_units(debt_raw, user.currency)
        except Exception:
            pass
    if dependants_val not in (None, ''):
        try:
            user.dependants_count = int(dependants_val)
        except Exception:
            pass

    # Handle Employment / User Type update without touching existing transactions
    if user_type in ('student', 'salaried') and user_type != user.user_type:
        user.user_type = user_type
        seed_categories_for_user_type(user, user_type)

    if income_raw not in (None, ''):
        try:
            user.monthly_income_minor_units = to_minor_units(income_raw, user.currency)
        except Exception:
            pass

    if opening_bal_raw not in (None, ''):
        try:
            user.opening_balance_minor_units = to_minor_units(opening_bal_raw, user.currency)
        except Exception:
            pass

    if savings_target_raw not in (None, ''):
        try:
            user.monthly_savings_target_minor_units = to_minor_units(savings_target_raw, user.currency)
        except Exception:
            pass

    budget_raw = data.get('monthly_budget')
    if budget_raw not in (None, ''):
        try:
            from datetime import date
            from app.services.persistent_budget_service import set_monthly_budget
            today = date.today()
            b_minor = to_minor_units(budget_raw, user.currency)
            if b_minor >= 0:
                set_monthly_budget(user.id, today.year, today.month, b_minor, update_future=True)
        except Exception:
            pass
    elif income_raw not in (None, '') and (not user.monthly_budget_minor_units or user.monthly_budget_minor_units == 0):
        try:
            from datetime import date
            from app.services.persistent_budget_service import set_monthly_budget
            today = date.today()
            b_minor = to_minor_units(income_raw, user.currency)
            if b_minor >= 0:
                set_monthly_budget(user.id, today.year, today.month, b_minor, update_future=True)
        except Exception:
            pass

    if goal:
        user.primary_financial_goal = goal
    if exp:
        user.investment_experience = exp
    if inv_cats:
        import json
        if isinstance(inv_cats, list):
            user.preferred_investment_categories = json.dumps(inv_cats)
        else:
            user.preferred_investment_categories = str(inv_cats)

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Profile preferences updated successfully.',
        'user': user.to_dict()
    })


@settings_bp.route('/api/settings/password', methods=['POST'])
@login_required
def update_password():
    user = g.current_user
    data = request.get_json() or {}

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not user.check_password(current_password):
        return jsonify({'success': False, 'error': 'Incorrect current password.'}), 400

    if len(new_password) < 8:
        return jsonify({'success': False, 'error': 'New password must be at least 8 characters long.'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'error': 'New passwords do not match.'}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Password changed successfully.'})


@settings_bp.route('/api/settings/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = g.current_user
    data = request.get_json() or {}
    password = data.get('password', '')

    if not user.check_password(password):
        return jsonify({'success': False, 'error': 'Incorrect password. Account deletion cancelled.'}), 400

    # Delete user and cascading records
    db.session.delete(user)
    db.session.commit()
    session.clear()

    return jsonify({'success': True, 'message': 'Your account and all associated financial records have been permanently erased.'})


@settings_bp.route('/api/settings/appearance', methods=['GET'])
@login_required
def get_appearance():
    user = g.current_user
    return jsonify({
        'success': True,
        'theme': user.theme_preference or 'system'
    })


@settings_bp.route('/api/settings/appearance', methods=['POST'])
@login_required
def update_appearance():
    user = g.current_user
    data = request.get_json() or {}
    theme = (data.get('theme') or 'system').strip().lower()

    if theme not in ('light', 'dark', 'system'):
        return jsonify({'success': False, 'error': 'Invalid theme option. Must be light, dark, or system.'}), 400

    user.theme_preference = theme
    session['theme_preference'] = theme
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Appearance preference updated to {theme}.',
        'theme': user.theme_preference
    })
