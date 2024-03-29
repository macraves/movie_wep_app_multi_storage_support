"""Backend for the web app."""
# import os
# import sys

# current_dir = os.path.dirname(os.path.abspath(__file__))
# # Add the project directory to the Python path
# project_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.append(project_dir)

from flask import Flask, jsonify, request
from datamanagement.JSON_Data_Manager import JsonStorage as JS
from user.user_instance import User, UserErrors

storage = JS()


app = Flask(__name__)


def create_user_instance(user_id):
    """Sample of user instance get its actual value by given ID
    In future planing to add storage key that gets value as text json or csv"""
    sample = {
        "nama": "sample",
        "password": "sample",
    }
    user = User(sample)
    exists_users = user.load_records()
    for name, info in exists_users.items():
        if info["id"] == user_id:
            user.userdata["name"] = name
            user.userdata["password"] = info["password"]
            return user
    return None


class BackendError(Exception):
    """Raise only Backend related errors"""

    def __init__(self, message: object) -> None:
        super().__init__(message)


@app.route("/users", methods=["GET"])
def list_users():
    """Loods user movies list"""
    users = storage.get_all_users()
    user_names = [users[user_id]["name"] for user_id in users]
    names_string = "\n".join(user_names)
    return jsonify(names_string)


@app.route("/users/<user_id>", methods=["GET"])
def user_movies(user_id):
    """Get methods with given query parameter"""
    user_id = str(user_id)
    users = storage.get_all_users()
    if user_id in users:
        return jsonify(users[user_id]["movies"])
    return jsonify({})


@app.route("/add_user", methods=["POST"])
def add_user():
    """Reads json base user POST to add new user"""
    try:
        given_request = request.get_json()
        request_data = {
            "name": given_request["name"],
            "password": given_request["password"],
            "storage": given_request["storage"],
        }
        user = User(request_data)
        users_data = user.load_records()
        if user.userdata["name"] in users_data:
            raise BackendError("User name already exists")
        user.get_id(user.userdata["storage"])
        user.save_record()
    except UserErrors as user_error:
        return jsonify({"User error": user_error}, 400)
    return jsonify(user)


if __name__ == "__main__":
    app.run(debug=True)
