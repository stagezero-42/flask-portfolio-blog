import os
from dotenv import load_dotenv

# Determine the absolute path to the project root directory
# This assumes config.py is in 'app/' and the .env is in the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

class Config:
    """Base configuration class. Contains default configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Define a default database URI if DATABASE_URL is not set (e.g., for SQLite in instance folder)
    # The instance folder should be at the same level as the 'app' directory
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(project_root, 'instance', 'app.db')

    @staticmethod
    def init_app(app):
        # Create the instance folder if it doesn't exist when using SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            instance_path = os.path.join(project_root, 'instance')
            if not os.path.exists(instance_path):
                try:
                    os.makedirs(instance_path)
                    print(f"Instance folder created at {instance_path}")
                except OSError as e:
                    print(f"Error creating instance folder: {e}")
        pass

class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_ECHO = False # Set to True to see SQL queries

class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Or use a file-based test DB
    WTF_CSRF_ENABLED = False # Disable CSRF for tests

class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    # Ensure DATABASE_URL is set in the environment for production

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}