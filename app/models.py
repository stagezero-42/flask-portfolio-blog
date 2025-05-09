from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # Import UserMixin
from .extensions import login_manager # Assuming login_manager is initialized in extensions

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model): # Add UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # Changed from 128 to 256 for potentially longer hashes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add a relationship to posts if a user can have multiple posts
    # posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    # ... (existing fields)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    category = db.Column(db.String(50), nullable=False, default='blog', index=True)

    # New fields
    first_image_url = db.Column(db.String(255), nullable=True)  # To store URL of the first image in post
    thumbnail_url = db.Column(db.String(255), nullable=True)  # To store URL of the generated thumbnail

    # excerpt = db.Column(db.Text, nullable=True) # Optional: for a manually/auto-generated excerpt

    def __repr__(self):
        return f'<Post {self.title}>'

class FooterIcon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon_filename = db.Column(db.String(200), nullable=False) # e.g., 'facebook_ico.png'
    click_url = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0) # For ordering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FooterIcon {self.name}>'

    @property
    def icon_url(self):
        # Assuming your static folder for images is 'img' inside 'static'
        # and icons are in 'app/static/img/'
        from flask import url_for
        return url_for('static', filename=f'img/{self.icon_filename}')

class SiteConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'copyright_message'
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SiteConfiguration {self.key}>'

