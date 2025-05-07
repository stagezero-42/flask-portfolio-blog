from .extensions import db
from datetime import datetime

# Example User model (if you add authentication)
# class User(db.Model): # Add UserMixin from flask_login if using it
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), index=True, unique=True, nullable=False)
#     email = db.Column(db.String(120), index=True, unique=True, nullable=False)
#     password_hash = db.Column(db.String(256))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f'<User {self.username}>'

# Example Post model for blog
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Example relationship
#
#     def __repr__(self):
#         return f'<Post {self.title}>'