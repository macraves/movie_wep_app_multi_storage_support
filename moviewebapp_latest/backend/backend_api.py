"""To able use backend user has to sign in to get access storage instance"""
from flask import Flask, jsonify, request
from flask_login import (
    LoginManager,
    login_required,
    login_manager,
    login_user,
    current_user,
)
from datamanagement.sqlite_data_manager import db
import frontend.forms_and_session_methods as ffasm
from backend.request_movie import extract_movie_data, RequestErrors
from frontend.movie_wtf import UserForm

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{ffasm.SQLITE_STORAGE_PATH}"

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "api_login"


def get_users(storage):
    """Returns Sqlite database users tables users records"""
    users = storage.get_all_users()
    if not isinstance(users, dict):
        users_dict = [user.to_dict() for user in users]
    return users_dict


@login_manager.user_loader
def load_user(user_id):
    """Gets flask sessin object user key to assing storage type"""
    storage_str = ffasm.session["user"].get("storage")
    storage = ffasm.get_storage_class(storage_text=storage_str)
    return storage.find_user(user_id=user_id)


@app.route("/api/login", methods=["POST"])
def api_login():
    """Endpoint to log in a user."""
    data = request.get_json()
    username = data.get("username").strip()
    password = data.get("password")
    storage_type = data.get("storage").strip()
    if storage_type != "sqlite":
        return jsonify({"error": "not supported storage type"})
    ffasm.session["user"] = {"username": username, "storage": storage_type}
    storage = ffasm.get_storage_class(storage_text=storage_type)
    user = storage.find_user(username=username)
    if not user:
        return jsonify({"error": "Invalid username"}), 401
    if not storage.check_password(user_id=user.id, password=password):
        return jsonify({"error": "Invalid password"}), 401
    login_user(user)
    return jsonify({"message": "Login successful"}), 200


@app.route("/api/user/add", methods=["POST"])
def api_add_user():
    """Endpoint to add new user"""
    data = request.get_json()
    storage = ffasm.get_storage_class(storage_text="sqlite")
    try:
        storage.add_new_user(data)
        return jsonify({"message": "User added successfuly"})
    except ffasm.IMPORTED_ERRORS as adding_error:
        return jsonify({"error": f"{str(adding_error)}"})


@app.route("/api/users", methods=["GET"])
@login_required
def api_list_users():
    """Display saved users in the related database."""
    _, storage = ffasm.get_user_and_storage()
    users_dict = get_users(storage)
    return jsonify(users_dict)


@app.route("/api/user-update/<int:user_id>", methods=["PUT"])
@login_required
def api_user_update(user_id):
    """Endpoint to user update."""
    _, storage = ffasm.get_user_and_storage()
    user = storage.find_user(user_id=user_id)
    if user is None:
        return jsonify({"warning": "User does not exitst"}), 404
    data = request.get_json()
    for key in data:
        if "password" in data and data.get(key, None) is not None:
            continue
        if "password" not in data:
            return jsonify({"warning": "Password not given"})
        else:
            setattr(user, key, data[key].strip())
    form = UserForm(obj=user)
    try:
        storage.update_user_info(user_id=user.id, form=form)
        return jsonify({"user": "user info updated successufully"})
    except ffasm.IMPORTED_ERRORS as update_user:
        return jsonify({"warning": f"{update_user}"}), 404


@app.route("/api/user-delete/<int:user_id>", methods=["DELETE"])
def api_user_delete(user_id):
    """Endpoint to delete user"""
    _, storage = ffasm.get_user_and_storage()
    user = storage.find_user(user_id=user_id)
    form = UserForm(obj=user)
    if user is None:
        return jsonify({"warning": "User does not exitst"}), 404
    storage.delete_user_info(user_id=user_id, form=form)
    users_dict = get_users(storage)
    return jsonify({"message": "User deleted successfuly", "users": users_dict})


@app.route("/api/users/<int:user_id>/movies", methods=["GET"])
@login_required
def api_user_movies(user_id):
    """Return a user's movie list."""
    _, storage = ffasm.get_user_and_storage()
    user = storage.find_user(user_id=user_id)
    if not user:
        return jsonify({"warning": "User does not exist"}), 404
    try:
        movies = storage.get_user_movies(user_id=user_id)
        movies_dict = [movie.to_dict() for movie in movies]
    except ffasm.IMPORTED_ERRORS as movie_err:
        return jsonify({"error": f"Movie ID is not valid: {movie_err}"}), 404
    return jsonify(movies_dict)


@app.route("/api/movies/add", methods=["POST"])
@login_required
def api_add_movie():
    """Add new movie info to the user's database."""
    userdata, storage = ffasm.get_user_and_storage()
    user = storage.find_user(username=userdata.get("username"))
    if not user or current_user.id != user.id:
        return jsonify({"error": "User does not exist"}), 400
    data = request.json
    title = data.get("title")
    try:
        movie = extract_movie_data(title)
    except RequestErrors as req_er:
        return jsonify({"error": f"Request error: {req_er}"}), 400

    userdata["movie"] = movie
    userdata["id"] = user.id
    registered, message = storage.add_movie_in_user_list(userdata)
    if not registered:
        return jsonify({"error": message}), 400
    return jsonify({"message": "New Movie Added Successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
