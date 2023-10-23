"""Backend for the web app."""
from flask import Flask, jsonify
from backend.user_app_methods import load_user_data


class ApiErrors(Exception):
    """Custom exceptions to point out errors in the API."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AppApi:
    """Prefer to set as instance. user object encapsulated its path,
    storage type and jsonify object can be modified  given user object"""

    def __init__(self, user):
        self.app = Flask(__name__)
        self.user = user

    def index(self):
        """user instance of user varible is used to get its movies list"""
        user_movies = load_user_data(self.user)
        return jsonify(user_movies)
