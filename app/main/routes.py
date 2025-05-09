# app/main/routes.py
from flask import render_template, request, current_app, url_for
from . import main
from app.models import Post
from app.admin.routes import ensure_home_post_exists # If used
from ..extensions import db
from bs4 import BeautifulSoup # For stripping HTML
import re # For regular expressions (sentence splitting)

def get_text_excerpt(html_content, num_sentences=2):
    if not html_content:
        # current_app.logger.debug("get_text_excerpt: HTML content is empty.")
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Remove script and style tags
    for SCRIPT_OR_STYLE_TAG in soup(["script", "style"]):
        SCRIPT_OR_STYLE_TAG.extract()

    # 2. Attempt to remove Trix figcaptions if they mostly contain filename-like metadata
    for figcaption in soup.find_all("figcaption"):
        caption_text = figcaption.get_text(separator=' ', strip=True)
        # Regex to check if caption text looks like a common image filename, optional size, or just dimensions
        if re.fullmatch(r'[\w\s\-_\.]+\.(?:jpg|jpeg|png|gif|webp|bmp|tiff|svg|ico|pdf|doc|docx|xls|xlsx|ppt|pptx)'
                        r'(?:\s+\d{1,7}(?:\.\d{1,2})?\s*(?:KB|MB|GB|B))?\.?', caption_text, re.IGNORECASE) or \
                re.fullmatch(r'\d{1,4}x\d{1,4}', caption_text) or \
                len(caption_text.split()) < 4:  # Or if it's very short (e.g., less than 4 words)
            # current_app.logger.debug(
            #     f"get_text_excerpt: Removing figcaption likely containing only filename/metadata: '{caption_text}'")
            figcaption.extract()

    # 3. Get text, trying paragraphs first
    paragraphs = soup.find_all('p')
    plain_text_from_tags = []
    if paragraphs:
        for p in paragraphs:
            plain_text_from_tags.append(p.get_text(separator=' ', strip=True))

    # If paragraph text is too short or absent, get all text from the (modified) soup
    if not plain_text_from_tags or len(" ".join(plain_text_from_tags).split()) < 15:  # Arbitrary threshold
        # current_app.logger.debug(
        #     "get_text_excerpt: Text from <p> tags is minimal or absent. Using broader text extraction from modified soup.")
        # Using the soup that has had figcaptions potentially removed
        extracted_text_from_soup = soup.get_text(separator=' ', strip=True)
    else:
        extracted_text_from_soup = " ".join(plain_text_from_tags)

    # Normalize whitespace
    extracted_plain_text = re.sub(r'\s+', ' ', extracted_text_from_soup).strip()

    if not extracted_plain_text:
        # current_app.logger.debug("get_text_excerpt: Plain text is empty after initial extraction and normalization.")
        return ""

    # current_app.logger.debug(
    #     f"get_text_excerpt: Plain text BEFORE specific filename/size stripping: \"{extracted_plain_text[:300]}...\"")

    # **4. NEW: Explicitly remove "filename.ext size KB/MB/GB." pattern from the beginning of the text**
    # This pattern looks for:
    # - Optional leading spaces/tabs
    # - Filename (word chars, spaces, hyphens, underscores, periods)
    # - Common image/doc extension
    # - Whitespace
    # - Size (number, optional decimal, KB/MB/GB/bytes/B)
    # - Optional punctuation after size (.,;)
    # - Trailing whitespace
    filename_size_pattern = r"^\s*[\w\s\-_\.]+\.(?:jpg|jpeg|png|gif|webp|bmp|tiff|svg|ico|pdf|doc|docx|xls|xlsx|ppt|pptx)\s+\d{1,7}(?:\.\d{1,2})?\s*(?:KB|MB|GB|bytes|B)\b[\.,;]?\s*"

    # Remove the pattern if it occurs at the beginning of the string
    cleaned_text = re.sub(filename_size_pattern, "", extracted_plain_text, count=1, flags=re.IGNORECASE).strip()

    if len(cleaned_text) < len(extracted_plain_text):
        pass
        #   current_app.logger.debug(f"get_text_excerpt: Plain text AFTER specific filename/size stripping: \"{cleaned_text[:300]}...\"")
    else:
        # current_app.logger.debug(
        #     f"get_text_excerpt: No leading filename/size pattern found, or stripping had no effect on length.")
        # Ensure cleaned_text is assigned even if no stripping occurred
        cleaned_text = extracted_plain_text

    if not cleaned_text:
        # current_app.logger.debug("get_text_excerpt: Plain text is empty after filename/size stripping.")
        return ""

    # 5. Sentence splitting
    # Using re.split for potentially better handling of trailing text if last sentence is incomplete.
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s', cleaned_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # 6. Filter for meaningful sentences
    # Also ensure the sentence itself doesn't re-match the filename pattern if it somehow got through
    meaningful_sentences = [
        s for s in sentences
        if len(s.split()) > 3 and not re.fullmatch(filename_size_pattern.strip('^$\\s*'), s, flags=re.IGNORECASE)
    ]  # Require more than 3 words for a sentence to be "meaningful"
    # current_app.logger.debug(
    #     f"get_text_excerpt: Found {len(meaningful_sentences)} meaningful sentences: {meaningful_sentences[:num_sentences + 1]}")  # Log one more than needed

    if not meaningful_sentences:
        words = cleaned_text.split()
        fallback_text = ' '.join(words[:35])  # Default to 35 words from cleaned text
        # current_app.logger.debug(
        #     f"get_text_excerpt: No meaningful sentences found, returning word fallback from cleaned text: \"{fallback_text}\"")
        return fallback_text

    final_excerpt = ' '.join(meaningful_sentences[:num_sentences])
    # current_app.logger.debug(f"get_text_excerpt: Returning final excerpt: \"{final_excerpt}\"")
    return final_excerpt

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
        .paginate(page=page, per_page=5)

    items_with_details = []
    # current_app.logger.debug("--- Debugging Portfolio Items ---")  # Log separator
    for post_item in portfolio_posts_pagination.items:
        excerpt_text = get_text_excerpt(post_item.content, 2)
        items_with_details.append({
            'post': post_item,
            'excerpt': excerpt_text
        })
        # Log the details for each item
    #     current_app.logger.debug(
    #         f"Post Title: \"{post_item.title}\" | "
    #         f"Has Thumbnail URL: {'Yes' if post_item.thumbnail_url else 'No'} | "
    #         f"Thumbnail URL: \"{post_item.thumbnail_url}\" | "
    #         f"Excerpt: \"{excerpt_text[:100]}...\""  # Log first 100 chars of excerpt
    #     )
    # current_app.logger.debug("--- End Debugging Portfolio Items ---")  # Log separator

    return render_template('main/portfolio.html',
                           title='My Portfolio',
                           items_pagination=portfolio_posts_pagination,
                           items_with_details=items_with_details)


@main.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    # You can make items_per_page configurable or keep it fixed
    items_per_page_blog = current_app.config.get('BLOG_ITEMS_PER_PAGE', 5)

    blog_posts_pagination = Post.query.filter_by(category='blog') \
        .order_by(Post.created_at.desc()) \
        .paginate(page=page, per_page=items_per_page_blog)  # Consistent pagination object

    items_with_details = []
    for post_item in blog_posts_pagination.items:
        # Use the same excerpt function as portfolio
        excerpt_text = get_text_excerpt(post_item.content, 2)  # Adjust num_sentences if needed
        items_with_details.append({
            'post': post_item,
            'excerpt': excerpt_text
            # thumbnail_url is already part of post_item if it exists (post_item.thumbnail_url)
        })

    return render_template('main/blog.html',
                           title='My Blog',
                           items_pagination=blog_posts_pagination,  # Pass the pagination object
                           items_with_details=items_with_details)  # Pass the detailed items

@main.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('main/view_post.html', title=post.title, post=post)
