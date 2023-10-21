"""Backend for the web app."""
import flask


class ApiErrors(Exception):
    """Custom exceptions to point out errors in the API."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AppApi:
    """Further more needs to sport user object"""

    def __init__(self, user):
        self.app = flask.Flask(__name__)
        self.user = user

    def index(self):
        return f"Hello, {self.user}!"


def test_api():
    var = AppApi("caner")
    var.app.add_url_rule("/", view_func=var.index, methods=["GET"])
    var.app.run(debug=True)


# test_api()
