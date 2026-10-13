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


@settings_bp.route('/settings')
@login_required
def view_settings():
    user = g.current_user
    categories = Category.query.filter_by(user_id=user.id).all()
    system_categories = Category.query.filter(Category.user_id.is_(None)).all()
    return render_template(
        'settings.html',
        user=user,
        categories=categories,
        system_categories=system_categories,
        currency_config=CURRENCY_CONFIG
    )


@settings_bp.route('/api/settings/profile', methods=['POST'])
@login_required
def update_profile():
    user = g.current_user
    data = request.get_json() or {}

    full_name = (data.get('full_name') or '').strip()
    currency = (data.get('currency') or user.currency).strip().upper()
    income_raw = data.get('monthly_income')

    if full_name:
        user.full_name = full_name
    if currency in CURRENCY_CONFIG:
        user.currency = currency
    if income_raw:
        try:
            user.monthly_income_minor_units = to_minor_units(income_raw, user.currency)
        except Exception:
            pass

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully.',
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
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Appearance preference updated to {theme}.',
        'theme': user.theme_preference
    })
