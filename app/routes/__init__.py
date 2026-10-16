from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.transactions import transactions_bp
from app.routes.income import income_bp
from app.routes.categories import categories_bp
from app.routes.budget import budget_bp
from app.routes.analysis import analysis_bp
from app.routes.simulations import simulations_bp
from app.routes.goals import goals_bp
from app.routes.reports import reports_bp
from app.routes.settings import settings_bp
from app.routes.tools import tools_bp
from app.routes.assistant import assistant_bp
from app.routes.locations import locations_bp
from app.routes.trips import trips_bp
from app.routes.sync import sync_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(simulations_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(trips_bp)
