"""
Savings Simulator routes and what-if projection API.
"""
from datetime import date
from flask import Blueprint, render_template, request, jsonify, g
from app.extensions import db
from app.routes.auth import login_required
from app.models.simulation import Simulation
from app.services.budget_engine import calculate_budget_summary
from app.services.simulation_engine import run_simulation
from app.services.money import to_minor_units

simulations_bp = Blueprint('simulations', __name__)


@simulations_bp.route('/simulator')
@login_required
def view_simulator():
    user = g.current_user
    today = date.today()
    baseline = calculate_budget_summary(user.id, today.year, today.month)
    saved_scenarios = Simulation.query.filter_by(user_id=user.id).order_by(Simulation.created_at.desc()).all()
    return render_template('simulator.html', user=user, baseline=baseline, saved_scenarios=saved_scenarios)


@simulations_bp.route('/api/simulations/calculate', methods=['POST'])
@login_required
def api_calculate_simulation():
    user = g.current_user
    data = request.get_json() or {}

    reductions_input = data.get('reductions', {})  # { "category_id": raw_amount_or_minor }
    is_minor = data.get('is_minor_units', False)

    reductions_minor = {}
    for cat_id_str, val in reductions_input.items():
        try:
            cid = int(cat_id_str)
            if is_minor:
                minor_amt = int(val)
            else:
                minor_amt = to_minor_units(val, user.currency)
            if minor_amt > 0:
                reductions_minor[cid] = minor_amt
        except (ValueError, TypeError):
            continue

    today = date.today()
    result = run_simulation(user.id, reductions_minor, today.year, today.month)
    return jsonify({'success': True, 'simulation': result})


@simulations_bp.route('/api/simulations', methods=['GET'])
@login_required
def api_get_saved_simulations():
    user = g.current_user
    sims = Simulation.query.filter_by(user_id=user.id).order_by(Simulation.created_at.desc()).all()
    return jsonify({'success': True, 'simulations': [s.to_dict() for s in sims]})


@simulations_bp.route('/api/simulations', methods=['POST'])
@login_required
def api_save_simulation():
    user = g.current_user
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    scenario_data = data.get('scenario_data') or {}

    if not name:
        return jsonify({'success': False, 'error': 'Scenario name is required.'}), 400

    sim = Simulation(
        user_id=user.id,
        name=name,
        baseline_period=data.get('baseline_period', 'CURRENT')
    )
    sim.scenario_data = scenario_data

    db.session.add(sim)
    db.session.commit()

    return jsonify({'success': True, 'simulation': sim.to_dict()}), 201


@simulations_bp.route('/api/simulations/<int:sim_id>', methods=['GET'])
@login_required
def api_get_single_simulation(sim_id):
    user = g.current_user
    sim = Simulation.query.filter_by(id=sim_id, user_id=user.id).first()
    if not sim:
        return jsonify({'success': False, 'error': 'Simulation not found.'}), 404
    return jsonify({'success': True, 'simulation': sim.to_dict()})


@simulations_bp.route('/api/simulations/<int:sim_id>', methods=['DELETE'])
@login_required
def api_delete_simulation(sim_id):
    user = g.current_user
    sim = Simulation.query.filter_by(id=sim_id, user_id=user.id).first()
    if not sim:
        return jsonify({'success': False, 'error': 'Simulation not found.'}), 404

    db.session.delete(sim)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Scenario deleted.'})
