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


def test_savings_simulator_calculate_api_with_decimals_and_caps(client, test_user):
    today = date.today()
    cats = {c.name: c for c in Category.query.filter_by(user_id=test_user.id).all()}

    # Spend ₹4,000 on Food Delivery (400,000 minor)
    t = Transaction(
        user_id=test_user.id,
        category_id=cats['Food Delivery Apps'].id,
        amount_minor_units=400000,
        transaction_type='EXPENSE',
        transaction_date=today,
        description='Zomato'
    )
    db.session.add(t)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # 1. Decimal trim: ₹1,000.50
    res = client.post('/api/simulations/calculate', json={
        'reductions': {
            str(cats['Food Delivery Apps'].id): 1000.50
        },
        'is_minor_units': False
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['simulation']['proposed']['total_reduction_minor'] == 100050
    assert data['simulation']['proposed']['annualized_savings_minor'] == 100050 * 12

    # 2. Exceeding trim: ₹6,000 entered for ₹4,000 spend -> capped to ₹4,000 (400,000 minor)
    res_exceed = client.post('/api/simulations/calculate', json={
        'reductions': {
            str(cats['Food Delivery Apps'].id): 6000
        },
        'is_minor_units': False
    })
    assert res_exceed.status_code == 200
    data_exceed = res_exceed.get_json()
    assert data_exceed['simulation']['proposed']['total_reduction_minor'] == 400000

    # 3. Negative trim: should be ignored and not corrupt calculations
    res_neg = client.post('/api/simulations/calculate', json={
        'reductions': {
            str(cats['Food Delivery Apps'].id): -500
        },
        'is_minor_units': False
    })
    assert res_neg.status_code == 200
    data_neg = res_neg.get_json()
    assert data_neg['simulation']['proposed']['total_reduction_minor'] == 0


def test_savings_simulator_api_uncategorized_and_scenarios(client, test_user):
    today = date.today()
    # Uncategorized expense: category_id = None -> becomes cat id 0 in summary
    t_uncat = Transaction(
        user_id=test_user.id,
        category_id=None,
        amount_minor_units=500000,  # ₹5,000
        transaction_type='EXPENSE',
        transaction_date=today,
        description='Cash outflow'
    )
    db.session.add(t_uncat)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Simulate reduction on uncategorized spending (catId: 0)
    res = client.post('/api/simulations/calculate', json={
        'reductions': {
            '0': 2000
        },
        'is_minor_units': False
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['simulation']['proposed']['total_reduction_minor'] == 200000

    # Scenario Save, Get, Delete
    save_res = client.post('/api/simulations', json={
        'name': 'Frugal Plan A',
        'scenario_data': {'0': 2000}
    })
    assert save_res.status_code == 201
    sim_id = save_res.get_json()['simulation']['id']

    # Get single
    get_res = client.get(f'/api/simulations/{sim_id}')
    assert get_res.status_code == 200
    assert get_res.get_json()['simulation']['name'] == 'Frugal Plan A'

    # Delete
    del_res = client.delete(f'/api/simulations/{sim_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True


def test_savings_simulator_page_render(client, test_user):
    today = date.today()
    cats = {c.name: c for c in Category.query.filter_by(user_id=test_user.id).all()}
    t = Transaction(
        user_id=test_user.id,
        category_id=cats['Dining Out & Cafes'].id,
        amount_minor_units=300000,
        transaction_type='EXPENSE',
        transaction_date=today,
        description='Lunch'
    )
    db.session.add(t)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/simulator')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Savings Simulator (What-If Engine)' in html
    assert 'Adjust Category Reductions' in html
    assert 'Current Monthly Spending' in html
    assert 'Reduce Spending By' in html
    assert 'Proposed Monthly Spending' in html
    assert 'Reset Reductions' in html
    assert 'Projected Annual Savings' in html
    assert 'MoneyLeakSimulatorConfig' in html

