"""flask-wtf forms for user and movie entries"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField
from wtforms.validators import DataRequired, Optional, EqualTo
from wtforms.widgets import TextArea

# Form class


class UserForm(FlaskForm):
    """WTFForm for user form"""

    name = StringField("Enter your name:", validators=[DataRequired()])
    username = StringField("Enter your username", validators=[DataRequired()])
    email = StringField("Email: (Optinal)", validators=[DataRequired()])
    storage = StringField(
        "(CSV-JSON-SQLITE) enter the stroage type", validators=[DataRequired()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Re-enter the password",
        validators=[DataRequired(), EqualTo("password", "Password has to be matched")],
    )
    submit = SubmitField("Submit")


class UserUpdateForm(FlaskForm):
    """WTFForm for user form"""

    name = StringField("Enter your name:", validators=[DataRequired()])
    username = StringField("Enter your username", validators=[DataRequired()])
    email = StringField("Email: (Optinal)", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MovieForm(FlaskForm):
    """WTFForm for movie form"""

    title = StringField("Enter the movie title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


class MovieUpdateForm(FlaskForm):
    """WTFForm for movie form"""

    title = StringField("Edit the movie title", validators=[Optional()])
    year = StringField("Edit the movie year", validators=[Optional()])
    rate = FloatField("Edit the movie rate", validators=[Optional()])
    submit = SubmitField("Update Movie")


class SigninForm(FlaskForm):
    """WTFForm for Signin form"""

    username = StringField("Enter your user name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    storage = StringField(
        "(CSV-JSON-SQLITE) enter the stroage type", validators=[DataRequired()]
    )
    submit = SubmitField("Sign In")


class ReviewForm(FlaskForm):
    """Form for review"""

    content = StringField("Review", validators=[Optional], widget=TextArea)
