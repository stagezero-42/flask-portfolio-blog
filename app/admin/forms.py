from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, URL
from flask_wtf.file import FileField, FileAllowed # For file uploads

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=150)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Post')

class FooterIconForm(FlaskForm):
    name = StringField('Icon Name (e.g., Facebook)', validators=[DataRequired(), Length(min=1, max=100)])
    click_url = StringField('Click URL (Link)', validators=[DataRequired(), URL(), Length(max=500)])
    icon_file = FileField('Icon Image (PNG only, e.g., name_ico.png)', validators=[
        FileAllowed(['png'], 'PNG images only!')
    ]) # This field is for uploading new icons. Make it optional if editing and not changing the image.
    order = IntegerField('Display Order (e.g., 1, 2, 3...)', default=0)
    submit = SubmitField('Save Icon')

class CopyrightForm(FlaskForm):
    copyright_message = TextAreaField('Copyright Message', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Update Copyright')
