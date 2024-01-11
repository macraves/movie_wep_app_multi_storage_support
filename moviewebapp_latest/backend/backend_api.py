from flask import Flask, jsonify, request, abort
from flask_login import LoginManager, login_required, login_user
from datamanagement.sqlite_data_manager import db
import frontend.forms_and_session_methods as ffasm
from backend.request_movie import extract_movie_data, RequestErrors

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{ffasm.SQLITE_STORAGE_PATH}"

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"


@login_manager.user_loader
def load_user(user_id):
    """Endpoint to load user info to current_user instance"""
    storage_str = ffasm.session["user"].get("storage")
    storage = ffasm.get_storage_class(storage_text=storage_str)
    return storage.find_user(user_id=user_id)


@app.route("/api/login", methods=["POST"])
def api_login():
    """Endpoint to log in a user."""
    username = request.form.get("username").strip()
    password = request.form.get("password")
    storage_type = request.form.get("storage").strip()
    ffasm.session["user"] = {"username": username, "storage": storage_type}
    storage = ffasm.get_storage_class(request.form.get("storage").strip())
    user = storage.find_user(username=username)
    if not user:
        return jsonify({"error": "Invalid username"}), 401
    if not storage.check_password(user_id=user.id, password=password):
        return jsonify({"error": "Invalid password"}), 401

    # Flask-Login'in login_user fonksiyonunu kullanarak current_user'ı yükle
    login_user(user)

    return jsonify({"message": "Login successful"}), 200


@app.route("/api/users", methods=["GET"])
@login_required
def api_list_users():
    """API endpoint to display saved users in related database."""
    user, storage = ffasm.get_user_and_storage()
    users = storage.get_all_users()
    return jsonify({"user": user, "users": users})


@app.route("/api/users/<int:user_id>/movies", methods=["GET"])
@login_required
def api_user_movies(user_id):
    """API endpoint to render a user's movie list."""
    _, storage = ffasm.get_user_and_storage()
    user = storage.find_user(user_id=user_id)
    if not user:
        abort(404, description="User does not exist")

    try:
        movies = storage.get_user_movies(user_id=user_id)
    except ffasm.IMPORTED_ERRORS as movie_err:
        abort(404, description=f"Movie ID is not valid {movie_err}")

    return jsonify({"user": user, "movies": movies})


@app.route("/api/movies/add", methods=["POST"])
@login_required
def api_add_movie():
    """API endpoint to add new movie info in user's database."""
    form = MovieForm()
    message = None
    if request.method == "POST":
        title = request.form["title"]
        try:
            movie = extract_movie_data(title)
        except RequestErrors as req_er:
            return jsonify({"error": f"Error extracting movie data: {req_er}"}), 400

        userdata, storage = ffasm.get_user_and_storage()
        userdata["movie"] = movie
        registered, message = storage.add_movie_in_user_list(userdata)
        if not registered:
            return jsonify({"error": message}), 400
        return jsonify({"message": "New Movie Added Successfully"}), 200

    return render_template("add_movie.html", form=form, message=message)
