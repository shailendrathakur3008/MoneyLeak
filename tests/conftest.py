import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.budget import Budget
from app.services.budget_engine import seed_default_categories


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    user = User(
        full_name='Test Alice',
        email='alice@example.com',
        currency='INR',
        monthly_income_minor_units=4000000,  # ₹40,000.00
        onboarding_completed=True
    )
    user.set_password('securePassword123')
    db.session.add(user)
    db.session.flush()

    budget = Budget(
        user_id=user.id,
        needs_percentage=50.0,
        wants_percentage=30.0,
        savings_percentage=20.0
    )
    db.session.add(budget)
    seed_default_categories(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(app):
    user = User(
        full_name='Test Bob',
        email='bob@example.com',
        currency='INR',
        monthly_income_minor_units=6000000,  # ₹60,000.00
        onboarding_completed=True
    )
    user.set_password('bobPassword123')
    db.session.add(user)
    db.session.flush()

    budget = Budget(
        user_id=user.id,
        needs_percentage=50.0,
        wants_percentage=30.0,
        savings_percentage=20.0
    )
    db.session.add(budget)
    seed_default_categories(user)
    db.session.commit()
    return user
