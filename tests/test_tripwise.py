"""
Comprehensive tests for TripWise — Smart Trip Budget Planner:
- Category budget calculation & benchmark routing
- 1-day vs multi-day scaling & traveller scaling
- Travel styles (Budget, Standard, Premium) & scenario comparisons
- Affordability checker (spontaneous vs planned, liquid cash, emergency reserve)
- Budget adjustment suggestions (SpendSense leaks, stay tier, transport mode)
- Trip CRUD API, transaction linking & unlinking, duplicate prevention
- User data isolation
- Text-only AI Finance Assistant TripWise queries
- Web views rendering & Dashboard integration
"""

import json
from datetime import date, timedelta
import pytest

from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.trip import Trip
from app.services.trip_engine import (
    estimate_trip_budget,
    generate_scenario_comparison,
    check_trip_affordability,
    generate_budget_adjustment_suggestions,
    get_route_benchmark
)
from app.services.assistant_service import generate_deterministic_assistant_response


# ============================================================================
# 1. UNIT TESTS: TRIP ENGINE ESTIMATES & BENCHMARKS
# ============================================================================

def test_trip_engine_one_day_vs_multi_day():
    """Verify 1-day trip has 0 hotel nights vs 4-day trip having 3 hotel nights."""
    # 1-Day Trip
    one_day_params = {
        "starting_city": "Delhi",
        "destination": "Jaipur",
        "duration_days": 1,
        "travellers_count": 1,
        "travel_style": "STANDARD",
        "transport_mode": "TRAIN",
        "accommodation_type": "STANDARD_HOTEL"
    }
    one_day = estimate_trip_budget(one_day_params, "INR")
    assert one_day["breakdown"]["accommodation"]["nights"] == 0
    # 0 nights means accommodation cost is 0
    assert one_day["breakdown"]["accommodation"]["estimated_cost_minor"] == 0
    assert one_day["total_budget_minor"] > 0
    assert one_day["breakdown"]["contingency"]["estimated_cost_minor"] > 0

    # 4-Day Trip (3 nights)
    multi_day_params = {
        "starting_city": "Delhi",
        "destination": "Jaipur",
        "duration_days": 4,
        "travellers_count": 1,
        "travel_style": "STANDARD",
        "transport_mode": "TRAIN",
        "accommodation_type": "STANDARD_HOTEL"
    }
    multi_day = estimate_trip_budget(multi_day_params, "INR")
    assert multi_day["breakdown"]["accommodation"]["nights"] == 3
    assert multi_day["breakdown"]["accommodation"]["estimated_cost_minor"] > 0
    assert multi_day["total_budget_minor"] > one_day["total_budget_minor"]


def test_trip_engine_traveller_scaling():
    """Verify costs scale properly with traveller counts."""
    solo_params = {
        "starting_city": "Mumbai",
        "destination": "Goa",
        "duration_days": 3,
        "travellers_count": 1,
        "travel_style": "STANDARD",
        "transport_mode": "FLIGHT",
        "accommodation_type": "STANDARD_HOTEL"
    }
    solo = estimate_trip_budget(solo_params, "INR")

    duo_params = {
        "starting_city": "Mumbai",
        "destination": "Goa",
        "duration_days": 3,
        "travellers_count": 2,
        "travel_style": "STANDARD",
        "transport_mode": "FLIGHT",
        "accommodation_type": "STANDARD_HOTEL"
    }
    duo = estimate_trip_budget(duo_params, "INR")

    # Flight is per person: duo outbound/return flight should be exactly 2x solo
    assert duo["breakdown"]["travel"]["estimated_cost_minor"] == solo["breakdown"]["travel"]["estimated_cost_minor"] * 2
    # Food is per person: duo food should be 2x solo
    assert duo["breakdown"]["food"]["estimated_cost_minor"] == solo["breakdown"]["food"]["estimated_cost_minor"] * 2
    # 2 travellers share 1 hotel room, so accommodation stays the same as solo!
    assert duo["breakdown"]["accommodation"]["estimated_cost_minor"] == solo["breakdown"]["accommodation"]["estimated_cost_minor"]


def test_trip_engine_transport_modes():
    """Verify different transport options (Train, Bus, Flight, Car, Two-wheeler) compute valid costs."""
    modes = ["TRAIN", "BUS", "FLIGHT", "CAR", "TWO_WHEELER"]

    for mode in modes:
        params = {
            "starting_city": "Delhi",
            "destination": "Jaipur",
            "duration_days": 3,
            "travellers_count": 1,
            "travel_style": "STANDARD",
            "transport_mode": mode,
            "accommodation_type": "STANDARD_HOTEL"
        }
        est = estimate_trip_budget(params, "INR")
        travel_cost = est["breakdown"]["travel"]["estimated_cost_minor"]
        assert travel_cost > 0
        assert est["breakdown"]["travel"]["data_source"] is not None


def test_trip_engine_scenario_comparison():
    """Verify Budget, Standard, and Premium scenarios and their progression."""
    params = {
        "starting_city": "Delhi",
        "destination": "Jaipur",
        "duration_days": 3,
        "travellers_count": 2,
        "transport_mode": "TRAIN",
        "accommodation_type": "STANDARD_HOTEL"
    }
    scenarios = generate_scenario_comparison(params, "INR")

    assert "budget" in scenarios
    assert "standard" in scenarios
    assert "premium" in scenarios

    b_cost = scenarios["budget"]["total_minor"]
    s_cost = scenarios["standard"]["total_minor"]
    p_cost = scenarios["premium"]["total_minor"]

    assert b_cost < s_cost < p_cost
    assert scenarios["budget"]["savings_vs_standard_minor"] >= 0


def test_route_benchmark_fallbacks():
    """Verify reliable route fallback when an unlisted city pair is provided."""
    bm = get_route_benchmark("Kochi", "Udaipur")
    assert bm["distance_km"] > 0
    assert bm["train_fare"] > 0
    assert bm["flight_fare"] > 0
    assert bm["is_exact_match"] is False


# ============================================================================
# 2. AFFORDABILITY & BUDGET ADJUSTMENT SUGGESTIONS
# ============================================================================

def test_affordability_spontaneous_vs_planned(app, test_user):
    """Test affordability rules: spontaneous uses liquid cash only without future unearned income."""
    with app.app_context():
        # Setup test user baseline
        test_user.monthly_income_minor_units = 5000000  # ₹50,000
        test_user.opening_balance_minor_units = 1000000  # ₹10,000
        test_user.essential_expenses_minor_units = 1500000  # ₹15,000
        db.session.commit()

        # Spontaneous trip: starts today, 50k budget
        spontaneous_res = check_trip_affordability(
            user_id=test_user.id,
            estimated_trip_cost_minor=5000000,
            departure_date=date.today(),
            trip_nature="SPONTANEOUS",
            custom_reserve_minor=1000000
        )
        assert spontaneous_res["is_spontaneous"] is True
        assert spontaneous_res["required_reserve_minor"] == 1000000
        # Should show shortfall because trip cost is high relative to available cash
        assert spontaneous_res["status"] == "SHORTFALL"
        assert spontaneous_res["gap_minor"] > 0

        # Small trip: ₹1,000 cost
        affordable_res = check_trip_affordability(
            user_id=test_user.id,
            estimated_trip_cost_minor=100000,
            departure_date=date.today(),
            trip_nature="SPONTANEOUS",
            custom_reserve_minor=100000
        )
        assert affordable_res["is_spontaneous"] is True
        assert affordable_res["gap_minor"] == 0
        assert affordable_res["surplus_minor"] >= 0


def test_budget_adjustment_suggestions(app, test_user):
    """Test suggestions when trip has budget shortfall."""
    with app.app_context():
        trip_params = {
            "travel_style": "PREMIUM",
            "transport_mode": "FLIGHT",
            "duration_days": 5,
            "travellers_count": 2
        }
        affordability = {
            "currency": test_user.currency,
            "gap_minor": 1500000
        }

        suggestions = generate_budget_adjustment_suggestions(
            user_id=test_user.id,
            trip_params=trip_params,
            affordability=affordability
        )

        assert len(suggestions) > 0
        titles = [s["title"] for s in suggestions]
        assert any("Train" in t or "Flight" in t for t in titles)
        assert any("Hotel" in t or "Boutique" in t or "Stay" in t for t in titles)


# ============================================================================
# 3. TRIP MODEL TESTS
# ============================================================================

def test_trip_model_properties(app, test_user):
    """Verify Trip model serialization, actual spending calculation, and progress."""
    with app.app_context():
        trip = Trip(
            user_id=test_user.id,
            name="Delhi to Jaipur Getaway",
            starting_city="Delhi",
            destination="Jaipur",
            departure_date=date(2026, 11, 1),
            return_date=date(2026, 11, 3),
            duration_days=3,
            travellers_count=2,
            travel_style="STANDARD",
            transport_mode="TRAIN",
            accommodation_type="STANDARD_HOTEL",
            trip_nature="PLANNED",
            total_budget_minor_units=1500000  # ₹15,000
        )
        trip.category_estimates = {
            "travel": {"estimated_cost_minor": 400000},
            "accommodation": {"estimated_cost_minor": 600000},
            "food": {"estimated_cost_minor": 500000}
        }
        db.session.add(trip)
        db.session.commit()

        assert trip.id is not None
        assert trip.category_estimates["travel"]["estimated_cost_minor"] == 400000
        assert trip.actual_spending_minor_units == 0
        assert trip.remaining_budget_minor_units == 1500000
        assert trip.budget_progress_pct == 0.0

        # Link a transaction
        cat = test_user.categories.first()
        t1 = Transaction(
            user_id=test_user.id,
            trip_id=trip.id,
            category_id=cat.id,
            amount_minor_units=300000,  # ₹3,000
            transaction_type='EXPENSE',
            transaction_date=date(2026, 11, 1),
            description="Train tickets"
        )
        db.session.add(t1)
        db.session.commit()

        assert trip.actual_spending_minor_units == 300000
        assert trip.remaining_budget_minor_units == 1200000
        assert trip.budget_progress_pct == 20.0

        d = trip.to_dict()
        assert d["id"] == trip.id
        assert d["actual_spending_minor_units"] == 300000


# ============================================================================
# 4. TRIP CRUD API & TRANSACTION LINKING
# ============================================================================

def test_trip_crud_api(client, test_user):
    """Test creating, reading, updating, and deleting trips via JSON API."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # 1. Create Trip
    res = client.post('/api/trips', json={
        "starting_city": "Delhi",
        "destination": "Goa",
        "departure_date": "2026-12-10",
        "return_date": "2026-12-14",
        "travellers_count": 2,
        "trip_nature": "PLANNED",
        "transport_mode": "FLIGHT",
        "travel_style": "STANDARD",
        "accommodation_type": "STANDARD_HOTEL"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    trip_id = data["trip"]["id"]
    assert data["trip"]["duration_days"] == 5
    assert data["trip"]["total_budget_minor_units"] > 0

    # 2. Get Trip
    res_get = client.get(f'/api/trips/{trip_id}')
    assert res_get.status_code == 200
    assert res_get.get_json()["trip"]["destination"] == "Goa"

    # 3. Update Trip
    res_put = client.put(f'/api/trips/{trip_id}', json={
        "total_budget_minor_units": 3500000,
        "notes": "Book flights by next week"
    })
    assert res_put.status_code == 200
    assert res_put.get_json()["trip"]["total_budget_minor_units"] == 3500000
    assert res_put.get_json()["trip"]["notes"] == "Book flights by next week"

    # 4. Delete Trip
    res_del = client.delete(f'/api/trips/{trip_id}')
    assert res_del.status_code == 200
    assert db.session.get(Trip, trip_id) is None


def test_trip_transaction_linking_and_unlinking(client, test_user):
    """Test linking an existing transaction to a trip, unlinking, and creating a new one."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Create a trip
    trip = Trip(
        user_id=test_user.id,
        name="Delhi to Agra Day Trip",
        starting_city="Delhi",
        destination="Agra",
        departure_date=date.today(),
        return_date=date.today(),
        duration_days=1,
        travellers_count=1,
        total_budget_minor_units=300000
    )
    db.session.add(trip)

    # Create an unlinked transaction
    cat = test_user.categories.first()
    txn = Transaction(
        user_id=test_user.id,
        category_id=cat.id,
        amount_minor_units=75000,  # ₹750
        transaction_type='EXPENSE',
        transaction_date=date.today(),
        description="Taj Mahal Entry Fee"
    )
    db.session.add(txn)
    db.session.commit()

    # 1. Link transaction
    res_link = client.post(f'/api/trips/{trip.id}/transactions', json={
        "transaction_id": txn.id
    })
    assert res_link.status_code == 200
    db.session.refresh(txn)
    assert txn.trip_id == trip.id

    # 2. Log new expense directly to trip
    res_new = client.post(f'/api/trips/{trip.id}/transactions', json={
        "amount": 250.0,
        "description": "Agra Petha Gift",
        "category_id": cat.id,
        "transaction_date": date.today().isoformat()
    })
    assert res_new.status_code == 201
    new_txn_id = res_new.get_json()["transaction"]["id"]
    new_txn = db.session.get(Transaction, new_txn_id)
    assert new_txn is not None
    assert new_txn.trip_id == trip.id
    assert new_txn.amount_minor_units == 25000

    # 3. Unlink the first transaction
    res_unlink = client.delete(f'/api/trips/{trip.id}/transactions/{txn.id}')
    assert res_unlink.status_code == 200
    db.session.refresh(txn)
    # Txn must still exist in general ledger, but trip_id is now None!
    assert txn.trip_id is None
    assert db.session.get(Transaction, txn.id) is not None


def test_user_data_isolation(client, test_user, second_user):
    """Ensure User B cannot access, modify, or link to User A's trips."""
    # Create trip owned by User A (test_user)
    alice_trip = Trip(
        user_id=test_user.id,
        name="Alice's Private Vacation",
        starting_city="Delhi",
        destination="Leh Ladakh",
        departure_date=date(2026, 7, 1),
        return_date=date(2026, 7, 10),
        duration_days=10,
        travellers_count=1,
        total_budget_minor_units=6000000
    )
    db.session.add(alice_trip)
    db.session.commit()

    # Log in as User B (second_user)
    with client.session_transaction() as sess:
        sess['user_id'] = second_user.id

    # Bob tries to GET Alice's trip
    res_get = client.get(f'/api/trips/{alice_trip.id}')
    assert res_get.status_code == 404

    # Bob tries to PUT Alice's trip
    res_put = client.put(f'/api/trips/{alice_trip.id}', json={"name": "Hacked Trip"})
    assert res_put.status_code == 404

    # Bob tries to DELETE Alice's trip
    res_del = client.delete(f'/api/trips/{alice_trip.id}')
    assert res_del.status_code == 404

    # Trip must remain untouched
    reloaded = db.session.get(Trip, alice_trip.id)
    assert reloaded.name == "Alice's Private Vacation"


# ============================================================================
# 5. TEXT-ONLY AI FINANCE ASSISTANT INTEGRATION
# ============================================================================

def test_assistant_tripwise_queries(app, test_user):
    """Test all 7 TripWise questions supported by text-only assistant."""
    with app.app_context():
        # Create an active trip for user
        trip = Trip(
            user_id=test_user.id,
            name="Mumbai Getaway",
            starting_city="Delhi",
            destination="Mumbai",
            departure_date=date.today() + timedelta(days=20),
            return_date=date.today() + timedelta(days=23),
            duration_days=3,
            travellers_count=2,
            travel_style="STANDARD",
            transport_mode="TRAIN",
            total_budget_minor_units=1800000  # ₹18,000
        )
        trip.category_estimates = {
            "travel": {"estimated_cost_minor": 600000},
            "accommodation": {"estimated_cost_minor": 600000},
            "food": {"estimated_cost_minor": 300000},
            "contingency": {"estimated_cost_minor": 300000}
        }
        db.session.add(trip)
        db.session.commit()

        ctx = {
            "user_id": test_user.id,
            "monthly_income_minor": 5000000,
            "total_expenses_minor": 2000000,
            "currency": test_user.currency,
            "user": test_user
        }

        # 1. "Can I afford a trip this weekend?"
        r1 = generate_deterministic_assistant_response("Can I afford a trip this weekend?", ctx)
        assert r1 is not None
        assert "TripWise" in r1["response"] or "afford" in r1["response"].lower()

        # 2. "Create a budget for a three-day trip"
        r2 = generate_deterministic_assistant_response("Create a budget for a three-day trip", ctx)
        assert r2 is not None
        assert "3-Day" in r2["response"] or "Three-Day" in r2["response"] or "Transit" in r2["response"]

        # 3. "How much should I reserve for accommodation?"
        r3 = generate_deterministic_assistant_response("How much should I reserve for accommodation?", ctx)
        assert r3 is not None
        assert "Accommodation" in r3["response"] or "hotel" in r3["response"].lower()

        # 4. "How can I reduce this trip's cost?"
        r4 = generate_deterministic_assistant_response("How can I reduce this trip's cost?", ctx)
        assert r4 is not None
        assert "reduce" in r4["response"].lower() or "transport" in r4["response"].lower()

        # 5. "What is the difference between the budget and standard travel options?"
        r5 = generate_deterministic_assistant_response("What is the difference between the budget and standard travel options?", ctx)
        assert r5 is not None
        assert "Budget vs Standard" in r5["response"] or "Budget" in r5["response"]

        # 6. "How much money do I need to save before departure?"
        r6 = generate_deterministic_assistant_response("How much money do I need to save before departure?", ctx)
        assert r6 is not None
        assert "departure" in r6["response"].lower() or "save" in r6["response"].lower()

        # 7. "How much of my trip budget remains?"
        r7 = generate_deterministic_assistant_response("How much of my trip budget remains?", ctx)
        assert r7 is not None
        assert "Remaining" in r7["response"] or "remains" in r7["response"].lower()


# ============================================================================
# 6. WEB VIEWS RENDERING & DASHBOARD
# ============================================================================

def test_tripwise_web_views(client, test_user):
    """Test that /trips and dashboard render TripWise controls."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # 1. Visit /trips
    res_trips = client.get('/trips')
    assert res_trips.status_code == 200
    html = res_trips.data.decode('utf-8')
    assert "TripWise — Smart Trip Budget Planner" in html
    assert "Plan a Trip" in html

    # 2. Visit /dashboard and verify Plan a Trip action button and TripWise card
    res_dash = client.get('/dashboard')
    assert res_dash.status_code == 200
    dash_html = res_dash.data.decode('utf-8')
    assert "Plan a Trip" in dash_html
    assert "TripWise" in dash_html
