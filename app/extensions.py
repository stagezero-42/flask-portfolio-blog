from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
# from flask_login import LoginManager # If you add authentication

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login' # Example: redirect to auth.login route
# login_manager.login_message_category = 'info'