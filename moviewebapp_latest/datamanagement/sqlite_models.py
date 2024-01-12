"""Sqlite table Models"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """User model"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=False)
    # user have many movie in its list
    movies = db.relationship("Movie", backref="user", lazy=True, cascade="all,delete")
    reviews = db.relationship(
        "Review", backref="reviewer", lazy=True, cascade="all,delete"
    )

    @property
    def password(self):
        """Passward getter method, if it got called
        raises Attribute Exception"""
        raise AttributeError("Password is not callable attribute")

    @password.setter
    def password(self, password):
        """Password setter method to set password attribute"""
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Returns dict representation of instance"""
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
        }

    def __repr__(self):
        """Model representation"""
        return f"name: {self.name} username: {self.username}"


class Movie(db.Model):
    """Movie row properties"""

    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    # director = db.Column(db.String(200), nullable=False)
    Year = db.Column(db.String(100), nullable=True)
    imdbRating = db.Column(db.Float, nullable=True)
    Poster = db.Column(db.String(250), nullable=True)
    # Relationship with
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    reviews = db.relationship("Review", backref="view", lazy=True, cascade="all,delete")

    def to_dict(self):
        """Dictionary representation"""
        return {
            "id": self.id,
            "Title": self.Title,
            "Year": self.Year,
            "Rate": self.imdbRating,
        }

    def __repr__(self):
        """Model representation"""
        return f"name: {self.Title} username: {self.Year}"


class Review(db.Model):
    """Record table of user`s review"""

    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"))
    review_text = db.Column(db.Text)
