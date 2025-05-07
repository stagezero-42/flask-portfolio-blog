from flask import render_template
from . import main # Import the blueprint instance

@main.route('/')
@main.route('/index')
def index():
    """Renders the main index page."""
    # You can pass data to your template like this:
    # name = "Visitor"
    # return render_template('main/index.html', title='Welcome', username=name)
    return render_template('main/index.html', title='Home')

@main.route('/portfolio')
def portfolio():
    """Renders the portfolio page."""
    # Replace with actual portfolio items later
    portfolio_items = [
        {'id': 1, 'title': 'Project Alpha', 'description': 'A cool web app.'},
        {'id': 2, 'title': 'Project Beta', 'description': 'Another amazing project.'}
    ]
    return render_template('main/portfolio.html', title='My Portfolio', items=portfolio_items)

@main.route('/blog')
def blog():
    """Renders the blog page."""
    # Replace with actual blog posts later
    blog_posts = [
        {'id': 1, 'title': 'My First Blog Post', 'date': '2025-05-01', 'excerpt': 'This is the beginning...'},
        {'id': 2, 'title': 'Flask Tips', 'date': '2025-05-05', 'excerpt': 'Some useful tips for Flask dev.'}
    ]
    return render_template('main/blog.html', title='My Blog', posts=blog_posts)