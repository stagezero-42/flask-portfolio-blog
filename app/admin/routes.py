import os
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify  # Added current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename  # For securing filenames
from . import admin  # Import the blueprint
from .forms import LoginForm, PostForm
from app.models import User, Post
from app import db, csrf  # Import csrf

# Helper function to check allowed file extensions (optional, but good practice)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@admin.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        # Content now comes from the hidden input field populated by Trix
        new_post = Post(title=form.title.data, content=form.content.data)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('main.blog'))
        # Pre-populate Trix editor if editing (example for later, not implemented here)
    # elif request.method == 'GET' and post_to_edit: 
    #     form.title.data = post_to_edit.title
    #     form.content.data = post_to_edit.content # This will populate the hidden input
    return render_template('admin/add_post.html', title='Add New Post', form=form)


@admin.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    # You might want to add an ownership check here if posts are tied to users
    # For example: if post.author != current_user and not current_user.is_admin_role():
    #                  abort(403)

    form = PostForm(obj=post)  # Pre-populate form with post data

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # If you add a 'last_modified_at' field to your Post model, update it here
        # post.last_modified_at = datetime.utcnow()
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))  # Or redirect to the main blog page or the edited post

    # For GET requests, the form is already populated because of obj=post
    # The 'form.content.data' will correctly populate the hidden input for Trix
    # because when add_post.html (or edit_post.html) renders:
    # <input id="content" type="hidden" name="content" value="{{ form.content.data if form.content.data else '' }}">
    # this will use the pre-populated data.

    return render_template('admin/edit_post.html', title=f'Edit Post: "{post.title}"', form=form, post_id=post.id)


# Route to handle Trix file uploads
@admin.route('/upload_trix_attachment', methods=['POST'])
@login_required
# If you are sending the CSRF token with your AJAX request (as in the JS example),
# you might not need @csrf.exempt. Test carefully.
# If CSRF is handled globally and you don't send token with AJAX, exemption might be needed.
# For this example, assuming token is sent with JS:
# @csrf.exempt
def upload_trix_attachment():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file part in the request.'}), 400
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']

        # Get the size of the uploaded file
        # To do this without saving, we need to read its stream.
        # file.seek(0, os.SEEK_END) would find the end, then file.tell() gives size.
        # But we need to be careful not to consume the stream if we save it later.
        # A common way is to save to a temporary location or read into memory if files are small.
        # For simplicity here, let's get the size after checking existence and before deciding to save.
        # A more robust way for large files would be to stream to a temp file or use a lib.

        potential_filepath = os.path.join(upload_folder, original_filename)
        file_url = None
        saved_new_file = False

        if os.path.exists(potential_filepath):
            # File with the same name exists, check size
            try:
                existing_file_size = os.path.getsize(potential_filepath)

                # Get size of the uploaded file. Read its content to determine the size.
                # This reads the entire file into memory to get its length.
                # For very large files, this might be an issue.
                uploaded_file_content = file.read()
                uploaded_file_size = len(uploaded_file_content)
                # Reset stream position so it can be read again by file.save() if needed
                file.seek(0)

                if existing_file_size == uploaded_file_size:
                    # Same name, same size - assume it's the same file
                    current_app.logger.info(f"Reusing existing file (same name and size): {original_filename}")
                    file_url = url_for('static', filename=f'media_files/{original_filename}', _external=True)
                else:
                    # Same name, different size - save with counter
                    current_app.logger.info(
                        f"File with name '{original_filename}' exists but different size. Saving new version.")
                    base, ext = os.path.splitext(original_filename)
                    counter = 1
                    new_filename = f"{base}_{counter}{ext}"
                    filepath_to_save = os.path.join(upload_folder, new_filename)
                    while os.path.exists(filepath_to_save):
                        counter += 1
                        new_filename = f"{base}_{counter}{ext}"
                        filepath_to_save = os.path.join(upload_folder, new_filename)

                    file.save(filepath_to_save)  # Save the new file with the new name
                    saved_new_file = True
                    current_app.logger.info(f"Saved new file as: {new_filename}")
                    file_url = url_for('static', filename=f'media_files/{new_filename}', _external=True)

            except Exception as e:
                current_app.logger.error(f"Error processing file {original_filename} or its existing counterpart: {e}")
                return jsonify({'error': 'Server error during file processing.'}), 500
        else:
            # File does not exist, save it with the original secure name
            try:
                file.save(potential_filepath)
                saved_new_file = True
                current_app.logger.info(f"Saved new file: {original_filename}")
                file_url = url_for('static', filename=f'media_files/{original_filename}', _external=True)
            except Exception as e:
                current_app.logger.error(f"Error saving new file {original_filename}: {e}")
                return jsonify({'error': 'Server error during file save.'}), 500

        if file_url:
            return jsonify({'url': file_url}), 200
        else:
            # This case should ideally not be reached if logic is correct
            return jsonify({'error': 'File processing failed for an unknown reason.'}), 500

    return jsonify({'error': 'File type not allowed.'}), 400
