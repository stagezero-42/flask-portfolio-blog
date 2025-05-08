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


@admin.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html', title='Admin Dashboard')


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


# New route to handle Trix file uploads
@admin.route('/upload_trix_attachment', methods=['POST'])
@login_required
@csrf.exempt  # If you are using Flask-SeaSurf or similar global CSRF, you might need to exempt this for XHR
def upload_trix_attachment():
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure the upload folder exists (though we also do this in Config.init_app)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)

        # Avoid overwriting existing files by appending a number if necessary
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            counter += 1

        file.save(filepath)

        # Construct the URL for the saved file
        file_url = url_for('static', filename=f'media_files/{os.path.basename(filepath)}', _external=True)

        return jsonify({'url': file_url}), 200
    return jsonify({'error': 'Upload failed or file type not allowed'}), 400
