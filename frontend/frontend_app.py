"""Frontend html template rendering"""
from flask import Flask, flash, render_template, request, session, redirect, url_for
from frontend.movie_wtf import UserForm
from datamanagement.json_data_manager import JsonStorage
from datamanagement.sqlite_models import db, MYSQL_URI
from user.user_instance import User
from backend.request_movie import extract_movie_data


app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = MYSQL_URI

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


@app.route("/test", methods=["GET", "POST"])
def test_page():
    """Html page tester"""
    form = UserForm()
    data = {}
    if form.validate_on_submit():
        data["name"] = form.name.data
        data["username"] = form.username.data
        data["email"] = form.email.data
        data["storage"] = form.storage.data
        data["password"] = form.password.data
        user = User(userdata=data)
        flash(f"{user.userdata.get('name')} submited successfuly")
    check_errors(form)
    return render_template(
        "test.html", title="test", name=data.get("name", None), form=form
    )


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
            storage = JsonStorage()
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


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Render the signup page."""
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        storage_type = request.form["storage"]
        if storage_type.lower().strip() == "json":
            storage = JsonStorage()
        user = User({"name": name, "password": password, "storage": storage})
        user.save_record()
        new_id = user.get_id(user.userdata["storage"])
        user.userdata["id"] = new_id
        session["user_id"] = new_id
        session["storage"] = storage_type
        storage.add_new_user(user.userdata)
        return redirect(url_for("signin"))
    return render_template("signup.html")


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
        storage = JsonStorage()
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
            storage = JsonStorage()
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
        storage = JsonStorage()
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
        storage = JsonStorage()
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
        storage = JsonStorage()
    users = storage.get_all_users()
    return render_template("users.html", users=users)


@app.route("/users/<user_id>/movies")
def user_movies(user_id):
    """Render a user's movie list."""
    storage = session.get("storage")
    if storage is None:
        return redirect(url_for("signin"))
    if storage.lower().strip() == "json":
        storage = JsonStorage()
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
