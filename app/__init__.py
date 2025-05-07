from flask import Flask, render_template
from .config import config
from .extensions import db, migrate, csrf,  login_manager

def create_app(config_name='default'):
    """
    Application factory function.
    Initializes and configures the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) # Call static init_app if defined in Config

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db) # Initialize Flask-Migrate
    csrf.init_app(app) # Initialize CSRF protection
    login_manager.init_app(app) # If using Flask-Login

    # Register Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register your new admin blueprint
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # from .auth import auth as auth_blueprint # If you have an auth blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Optional: Register a simple route for testing
    # @app.route('/hello')
    # def hello():
    #    return "Hello, World from App Factory!"

    # Register custom error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """Register custom error pages."""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        # It's good practice to also log the error here
        # db.session.rollback() # If the error was DB related
        return render_template('errors/500.html'), 500

    # You can add more handlers for 403, 401, etc.