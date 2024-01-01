"""Frontend html template rendering"""
from flask import Flask, flash, render_template, request, session, redirect, url_for
from frontend.movie_wtf import UserForm
from datamanagement.json_data_manager import JsonStorage, JsonStorageErrors
from datamanagement.csv_data_manager import CsvStorage
from datamanagement.sqlite_data_manager import db, SqliteStorage
from user.user_instance import User, UserErrors
from backend.request_movie import extract_movie_data

FILE_NAME = "movies"
SQLITE_STORAGE = SqliteStorage(FILE_NAME)
SQLITE_STORAGE_PATH = SQLITE_STORAGE.filename

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{SQLITE_STORAGE_PATH}"

db.init_app(app)
with app.app_context():
    db.create_all()


class FrontendErrors(Exception):
    """Custom exception class for frontend errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def get_user_info(user_id, user):
    """provide user id name and storage information"""
    users_data = user.load_records()
    for name, info in users_data.items():
        if info["id"] == user_id:
            user.userdata["name"] = name
            user.userdata["password"] = info["password"]
            return user
    return None


def check_errors(form):
    """prints if there is error(s) from given form field"""
    flash(f"Current method: {request.method}")
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                f"Error in field '{getattr(form, field).label.text}': {error}",
                "error",
            )


def get_storage_class(storage_text, filename):
    """Assigns class name to storage varible"""

    if storage_text == "json":
        storage = JsonStorage(filename)
    elif storage_text == "sqlite":
        storage = SQLITE_STORAGE
    elif storage_text == "csv":
        storage = CsvStorage(filename)
    return storage


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html", title="index")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Render the signin page."""
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        storage_type = request.form["storage"]
        if storage_type.lower().strip() == "json":
            storage = None
        user = User({"name": name, "password": password, "storage": storage})
        if user.is_password_match():
            user_info = user.load_records()
            user_id = user_info[name]["id"]
            user.userdata["id"] = user_id
            users = storage.get_all_users()
            if not user_id in users:
                storage.add_new_user(user.userdata)
            session["user_id"] = user_id
            session["storage"] = storage_type
            return redirect(url_for("list_movies"))
    return render_template("signin.html")


def json_and_csv_user(data: dict, storage: object):
    """JSON and CSV file type integrate with User instance"""
    try:
        user = User(userdata=data)
        user_with_id = user.save_record()
        flash(f"User ID saved: {user_with_id['id']}")
        session["user_id"] = user_with_id["id"]
        storage.add_new_user(user.userdata)
    except (UserErrors, JsonStorageErrors) as usererror:
        return f"<h1>{usererror}</h1>"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Html page tester"""
    valid_storage_extensions = ["csv", "json", "sqlite"]
    form = UserForm()
    data = {}
    # Not all field of wtform are neccessary so request.method used
    if request.method == "POST":
        data["name"] = request.form.get("name")
        data["username"] = request.form.get("username")
        data["email"] = request.form.get("email")
        data["storage"] = request.form.get("storage").strip().lower()
        # storage field DataRequired:
        if data["storage"] not in valid_storage_extensions:
            flash("Invalid storage type, valid storage are csv, json, sqlite")
            return render_template(
                "test.html", title="test", name=data.get("name", None), form=form
            )
        data["storage"] = request.form.get("storage").strip().lower()
        session["storage"] = data["storage"]
        data["password"] = request.form.get("password")
        storage = get_storage_class(session["storage"], FILE_NAME)
        data["storage"] = storage
        # CSV and JSON managment uses user instance
        if session["storage"] in ["csv", "json"]:
            json_and_csv_user(data, storage)
        else:
            storage.add_new_user(data)
        flash(f"Storage type: {session['storage']}")
    return render_template(
        "signup.html", title="signup", name=data.get("name", None), form=form
    )


@app.route("/signout")
def signout():
    """Sign out the user."""
    session.pop("user_id", None)
    session.pop("storage", None)
    return redirect(url_for("index"))


@app.route("/movies")
def list_movies():
    """Render the movies page."""
    user_id = session.get("user_id")
    storage = session.get("storage")
    if storage.lower().strip() == "json":
        storage = None
    if not user_id and not storage:
        return redirect(url_for("signin"))
    user = User(
        {"id": user_id, "storage": storage, "name": "default", "password": "default"}
    )
    user = get_user_info(user_id, user)
    session["name"] = user.userdata["name"]
    movies = storage.get_user_movies(user.userdata)
    return render_template(
        "movies.html", movies=movies, signout_link=url_for("signout")
    )


@app.route("/movies/add", methods=["GET", "POST"])
def add_movie():
    """Render the add movie page."""
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        movie = extract_movie_data(movie_name)
        user_id = session.get("user_id", False)
        storage = session.get("storage", False)
        if not user_id and not storage:
            return redirect(url_for("signin"))
        if storage.lower().strip() == "json":
            storage = None
        user = User(
            {
                "id": user_id,
                "storage": storage,
                "name": "default",
                "password": "default",
            }
        )
        user = get_user_info(user_id, user)
        user.userdata["movie"] = movie
        storage.add_movie_in_user_list(user.userdata)
        return redirect(url_for("list_movies"))
    if not session.get("user_id"):
        return redirect(url_for("signin"))
    return render_template("add_movie.html")


@app.route("/users/<user_id>/update_movie/<movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    """Render the update movie page."""
    storage = session.get("storage")
    if storage is None:
        return redirect(url_for("signin"))
    if storage.lower().strip() == "json":
        storage = None
    user = User(
        {"id": user_id, "storage": storage, "name": "default", "password": "default"}
    )
    user = get_user_info(user_id, user)
    movie = storage.get_movie(user.userdata, movie_id)
    if request.method == "POST":
        movie["Title"] = request.form["title"]
        movie["Year"] = request.form["year"]
        movie["Director"] = request.form["director"]
        movie["imdbRating"] = request.form["imdbRating"]
        storage.update_movie_in_user_list(user.userdata, movie_id, movie)
        return redirect(url_for("list_movies"))
    return render_template("update_movie.html", movie=movie)


@app.route("/users/<user_id>/delete_movie/<movie_id>")
def delete_movie(user_id, movie_id):
    """Delete the selected movie from the user's list of favorite movies."""
    storage = session.get("storage")
    if storage is None:
        return redirect(url_for("signin"))
    if storage.lower().strip() == "json":
        storage = None
    user = User(
        {"id": user_id, "storage": storage, "name": "default", "password": "default"}
    )
    user = get_user_info(user_id, user)
    storage.delete_movie_from_user_list(user.userdata, movie_id)
    return redirect(url_for("list_movies"))


@app.route("/users")
def list_users():
    """Render the users page."""
    storage = session.get("storage")
    if storage is None:
        return redirect(url_for("signin"))
    if storage.lower().strip() == "json":
        storage = None
    users = storage.get_all_users()
    return render_template("users.html", users=users)


@app.route("/users/<user_id>/movies")
def user_movies(user_id):
    """Render a user's movie list."""
    storage = session.get("storage")
    if storage is None:
        return redirect(url_for("signin"))
    if storage.lower().strip() == "json":
        storage = None
    users = storage.get_all_users()

    user = users.get(user_id)
    if user is None:
        return "User not found"

    movies = user.get("movies", {})

    return render_template(
        "user_movies.html", user_name=user.get("name"), movies=movies, users=users
    )


if __name__ == "__main__":
    app.run(debug=True)
