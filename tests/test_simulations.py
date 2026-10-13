from datetime import date
from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction
from app.services.simulation_engine import run_simulation


def test_savings_simulator_calculation(app, test_user):
    today = date.today()
    cats = {c.name: c for c in Category.query.filter_by(user_id=test_user.id).all()}

    # Income = ₹40,000 (4,000,000 minor)
    # Add expenses totalling ₹35,000:
    # Needs: ₹20,000 (Housing)
    # Wants: ₹15,000 (Dining ₹8,000, Food delivery ₹4,000, Shopping ₹3,000)
    t1 = Transaction(user_id=test_user.id, category_id=cats['Housing & Rent'].id, amount_minor_units=2000000, transaction_type='EXPENSE', transaction_date=today, description='Rent')
    t2 = Transaction(user_id=test_user.id, category_id=cats['Dining Out & Cafes'].id, amount_minor_units=800000, transaction_type='EXPENSE', transaction_date=today, description='Dining')
    t3 = Transaction(user_id=test_user.id, category_id=cats['Food Delivery Apps'].id, amount_minor_units=400000, transaction_type='EXPENSE', transaction_date=today, description='Delivery')
    t4 = Transaction(user_id=test_user.id, category_id=cats['Shopping & Lifestyle'].id, amount_minor_units=300000, transaction_type='EXPENSE', transaction_date=today, description='Shopping')
    db.session.add_all([t1, t2, t3, t4])
    db.session.commit()

    # Proposed changes:
    # Reduce Food delivery by ₹1,500 (150,000 minor)
    # Reduce Shopping by ₹1,000 (100,000 minor)
    # Reduce Dining by ₹500 (50,000 minor)
    # Total proposed reduction = ₹3,000 (300,000 minor)
    reductions = {
        cats['Food Delivery Apps'].id: 150000,
        cats['Shopping & Lifestyle'].id: 100000,
        cats['Dining Out & Cafes'].id: 50000,
    }

    result = run_simulation(test_user.id, reductions)

    # Baseline assertions:
    assert result['baseline']['income_minor'] == 4000000
    assert result['baseline']['expenses_minor'] == 3500000  # ₹35,000
    assert result['baseline']['surplus_minor'] == 500000    # ₹5,000

    # Proposed assertions:
    assert result['proposed']['total_reduction_minor'] == 300000       # ₹3,000
    assert result['proposed']['revised_expenses_minor'] == 3200000     # ₹32,000
    assert result['proposed']['revised_surplus_minor'] == 800000       # ₹8,000
    assert result['proposed']['annualized_savings_minor'] == 3600000   # ₹36,000

    # Verify original transactions were NOT modified
    saved_txns = Transaction.query.filter_by(user_id=test_user.id).all()
    assert len(saved_txns) == 4
    total_db_expenses = sum(t.amount_minor_units for t in saved_txns)
    assert total_db_expenses == 3500000
