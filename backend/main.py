import logging
from flask import Flask
from flask_jwt_extended import JWTManager

from backend.config import Config
from backend.common.db import db
from backend.common.exceptions import AppException
from backend.common.logging_config import setup_logging

# Import blueprints
from backend.auth.routes import auth_bp
from backend.departments.routes import departments_bp
from backend.doctors.routes import doctors_bp

# Force SQLAlchemy to see all models
from backend.auth import models as auth_models
from backend.departments import models as department_models
from backend.doctors import models as doctor_models

logger = logging.getLogger(__name__)


def create_app():
    """Application factory to create and configure the Flask app."""
    
    # Setup logging first
    setup_logging(log_level="INFO")
    
    logger.info("Creating Flask application")
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    logger.info("Extensions initialized")

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(doctors_bp)
    logger.info("Blueprints registered")

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return {"status": "ok"}

    @app.errorhandler(AppException)
    def handle_app_exception(e):
        """Handle application-specific exceptions."""
        logger.warning(f"AppException: {e.message}")
        return {"error": e.message}, e.status_code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {"error": "Internal server error"}, 500

    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

    logger.info("Flask application created successfully")
    return app
