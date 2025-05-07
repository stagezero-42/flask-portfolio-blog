from flask import Blueprint

# Create a Blueprint instance
# 'main' is the name of the blueprint
# __name__ tells the blueprint where it's defined
# template_folder='templates' specifies that this blueprint has its own templates subfolder
main = Blueprint('main', __name__, template_folder='templates')

# Import routes at the end to avoid circular dependencies
# All routes associated with the 'main' blueprint will be defined in routes.py
from . import routes