"""Sqlite table Models"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password = db.Column(db.String(50), nullable=False)
    # user have many movie in its list
    movies = db.relationship("Movie", backref="adder", lazy=True)
    # "Movie", backref="user", lazy=True

    def verify_password(self, password):
        """Verify user password"""
        return self.password == password

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

    def __repr__(self):
        """Model representation"""
        return f"name: {self.Title} username: {self.Year}"
