from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class CreateRegisterForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    email= StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    Submit = SubmitField('Add me')

# TODO: Create a LoginForm to login existing users
class CreateLoginForm(FlaskForm):
    email= StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    Submit = SubmitField('Let me in')

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    Submit = SubmitField('Submit comment')