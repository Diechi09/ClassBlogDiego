from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')


class PostForm(FlaskForm):
    FLAIR_CHOICES = [
        ("TRADE_HELP", "TRADE HELP"),
        ("WAIVER_WIRE", "WAIVER WIRE ADVICE"),
        ("INJURY_TALK", "INJURY TALK"),
        ("OTHER", "OTHER"),
    ]
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    flair = SelectField('Flair', choices=FLAIR_CHOICES, validators=[DataRequired()], default="OTHER")
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Publish')


class CommentForm(FlaskForm):
    content = TextAreaField('Add a comment', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Comment')
