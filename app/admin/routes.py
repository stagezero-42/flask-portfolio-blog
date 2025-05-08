import os
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify  # Added current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename  # For securing filenames
from . import admin  # Import the blueprint
from .forms import LoginForm, PostForm
from app.models import User, Post, db
from app import db, csrf  # Import csrf
from PIL import Image # For thumbnail generation
from bs4 import BeautifulSoup # For parsing HTML content
from urllib.parse import urlparse # For robust URL parsing

import logging
# if not current_app.debug: # Only configure basicConfig if not in debug mode (Flask might do it)
#     logging.basicConfig(level=logging.DEBUG)

# Helper function to check allowed file extensions (optional, but good practice)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_thumbnail(image_path, thumbnail_path, height):
    # current_app.logger.debug(f"create_thumbnail: Attempting for {image_path} -> {thumbnail_path} with height {height}")
    try:
        if not os.path.exists(image_path):
            # current_app.logger.error(f"create_thumbnail: Original image file not found at {image_path}")
            return False
        img = Image.open(image_path)
        # current_app.logger.debug(f"create_thumbnail: Image opened: {image_path}")

        aspect_ratio = img.width / img.height
        new_width = int(aspect_ratio * height)

        img.thumbnail((new_width, height))
        img.save(thumbnail_path)  # This will overwrite if thumb_path already exists from a previous attempt
        # current_app.logger.debug(f"create_thumbnail: Thumbnail saved: {thumbnail_path}")
        return True
    except FileNotFoundError:  # Should be caught by os.path.exists above, but good to keep
        current_app.logger.error(f"create_thumbnail: Original image file not found (again?) at {image_path}")
        return False
    except Exception as e:
        current_app.logger.error(f"create_thumbnail: Error creating thumbnail for {image_path}: {e}")
        return False


# Modified: extract_first_image_and_generate_thumbnail - NOW EXPECTS THUMBNAIL TO EXIST
def extract_first_image_and_get_urls(post_content, post_id_for_logging):
    # current_app.logger.debug(f"extract_first_image_and_get_urls: Called for post_id (context): {post_id_for_logging}")
    # current_app.logger.debug(f"extract_first_image_and_get_urls: Raw post_content: {post_content[:500]}...")

    soup = BeautifulSoup(post_content, 'html.parser')
    first_img_tag = soup.find('img')

    original_image_url_from_content = None  # URL as found in HTML content
    derived_thumbnail_url = None  # URL for the pre-generated thumbnail

    if first_img_tag:
        # current_app.logger.debug(f"extract_first_image_and_get_urls: Found <img> tag: {first_img_tag}")
        original_image_url_from_content = first_img_tag.get('src')
        # current_app.logger.debug(f"extract_first_image_and_get_urls: Extracted src: {original_image_url_from_content}")

        if original_image_url_from_content:
            media_url_path_segment = url_for('static', filename='media_files/', _external=False)
            path_from_url = None
            try:
                parsed_original_url = urlparse(original_image_url_from_content)
                path_from_url = parsed_original_url.path
            except Exception as e:
                current_app.logger.error(
                    f"extract_first_image_and_get_urls: Error parsing original_image_url_from_content: {e}")
                path_from_url = original_image_url_from_content  # Fallback

            # current_app.logger.debug(f"extract_first_image_and_get_urls: path_from_url for original: {path_from_url}")

            if path_from_url and path_from_url.startswith(media_url_path_segment):
                original_image_filename_from_url = os.path.basename(path_from_url)
                # original_image_filename_secure = secure_filename(original_image_filename_from_url) # Already secured on upload

                upload_folder = current_app.config['UPLOAD_FOLDER']
                # Path to the original file on disk (already secured name)
                # original_filepath_on_disk = os.path.join(upload_folder, original_image_filename_secure)

                # Derive thumbnail filename and path
                base, ext = os.path.splitext(original_image_filename_from_url)
                thumb_filename = f"{base}_thumb{ext}"
                thumb_filepath_on_disk = os.path.join(upload_folder, thumb_filename)
                # current_app.logger.debug(
                #     f"extract_first_image_and_get_urls: Expected thumbnail filepath: {thumb_filepath_on_disk}")

                if os.path.exists(thumb_filepath_on_disk):
                    derived_thumbnail_url = url_for('static', filename=f'media_files/{thumb_filename}',
                                                    _external=False)  # Or True if needed
                    current_app.logger.info(
                        f"extract_first_image_and_get_urls: Pre-generated thumbnail FOUND. URL: {derived_thumbnail_url}")
                else:
                    current_app.logger.warning(
                        f"extract_first_image_and_get_urls: Pre-generated thumbnail NOT FOUND at {thumb_filepath_on_disk}. This is unexpected in the new workflow.")
                    # As a fallback, you *could* try to generate it here, but it indicates an issue with the upload_trix_attachment step
                    # if create_thumbnail(original_filepath_on_disk, thumb_filepath_on_disk, 100):
                    #    derived_thumbnail_url = url_for('static', filename=f'media_files/{thumb_filename}', _external=False)
                    #    current_app.logger.info(f"extract_first_image_and_get_urls: Fallback thumbnail created. URL: {derived_thumbnail_url}")
                    # else:
                    #    current_app.logger.error(f"extract_first_image_and_get_urls: Fallback thumbnail creation FAILED.")
            else:
                current_app.logger.warning(
                    f"extract_first_image_and_get_urls: Image URL '{original_image_url_from_content}' (path: '{path_from_url}') does not match expected media path or path_from_url is None.")
        else:
            current_app.logger.debug("extract_first_image_and_get_urls: No src attribute found in the <img> tag.")
    else:
        current_app.logger.debug("extract_first_image_and_get_urls: No <img> tag found in post content.")

    return original_image_url_from_content, derived_thumbnail_url


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username_or_email.data) | (User.email == form.username_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    return render_template('admin/login.html', title='Admin Login', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@admin.route('/dashboard') # A simple dashboard page
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    # Fetch posts, ordered by most recent, and paginate them
    posts_pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10 # Adjust per_page as needed
    )
    return render_template('admin/dashboard.html', title='Admin Dashboard', posts=posts_pagination)


# Update add_post and edit_post to use the renamed function
@admin.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        # current_app.logger.debug("add_post: Form validated.")
        new_post = Post(title=form.title.data, content=form.content.data)

        # Use the modified function name
        first_img_url_in_content, actual_thumb_url = extract_first_image_and_get_urls(new_post.content, 'new_post')

        new_post.first_image_url = first_img_url_in_content  # This is the URL from the <img> src
        new_post.thumbnail_url = actual_thumb_url  # This is the URL for the _thumb.jpg

        # current_app.logger.debug(
        #     f"add_post: To be saved: first_image_url='{new_post.first_image_url}', thumbnail_url='{new_post.thumbnail_url}'")

        db.session.add(new_post)
        db.session.commit()
        # current_app.logger.debug("add_post: Post committed to DB.")
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('main.blog'))  # Or admin.dashboard
    return render_template('admin/add_post.html', title='Add New Post', form=form)


@admin.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        # current_app.logger.debug(f"edit_post ({post_id}): Form validated.")
        post.title = form.title.data
        post.content = form.content.data

        # Use the modified function name
        first_img_url_in_content, actual_thumb_url = extract_first_image_and_get_urls(post.content, post.id)

        post.first_image_url = first_img_url_in_content
        post.thumbnail_url = actual_thumb_url

        # current_app.logger.debug(
        #     f"edit_post ({post_id}): To be saved: first_image_url='{post.first_image_url}', thumbnail_url='{post.thumbnail_url}'")

        db.session.commit()
        # current_app.logger.debug(f"edit_post ({post_id}): Post committed to DB.")
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_post.html', title=f'Edit Post: "{post.title}"', form=form, post_id=post.id)


def _get_current_home_post():
    return Post.query.filter_by(category='home').first()


def _set_new_home_post(new_home_post):
    if not new_home_post:
        return None, None

    old_home_post = _get_current_home_post()
    old_home_post_id_for_js = None

    if old_home_post and old_home_post.id != new_home_post.id:
        old_home_post.category = 'blog'  # Revert old home post to 'blog'
        db.session.add(old_home_post)
        old_home_post_id_for_js = old_home_post.id

    new_home_post.category = 'home'
    db.session.add(new_home_post)
    return new_home_post, old_home_post_id_for_js


@admin.route('/set_post_category', methods=['POST'])
@login_required
# @csrf.exempt # If you are sending CSRF token via X-CSRFToken header with AJAX
# Or ensure your Flask-WTF setup handles CSRF for JSON AJAX requests
def set_post_category():
    data = request.get_json()
    post_id = data.get('post_id')
    new_category = data.get('category')

    if not all([post_id, new_category]):
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404

    if new_category not in ['home', 'portfolio', 'blog']:
        return jsonify({'success': False, 'error': 'Invalid category'}), 400

    old_home_post_id_for_js = None  # For JS to update UI

    try:
        if new_category == 'home':
            _, old_home_post_id_for_js = _set_new_home_post(post)
        else:
            # If this post was 'home' and is now changing, ensure a new home post is designated
            if post.category == 'home':
                post.category = new_category  # Change it first
                # Designate the most recent overall post as the new home post if no other is 'home'
                # This logic will be more robustly handled by ensure_home_post_exists
            else:
                post.category = new_category
            db.session.add(post)

        db.session.commit()
        # Ensure there's always a home post after any change
        ensure_home_post_exists(excluded_post_id=post.id if new_category != 'home' else None)

        return jsonify({'success': True, 'new_category': post.category, 'old_home_post_id': old_home_post_id_for_js})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating category for post {post_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Helper function to ensure a home post exists
def ensure_home_post_exists(excluded_post_id=None):
    """
    Ensures that at least one post is marked as 'home'.
    If no 'home' post exists, it marks the most recent post as 'home'.
    If excluded_post_id is provided (e.g., a post just changed from 'home' to something else),
    it avoids selecting that one as the new 'home' post in the same transaction if possible.
    """
    current_home = Post.query.filter_by(category='home').first()
    if not current_home:
        query = Post.query.order_by(Post.created_at.desc())
        if excluded_post_id:
            # Try to find a post that isn't the one just changed from home
            new_home_candidate = query.filter(Post.id != excluded_post_id).first()
            if not new_home_candidate: # If only one post exists and it was the one changed
                 new_home_candidate = query.first() # Fallback to it
        else:
            new_home_candidate = query.first()

        if new_home_candidate:
            # No need to call _set_new_home_post as this is a fallback
            new_home_candidate.category = 'home'
            db.session.add(new_home_candidate)
            db.session.commit()
            current_app.logger.info(f"No home post found. Designated post ID {new_home_candidate.id} as new home post.")

@admin.route('/delete_post/<int:post_id>', methods=['POST'])  # Only allow POST requests
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    was_home_post = (post_to_delete.category == 'home')
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash(f'Post "{post_to_delete.title}" has been deleted successfully.', 'success')
        if was_home_post:
            ensure_home_post_exists() # Ensure a new home post is selected
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash(f'Error deleting post: {str(e)}', 'danger')
        current_app.logger.error(f"Error deleting post {post_id}: {e}")

    return redirect(url_for('admin.dashboard'))


# Modified: upload_trix_attachment - NOW CREATES THUMBNAIL
@admin.route('/upload_trix_attachment', methods=['POST'])
@login_required
def upload_trix_attachment():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file part in the request.'}), 400
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if allowed_file(file.filename):
        original_filename_secure = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']

        # Path for the original file
        potential_filepath = os.path.join(upload_folder, original_filename_secure)

        # Handle existing file logic (same name, different size, etc.) - This is simplified here
        # For robustness, the original logic for checking existing file size and renaming should be kept.
        # For this example, we'll assume we save with original_filename_secure or a uniquely generated one.
        # Let's assume a simple save for now, ensure your original renaming logic is in place if needed.

        # Save the original file
        try:
            # If file exists, you might want to generate a unique name before saving
            # For simplicity, we'll overwrite here, but in production, unique names are better.
            file.save(potential_filepath)
            current_app.logger.info(f"upload_trix_attachment: Saved original file: {potential_filepath}")
        except Exception as e:
            current_app.logger.error(f"upload_trix_attachment: Error saving original file {potential_filepath}: {e}")
            return jsonify({'error': 'Server error during original file save.'}), 500

        # --- IMMEDIATELY CREATE THUMBNAIL ---
        base, ext = os.path.splitext(original_filename_secure)
        thumb_filename = f"{base}_thumb{ext}"
        thumb_filepath = os.path.join(upload_folder, thumb_filename)
        THUMBNAIL_TARGET_HEIGHT = 100  # Or your desired height

        if create_thumbnail(potential_filepath, thumb_filepath, THUMBNAIL_TARGET_HEIGHT):
            current_app.logger.info(f"upload_trix_attachment: Thumbnail created successfully: {thumb_filepath}")
        else:
            current_app.logger.error(f"upload_trix_attachment: Failed to create thumbnail for {potential_filepath}")
            # Not returning an error here as Trix only needs the original URL.
            # The main image is saved, but thumbnail creation failed. This needs monitoring.

        # URL for the original file (Trix needs this)
        file_url = url_for('static', filename=f'media_files/{original_filename_secure}', _external=True)
        return jsonify({'url': file_url}), 200

    return jsonify({'error': 'File type not allowed.'}), 400
