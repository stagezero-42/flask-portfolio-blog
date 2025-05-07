import os
from app import create_app, db # Assuming db from app.extensions
# from app.models import User, Post # Import your models for shell context if you have them

# Determine the configuration name from an environment variable or use default
config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)

# Optional: Add a shell context processor for `flask shell`
# This makes certain objects available in the Flask shell without explicit imports
@app.shell_context_processor
def make_shell_context():
    context = {'db': db}
    # Add your models here to make them available in the shell
    # For example, if you have User and Post models:
    # from app.models import User, Post
    # context['User'] = User
    # context['Post'] = Post
    return context

# Optional: Add a CLI command to initialize the database or other setup tasks
@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    # This is a basic example. For production, use Flask-Migrate.
    db.drop_all() # Be careful with this in production
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    # This block is mainly for running with `python run.py` directly.
    # `flask run` will typically use the app instance created above and respect .flaskenv.
    app.run() # Debug will be controlled by FLASK_DEBUG in .flaskenv or app.config
