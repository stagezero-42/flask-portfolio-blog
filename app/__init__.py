# app/__init__.py
from flask import Flask, render_template
from .config import config
from .extensions import db, migrate, csrf,  login_manager
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(config_name='default'):
    """
    Application factory function.
    Initializes and configures the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Apply ProxyFix: Trust headers from one hop (Caddy)
    # x_proto=1 tells Flask to trust the X-Forwarded-Proto header (e.g., 'https')
    # x_host=1 tells Flask to trust the X-Forwarded-Host header (e.g., 'serenity.stagezero.com.au')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

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

    # Context Processor for Footer Data
    @app.context_processor
    def inject_footer_data():
        # It's crucial to import models *inside* the function or ensure the app context
        # is fully active, especially if models themselves might import things that need the app.
        # For simplicity and to avoid circular import issues, importing here is often safest.
        from .models import FooterIcon, SiteConfiguration

        footer_icons_list = []
        copyright_message_text = None
        current_year_val = datetime.utcnow().year

        try:
            # These database queries require an active application context and
            # for the database to be initialized. This is generally fine when requests
            # are being processed, but be mindful during initial `flask db init` or similar commands.
            footer_icons_list = FooterIcon.query.order_by(FooterIcon.order).all()
            copyright_config = SiteConfiguration.query.filter_by(key='copyright_message').first()
            if copyright_config:
                copyright_message_text = copyright_config.value
        except Exception as e:
            # Log a warning if data can't be fetched, which might happen during initial setup
            # before the database tables are created, or if the DB is temporarily unavailable.
            app.logger.warning(f"Could not load footer data from DB for context processor: {e}. "
                               "This might be normal during initial setup or migrations.")
            # Fallback values will be used if an error occurs

        # Provide a sensible default for the copyright message if not found in the database
        if copyright_message_text is None:
            copyright_message_text = f"&copy; {current_year_val} Your Company Name. All Rights Reserved."
        elif "{year}" in copyright_message_text: # Allow dynamic year replacement
            copyright_message_text = copyright_message_text.replace("{year}", str(current_year_val))

        return dict(
            footer_icons=footer_icons_list,
            copyright_message=copyright_message_text,
            current_year=current_year_val # You already have a current_year block, so this might be redundant
                                          # or you can rename it to avoid conflict, e.g., `footer_current_year`
        )

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