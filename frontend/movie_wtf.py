"""flask-wtf forms for user and movie entries"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Optional, EqualTo

# Form class


class UserForm(FlaskForm):
    """User related"""

    name = StringField("Enter your name:", validators=[DataRequired()])
    username = StringField("Enter your username:", validators=[DataRequired()])
    email = StringField("Email:", validators=[Optional()])
    storage = StringField("(CSV-JSON-SQLITE) enter the stroage type")
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Re-enter the password",
        validators=[DataRequired(), EqualTo("password", "Password has to be matched")],
    )
    submit = SubmitField("Submit")
