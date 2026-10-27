"""
Demo Data Seeder for MoneyLeak.

Seeds a realistic student/young professional profile:
- Monthly Salary: ₹40,000
- 50/30/20 Allocation: Needs ₹20,000, Wants ₹12,000, Savings ₹8,000
- Sample realistic transactions for the current month and previous month
- Active recurring subscriptions (Netflix, Spotify, Gym)
- Active Financial Goals (Emergency Fund, Goa Trip)
- Triggered MoneyLeak alerts with explainable reasons!
"""
from datetime import date, timedelta
from app.extensions import db
from app.models.user import User
from app.models.budget import Budget, MonthlyBudget
from app.models.category import Category
from app.models.income import IncomeRecord
from app.models.transaction import Transaction
from app.models.goal import SavingsGoal, GoalContribution
from app.models.recurring_payment import RecurringPayment
from app.services.budget_engine import seed_default_categories
from app.services.leak_detection import run_leak_detection
from app.services.money import to_minor_units


def seed_demo_user(force_reseed: bool = False):
    demo_email = 'demo@moneyleak.app'
    user = User.query.filter_by(email=demo_email).first()
    if user and not force_reseed and user.transactions.count() > 0:
        return user

    if user:
        # Delete old demo user to re-seed cleanly
        db.session.delete(user)
        db.session.commit()

    # Create demo user
    user = User(
        full_name='Tanu Sharma',
        email=demo_email,
        currency='INR',
        monthly_income_minor_units=4000000,  # ₹40,000.00
        monthly_budget_minor_units=4000000,
        income_frequency='MONTHLY',
        user_type='salaried',
        country='India',
        state_id='KA',
        state_name='Karnataka',
        city_name='Bengaluru',
        location_tier='METRO',
        budget_preset='metro',
        theme_preference='light',
        profile_picture_url='https://api.dicebear.com/7.x/initials/svg?seed=Tanu%20Sharma&backgroundColor=059669&textColor=ffffff',
        auth_provider='local',
        email_verified=True,
        onboarding_completed=True,
        onboarding_step=5
    )
    user.set_password('demo1234')
    db.session.add(user)
    db.session.flush()

    # Create 50/30/20 budget
    budget = Budget(
        user_id=user.id,
        needs_percentage=50.0,
        wants_percentage=30.0,
        savings_percentage=20.0
    )
    db.session.add(budget)

    # Seed default categories
    seed_default_categories(user)
    db.session.flush()

    # Query categories map
    cats = {c.name: c for c in Category.query.filter_by(user_id=user.id).all()}

    today = date.today()
    curr_y, curr_m = today.year, today.month

    # Income record
    inc = IncomeRecord(
        user_id=user.id,
        amount_minor_units=4000000,
        income_source='Infosys Salary Credit',
        received_date=date(curr_y, curr_m, 1),
        notes='Monthly net salary'
    )
    db.session.add(inc)

    # Recurring Subscriptions
    subs = [
        ('Netflix Premium UHD', 64900, 'MONTHLY', cats.get('Subscriptions & Streaming')),
        ('Spotify Duo', 14900, 'MONTHLY', cats.get('Subscriptions & Streaming')),
        ('Cult.fit Gym Pass', 175000, 'MONTHLY', cats.get('Healthcare & Pharmacy')),
        ('Amazon Prime', 149900, 'YEARLY', cats.get('Subscriptions & Streaming')),
    ]
    for name, amt, freq, cat in subs:
        rp = RecurringPayment(
            user_id=user.id,
            name=name,
            amount_minor_units=amt,
            frequency=freq,
            next_due_date=date(curr_y, curr_m, 15),
            category_id=cat.id if cat else None,
            status='ACTIVE'
        )
        db.session.add(rp)

    # Current Month Transactions
    sample_txns = [
        # Needs (Total approx ₹18,400)
        (cats.get('Housing & Rent'), 1200000, 'EXPENSE', date(curr_y, curr_m, 2), 'Rent Payment', 'Landlord Sh. Rao'),
        (cats.get('Essential Groceries'), 320000, 'EXPENSE', date(curr_y, curr_m, 5), 'Zepto & Nature Basket Staples', 'Zepto'),
        (cats.get('Utilities (Power, Water, Gas)'), 145000, 'EXPENSE', date(curr_y, curr_m, 7), 'BESCOM Electricity Bill', 'BESCOM'),
        (cats.get('Essential Commute & Fuel'), 110000, 'EXPENSE', date(curr_y, curr_m, 10), 'Namma Metro Card Recharge', 'BMRCL'),
        (cats.get('Basic Internet & Mobile'), 65000, 'EXPENSE', date(curr_y, curr_m, 8), 'Airtel Fiber Broadband', 'Airtel'),

        # Wants (Over target at approx ₹13,850 > ₹12,000 to trigger Rule 1 leak!)
        (cats.get('Dining Out & Cafes'), 420000, 'EXPENSE', date(curr_y, curr_m, 4), 'Weekend Dinner with Friends', 'Toit Indiranagar'),
        (cats.get('Food Delivery Apps'), 310000, 'EXPENSE', date(curr_y, curr_m, 9), 'Late Night Swiggy & Zomato', 'Swiggy'),
        (cats.get('Shopping & Lifestyle'), 390000, 'EXPENSE', date(curr_y, curr_m, 6), 'Myntra Autumn Sale Clothes', 'Myntra'),
        (cats.get('Entertainment & Outings'), 180000, 'EXPENSE', date(curr_y, curr_m, 11), 'PVR IMAX Movie Tickets', 'PVR Cinemas'),
        (cats.get('Subscriptions & Streaming'), 85000, 'EXPENSE', date(curr_y, curr_m, 3), 'Streaming subscriptions auto-debit', 'Apple Services'),

        # Savings & Investment contributions (₹6,500 < ₹8,000 target to trigger savings gap!)
        (cats.get('Mutual Funds & Stocks'), 400000, 'SAVINGS_CONTRIBUTION', date(curr_y, curr_m, 5), 'Nifty 50 Index SIP', 'Zerodha Coin'),
        (cats.get('Emergency Fund'), 250000, 'SAVINGS_CONTRIBUTION', date(curr_y, curr_m, 5), 'Liquid Fund Emergency Buffer', 'Groww'),
    ]

    # Monthly Budgets
    mb_curr = MonthlyBudget(
        user_id=user.id,
        year=curr_y,
        month=curr_m,
        budget_amount_minor_units=4000000,
        is_manually_set=True
    )
    db.session.add(mb_curr)

    # Previous Month Benchmark Context
    last_m_anchor = date(curr_y, curr_m, 1) - timedelta(days=15)
    prev_y, prev_m = last_m_anchor.year, last_m_anchor.month

    mb_prev = MonthlyBudget(
        user_id=user.id,
        year=prev_y,
        month=prev_m,
        budget_amount_minor_units=4000000,
        is_manually_set=True
    )
    db.session.add(mb_prev)

    inc_prev = IncomeRecord(
        user_id=user.id,
        amount_minor_units=4000000,
        income_source='Infosys Salary Credit',
        received_date=date(prev_y, prev_m, 1),
        notes='Previous month net salary'
    )
    db.session.add(inc_prev)

    # Previous Month Transactions
    prev_sample_txns = [
        (cats.get('Housing & Rent'), 1200000, 'EXPENSE', date(prev_y, prev_m, 2), 'Rent Payment', 'Landlord Sh. Rao'),
        (cats.get('Essential Groceries'), 285000, 'EXPENSE', date(prev_y, prev_m, 6), 'Zepto & Nature Basket Staples', 'Zepto'),
        (cats.get('Utilities (Power, Water, Gas)'), 135000, 'EXPENSE', date(prev_y, prev_m, 8), 'BESCOM Electricity Bill', 'BESCOM'),
        (cats.get('Essential Commute & Fuel'), 95000, 'EXPENSE', date(prev_y, prev_m, 11), 'Namma Metro Card Recharge', 'BMRCL'),
        (cats.get('Dining Out & Cafes'), 380000, 'EXPENSE', date(prev_y, prev_m, 14), 'Team Lunch', 'Toit Indiranagar'),
        (cats.get('Food Delivery Apps'), 240000, 'EXPENSE', date(prev_y, prev_m, 18), 'Swiggy Dinner Orders', 'Swiggy'),
        (cats.get('Mutual Funds & Stocks'), 800000, 'SAVINGS_CONTRIBUTION', date(prev_y, prev_m, 5), 'Nifty 50 Index SIP', 'Zerodha Coin'),
    ]
    for cat, amt, t_type, t_date, desc, merchant in prev_sample_txns:
        if cat:
            t = Transaction(
                user_id=user.id,
                category_id=cat.id,
                amount_minor_units=amt,
                transaction_type=t_type,
                transaction_date=t_date,
                description=desc,
                merchant=merchant
            )
            db.session.add(t)

    for cat, amt, t_type, t_date, desc, merchant in sample_txns:
        if cat:
            t = Transaction(
                user_id=user.id,
                category_id=cat.id,
                amount_minor_units=amt,
                transaction_type=t_type,
                transaction_date=t_date,
                description=desc,
                merchant=merchant
            )
            db.session.add(t)

    # Goals
    g1 = SavingsGoal(
        user_id=user.id,
        name='Emergency Safety Cushion',
        target_amount_minor_units=12000000,  # ₹1,20,000
        target_date=date(curr_y + 1, 3, 31),
        category_type='EMERGENCY_FUND',
        status='ACTIVE',
        icon='shield'
    )
    db.session.add(g1)
    db.session.flush()

    gc1 = GoalContribution(
        user_id=user.id,
        goal_id=g1.id,
        amount_minor_units=4500000,  # ₹45,000
        contribution_date=date(curr_y, curr_m, 5),
        notes='Initial emergency allocation'
    )
    db.session.add(gc1)

    g2 = SavingsGoal(
        user_id=user.id,
        name='Goa Vacation Trip',
        target_amount_minor_units=3000000,  # ₹30,000
        target_date=date(curr_y, 12, 20),
        category_type='TRAVEL',
        status='ACTIVE',
        icon='compass'
    )
    db.session.add(g2)
    db.session.flush()

    gc2 = GoalContribution(
        user_id=user.id,
        goal_id=g2.id,
        amount_minor_units=1200000,  # ₹12,000
        contribution_date=date(curr_y, curr_m, 6),
        notes='Saved from festival bonus'
    )
    db.session.add(gc2)

    db.session.commit()

    # Trigger leak detection to generate initial explainable alerts
    run_leak_detection(user.id, curr_y, curr_m)

    print(f"Successfully seeded demo user: {demo_email} (Password: demo1234)")
    return user


if __name__ == '__main__':
    from app import create_app
    app = create_app('development')
    with app.app_context():
        seed_demo_user()
