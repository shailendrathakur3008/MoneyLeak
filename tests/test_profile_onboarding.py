"""
Comprehensive tests for User Profile Setup, Google Auth, Email OTP,
and Onboarding Wizard Flow.
"""
import io
import json
import pytest
from app.extensions import db
from app.models.user import User
from app.models.auth_otp import EmailOTP
from app.models.category import Category
from app.models.transaction import Transaction
from app.services.budget_engine import STUDENT_DEFAULT_CATEGORIES, SALARIED_DEFAULT_CATEGORIES


def test_email_otp_flow_and_auto_registration(client, app):
    """Test Email OTP dispatch, verification, and auto-registration of new verified user."""
    with app.app_context():
        # 1. Send OTP
        res = client.post('/auth/send-otp', json={'email': 'newstudent@example.com', 'purpose': 'login'})
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert 'dev_otp' in data
        otp_code = data['dev_otp']
        assert len(otp_code) == 6

        # Check DB record
        record = EmailOTP.query.filter_by(email='newstudent@example.com', is_used=False).first()
        assert record is not None
        assert record.is_valid(otp_code)

        # 2. Verify OTP with invalid code
        bad_res = client.post('/auth/verify-otp', json={
            'email': 'newstudent@example.com',
            'otp_code': '000000',
            'purpose': 'login'
        })
        assert bad_res.status_code == 400
        assert bad_res.get_json()['success'] is False

        # 3. Verify OTP with valid code
        good_res = client.post('/auth/verify-otp', json={
            'email': 'newstudent@example.com',
            'otp_code': otp_code,
            'purpose': 'login'
        })
        assert good_res.status_code == 200
        res_data = good_res.get_json()
        assert res_data['success'] is True
        assert res_data['is_new_user'] is True
        assert res_data['redirect'] == '/onboarding'

        # Verify created user record
        u = User.query.filter_by(email='newstudent@example.com').first()
        assert u is not None
        assert u.email_verified is True
        assert u.auth_provider == 'email_otp'
        assert u.onboarding_completed is False
        assert u.onboarding_step == 1


def test_google_sign_in_flow(client, app):
    """Test Google sign-in with provider payload and profile pre-population."""
    with app.app_context():
        google_payload = {
            'email': 'googleuser@example.com',
            'name': 'Google Scholar',
            'picture': 'https://lh3.googleusercontent.com/a/avatar123',
            'sub': 'google_sub_998877'
        }
        res = client.post('/auth/google', json=google_payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['is_new_user'] is True
        assert data['redirect'] == '/onboarding'

        # Check user fields
        u = User.query.filter_by(email='googleuser@example.com').first()
        assert u is not None
        assert u.full_name == 'Google Scholar'
        assert u.profile_picture_url == 'https://lh3.googleusercontent.com/a/avatar123'
        assert u.provider_user_id == 'google_sub_998877'
        assert u.email_verified is True
        assert u.auth_provider == 'google'
        assert u.onboarding_completed is False


def test_step_by_step_onboarding_wizard_student(client, app):
    """Complete 5-step onboarding wizard for a Student user."""
    with app.app_context():
        # Create un-onboarded user
        user = User(
            full_name='Aarav Mehta',
            email='aarav@university.edu',
            auth_provider='email_otp',
            email_verified=True,
            country='India',
            currency='INR',
            onboarding_completed=False,
            onboarding_step=1
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = user_id

    # Step 1: Personal Info
    res1 = client.post('/onboarding', json={
        'step': 1,
        'full_name': 'Aarav Mehta',
        'country': 'India',
        'currency': 'INR',
        'preferred_language': 'English',
        'phone_number': '+91 9988776655',
        'date_of_birth': '2003-05-15'
    })
    assert res1.status_code == 200
    assert res1.get_json()['next_step'] == 2

    with app.app_context():
        u = db.session.get(User, user_id)
        assert u.onboarding_step == 2
        assert u.phone_number == '+91 9988776655'
        assert u.date_of_birth == '2003-05-15'

    # Step 2: Employment Status (Student)
    res2 = client.post('/onboarding', json={
        'step': 2,
        'user_type': 'student'
    })
    assert res2.status_code == 200
    assert res2.get_json()['next_step'] == 3

    with app.app_context():
        u = db.session.get(User, user_id)
        assert u.user_type == 'student'
        assert u.onboarding_step == 3

    # Step 3: Financial Preferences
    res3 = client.post('/onboarding', json={
        'step': 3,
        'monthly_income': '15000',
        'opening_balance': '5000',
        'monthly_savings_target': '3000',
        'primary_financial_goal': 'Education',
        'investment_experience': 'Beginner',
        'preferred_investment_categories': ['Equity Mutual Funds', 'Gold']
    })
    assert res3.status_code == 200
    assert res3.get_json()['next_step'] == 4

    with app.app_context():
        u = db.session.get(User, user_id)
        assert u.monthly_income_minor_units == 1500000
        assert u.opening_balance_minor_units == 500000
        assert u.monthly_savings_target_minor_units == 300000
        assert u.primary_financial_goal == 'Education'
        assert u.investment_experience == 'Beginner'

    # Step 4: Category Preferences
    res4 = client.post('/onboarding', json={
        'step': 4,
        'categories': ['Education Fees', 'Books and Stationery', 'Food', 'Part-Time Income']
    })
    assert res4.status_code == 200
    assert res4.get_json()['next_step'] == 5

    with app.app_context():
        cats = Category.query.filter_by(user_id=user_id).all()
        cat_names = [c.name for c in cats]
        assert 'Education Fees' in cat_names
        assert 'Books and Stationery' in cat_names

    # Step 5: Review and Complete
    res5 = client.post('/onboarding', json={'step': 5})
    assert res5.status_code == 200
    assert res5.get_json()['success'] is True
    assert res5.get_json()['redirect'] == '/dashboard'

    with app.app_context():
        u = db.session.get(User, user_id)
        assert u.onboarding_completed is True


def test_onboarding_resumption_and_redirection(client, app):
    """Test that incomplete onboarding resumes from saved step and completed redirects to dashboard."""
    with app.app_context():
        user = User(
            full_name='Priya Sharma',
            email='priya@work.com',
            auth_provider='local',
            onboarding_completed=False,
            onboarding_step=3
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    # Accessing /onboarding when step=3 renders onboarding page resuming at step 3
    res = client.get('/onboarding')
    assert res.status_code == 200
    assert b'Complete Your Profile' in res.data

    # Complete onboarding via step 5
    res_complete = client.post('/onboarding', json={'step': 5})
    assert res_complete.status_code == 200
    assert res_complete.get_json()['success'] is True

    # Now accessing /onboarding redirects to /dashboard
    res_done = client.get('/onboarding')
    assert res_done.status_code == 302
    assert res_done.headers['Location'] == '/dashboard'


def test_avatar_upload_and_removal(client, app):
    """Test photo upload validation and photo removal."""
    with app.app_context():
        user = User(
            full_name='Vikram Patel',
            email='vikram@test.com',
            auth_provider='local',
            onboarding_completed=True
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    # 1. Invalid file format
    res_bad = client.post('/api/profile/upload-photo', data={
        'photo': (io.BytesIO(b'dummy executable'), 'script.sh')
    }, content_type='multipart/form-data')
    assert res_bad.status_code == 400
    assert 'Invalid file format' in res_bad.get_json()['error']

    # 2. Valid image upload
    fake_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4'
    res_good = client.post('/api/profile/upload-photo', data={
        'photo': (io.BytesIO(fake_png), 'avatar.png')
    }, content_type='multipart/form-data')
    assert res_good.status_code == 200
    data = res_good.get_json()
    assert data['success'] is True
    assert 'photo_url' in data

    with app.app_context():
        u = db.session.get(User, uid)
        assert u.profile_picture_url == data['photo_url']

    # 3. Serve avatar route check
    res_serve = client.get('/api/profile/avatar/avatar_test.png')
    assert res_serve.status_code in (200, 302)

    # 4. Remove photo
    res_remove = client.post('/api/profile/remove-photo')
    assert res_remove.status_code == 200
    with app.app_context():
        u = db.session.get(User, uid)
        assert u.profile_picture_url is None

    # 5. Unauthenticated upload returns JSON 401 instead of redirecting
    with client.session_transaction() as sess:
        sess.clear()
    res_unauth = client.post('/api/profile/upload-photo', data={
        'photo': (io.BytesIO(fake_png), 'avatar.png')
    }, content_type='multipart/form-data')
    assert res_unauth.status_code == 401
    assert res_unauth.get_json()['success'] is False


def test_changing_employment_status_preserves_transactions(client, app):
    """
    Ensure changing employment status between Student and Salaried in Settings
    activates recommended categories without deleting or modifying existing transactions.
    """
    with app.app_context():
        user = User(
            full_name='Rohan Verma',
            email='rohan@company.com',
            user_type='student',
            auth_provider='local',
            onboarding_completed=True
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.flush()

        # Add custom category and a financial transaction
        custom_cat = Category(name='Robotics Club', budget_group='WANTS', user_id=user.id)
        db.session.add(custom_cat)
        db.session.flush()

        txn = Transaction(
            user_id=user.id,
            category_id=custom_cat.id,
            amount_minor_units=250000,
            transaction_type='EXPENSE',
            description='Semester kit'
        )
        db.session.add(txn)
        db.session.commit()
        uid = user.id
        txn_id = txn.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    # Switch role to 'salaried' via Settings API
    res = client.post('/api/settings/profile', json={
        'user_type': 'salaried',
        'monthly_income': '95000',
        'opening_balance': '120000',
        'primary_financial_goal': 'Home Downpayment'
    })
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    with app.app_context():
        u = db.session.get(User, uid)
        assert u.user_type == 'salaried'
        assert u.monthly_income_minor_units == 9500000
        assert u.opening_balance_minor_units == 12000000
        assert u.primary_financial_goal == 'Home Downpayment'

        # Verify transaction remains completely intact
        saved_txn = db.session.get(Transaction, txn_id)
        assert saved_txn is not None
        assert saved_txn.amount_minor_units == 250000
        assert saved_txn.description == 'Semester kit'

        # Verify new salaried categories are available
        cat_names = [c.name for c in Category.query.filter_by(user_id=uid).all()]
        assert 'Robotics Club' in cat_names  # Existing custom category preserved
        assert 'Salary' in cat_names or 'Rent' in cat_names  # Salaried categories seeded


def test_secure_email_change_via_otp(client, app):
    """Test authenticated secure email change flow using Email OTP verification."""
    with app.app_context():
        user = User(
            full_name='Ananya Sen',
            email='ananya.old@domain.com',
            auth_provider='local',
            email_verified=True,
            onboarding_completed=True
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    new_email = 'ananya.new@domain.com'

    # Step 1: Send OTP to new email with purpose='email_change'
    res_send = client.post('/auth/send-otp', json={'email': new_email, 'purpose': 'email_change'})
    assert res_send.status_code == 200
    otp_code = res_send.get_json()['dev_otp']

    # Step 2: Verify OTP and update email
    res_verify = client.post('/auth/verify-otp', json={
        'email': new_email,
        'otp_code': otp_code,
        'purpose': 'email_change',
        'new_email': new_email
    })
    assert res_verify.status_code == 200
    assert res_verify.get_json()['success'] is True

    # Verify user record updated
    with app.app_context():
        u = db.session.get(User, uid)
        assert u.email == new_email
        assert u.email_verified is True


def test_rerun_onboarding_restart(client, app):
    """Test re-running onboarding setup from settings."""
    with app.app_context():
        user = User(
            full_name='Karan Johar',
            email='karan@cinema.com',
            auth_provider='local',
            onboarding_completed=True,
            onboarding_step=5
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    res = client.post('/onboarding/restart')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['redirect'] == '/onboarding'

    with app.app_context():
        u = db.session.get(User, uid)
        assert u.onboarding_completed is False
        assert u.onboarding_step == 1


def test_user_entered_income_with_comma_preserved_and_not_overwritten(client, app):
    """
    Test that when a user enters 10,000 (with comma or currency) during profile/onboarding,
    it is saved accurately as 1000000 minor units and NOT overwritten by 40,000.
    """
    from app.services.budget_engine import calculate_budget_summary

    with app.app_context():
        user = User(
            full_name='Shailendra Thakur',
            email='shailendra@test.com',
            auth_provider='local',
            currency='INR',
            onboarding_completed=False,
            onboarding_step=1
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    # Step 3: Enter 10,000 with comma as monthly_income
    res3 = client.post('/onboarding', json={
        'step': 3,
        'user_type': 'student',
        'monthly_income': '10,000',
        'opening_balance': '5,000'
    })
    assert res3.status_code == 200
    assert res3.get_json()['success'] is True

    # Verify user record updated immediately
    with app.app_context():
        u = db.session.get(User, uid)
        assert u.monthly_income_minor_units == 1000000  # Exactly ₹10,000.00, not 40,000!
        assert u.opening_balance_minor_units == 500000

    # Step 5: Complete onboarding
    res5 = client.post('/onboarding', json={
        'step': 5,
        'primary_financial_goal': 'Education',
        'monthly_savings_target': '2,000',
        'investment_experience': 'Beginner',
        'monthly_income': '10,000',
        'user_type': 'student'
    })
    assert res5.status_code == 200
    assert res5.get_json()['success'] is True

    # Verify after Step 5 completion, monthly_income is still 10,000 (1000000 minor units)
    with app.app_context():
        u = db.session.get(User, uid)
        assert u.monthly_income_minor_units == 1000000
        assert u.onboarding_completed is True

        # Check 50/30/20 budget calculation
        summary = calculate_budget_summary(uid)
        assert summary['income']['minor'] == 1000000
        assert summary['income']['formatted'] == '₹10,000.00'
        assert summary['needs']['target_minor'] == 500000     # 50% = ₹5,000.00
        assert summary['wants']['target_minor'] == 300000     # 30% = ₹3,000.00
        assert summary['savings']['target_minor'] == 200000   # 20% = ₹2,000.00
        assert summary['surplus']['minor'] == 1000000         # ₹10,000.00 surplus when no expense
        assert summary['surplus']['formatted'] == '₹10,000.00'


def test_settings_and_budget_update_preserves_custom_amount(client, app):
    """
    Test updating monthly income with commas via Settings and Budget APIs.
    """
    with app.app_context():
        user = User(
            full_name='Test User',
            email='testuser@moneyleak.app',
            auth_provider='local',
            currency='INR',
            onboarding_completed=True,
            onboarding_step=5
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = uid

    # Update profile in settings with 10,000
    res_prof = client.post('/api/settings/profile', json={
        'full_name': 'Test User',
        'currency': 'INR',
        'monthly_income': '10,000',
        'monthly_savings_target': '2,000'
    })
    assert res_prof.status_code == 200
    assert res_prof.get_json()['success'] is True

    with app.app_context():
        u = db.session.get(User, uid)
        assert u.monthly_income_minor_units == 1000000
        assert u.monthly_savings_target_minor_units == 200000

    # Update via Budget API
    res_budget = client.put('/api/budget', json={
        'needs_percentage': 50,
        'wants_percentage': 30,
        'savings_percentage': 20,
        'monthly_income': '15,000'
    })
    assert res_budget.status_code == 200
    assert res_budget.get_json()['success'] is True

    with app.app_context():
        u = db.session.get(User, uid)
        assert u.monthly_income_minor_units == 1500000
