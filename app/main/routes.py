from flask import render_template, request,  current_app
from . import main # Import the blueprint instance
from app.models import Post # Import the Post model
from app.admin.routes import ensure_home_post_exists # Import the helper
from ..extensions import db

@main.route('/')
@main.route('/index')
def index():
    # Ensure a home post exists (especially on first run or after all posts were non-home)
    ensure_home_post_exists()

    home_post = Post.query.filter_by(category='home').order_by(Post.created_at.desc()).first()

    if not home_post:  # Fallback if ensure_home_post_exists didn't find one (e.g., no posts at all)
        home_post = Post.query.order_by(Post.created_at.desc()).first()
        if home_post:  # If there is at least one post, make it home
            home_post.category = 'home'
            try:
                db.session.add(home_post)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error setting fallback home post: {e}")

    return render_template('main/index.html', title='Home', home_post=home_post)

@main.route('/portfolio')
def portfolio():
    page = request.args.get('page', 1, type=int)
    portfolio_posts = Post.query.filter_by(category='portfolio')\
                                .order_by(Post.created_at.desc())\
                                .paginate(page=page, per_page=9) # Adjust per_page
    return render_template('main/portfolio.html', title='My Portfolio', items=portfolio_posts) # Pass 'items' for template

@main.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    blog_posts = Post.query.filter_by(category='blog')\
                           .order_by(Post.created_at.desc())\
                           .paginate(page=page, per_page=5)
    return render_template('main/blog.html', title='My Blog', posts=blog_posts)