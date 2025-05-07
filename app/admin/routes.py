from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import admin # Import the blueprint
from .forms import LoginForm, PostForm
from app.models import User, Post
from app import db

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard')) # Or wherever you want logged-in admins to go
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username_or_email.data) | (User.email == form.username_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard')) # Redirect to dashboard or intended page
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    return render_template('admin/login.html', title='Admin Login', form=form)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index')) # Or admin.login

@admin.route('/dashboard') # A simple dashboard page
@login_required
def dashboard():
    return render_template('admin/dashboard.html', title='Admin Dashboard')

@admin.route('/add_post', methods=['GET', 'POST'])
@login_required # Protect this route
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        # Create new post
        new_post = Post(title=form.title.data, content=form.content.data)
        # If you have user linked to post:
        # new_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('main.blog')) # Redirect to the blog page to see the new post
    return render_template('admin/add_post.html', title='Add New Post', form=form)