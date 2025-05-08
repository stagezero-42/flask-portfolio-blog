from flask import render_template, request,  current_app
from . import main # Import the blueprint instance
from app.models import Post # Import the Post model
from app.admin.routes import ensure_home_post_exists # Import the helper
from ..extensions import db
from bs4 import BeautifulSoup # For stripping HTML for excerpt


def get_text_excerpt(html_content, num_lines=5):
    """
    Extracts plain text from HTML and returns the first num_lines.
    This is a basic implementation. More sophisticated line breaking might be needed.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator='\n')  # Use newline as separator
    lines = text_content.splitlines()

    # Filter out empty lines and take the first num_lines
    actual_lines = [line for line in lines if line.strip()][:num_lines]
    return "\n".join(actual_lines)

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
    portfolio_posts_pagination = Post.query.filter_by(category='portfolio') \
        .order_by(Post.created_at.desc()) \
        .paginate(page=page, per_page=10)  # Changed to 10 per page

    # Prepare items with excerpts if not done in model
    items_with_details = []
    for post in portfolio_posts_pagination.items:
        items_with_details.append({
            'post': post,
            'excerpt': get_text_excerpt(post.content, 5)  # Generate 5 lines of text excerpt
        })

    return render_template('main/portfolio.html',
                           title='My Portfolio',
                           items_pagination=portfolio_posts_pagination,  # Pass the pagination object
                           items_with_details=items_with_details)  # Pass items with details

@main.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    blog_posts = Post.query.filter_by(category='blog')\
                           .order_by(Post.created_at.desc())\
                           .paginate(page=page, per_page=5)
    return render_template('main/blog.html', title='My Blog', posts=blog_posts)

@main.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('main/view_post.html', title=post.title, post=post)
