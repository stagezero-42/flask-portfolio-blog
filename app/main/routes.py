from flask import render_template, request
from . import main # Import the blueprint instance
from app.models import Post # Import the Post model

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
    # Fetch posts from the database, ordered by creation date (newest first)
    page = request.args.get('page', 1, type=int) # For pagination later
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=5 # Adjust per_page as needed
    )
    # The old static blog_posts can be removed
    return render_template('main/blog.html', title='My Blog', posts=posts) # Pass the paginate object