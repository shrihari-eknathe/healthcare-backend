import logging
from flask import Flask
from flask_jwt_extended import JWTManager

from backend.config import Config
from backend.common.db import db
from backend.common.exceptions import AppException
from backend.common.logging_config import setup_logging

from backend.auth.routes import auth_bp
from backend.departments.routes import departments_bp
from backend.doctors.routes import doctors_bp
from backend.availability.routes import availability_bp
from backend.appointments.routes import appointments_bp
from backend.reimbursements.routes import reimbursements_bp

from backend.common import models_registry

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application."""
    setup_logging(log_level="INFO")
    
    logger.info("Creating Flask application")
    
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    logger.info("Extensions initialized")

    app.register_blueprint(auth_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(availability_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(reimbursements_bp)
    logger.info("Blueprints registered")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    @app.errorhandler(AppException)
    def handle_app_exception(e):
        logger.warning(f"AppException: {e.message}")
        return {"error": e.message}, e.status_code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {"error": "Internal server error"}, 500

    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

    logger.info("Flask application created successfully")
    return app
