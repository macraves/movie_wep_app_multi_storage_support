"""Frontend html template rendering"""
from flask import Flask, flash, render_template, request, session, redirect, url_for
from flask_migrate import Migrate
from frontend.movie_wtf import UserForm, MovieForm, MovieUpdateForm, SigninForm
from datamanagement.json_data_manager import JsonStorage, JsonStorageErrors
from datamanagement.csv_data_manager import CsvStorage, CsvStorageErrors
from datamanagement.sqlite_data_manager import db, SqliteStorage, SqliteErrors

from backend.request_movie import extract_movie_data, RequestErrors

IMPORTED_ERRORS = (CsvStorageErrors, JsonStorageErrors, SqliteErrors)
FILE_NAME = "movies"
SQLITE_STORAGE = SqliteStorage(FILE_NAME)
SQLITE_STORAGE_PATH = SQLITE_STORAGE.filename

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{SQLITE_STORAGE_PATH}"

db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)


class FrontendError(Exception):
    """Custom exception class for frontend errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def clean_user_form(form):
    """WTFORM cleaner"""
    form.name.data = ""
    form.username.data = ""
    form.email.data = ""
    form.storage.data = ""
    form.password.data = ""


def clean_session_keys():
    """Previously assingend key deleted"""
    if "user" in session:
        del session["user"]
    if "storage" in session:
        del session["storage"]
    if "user_id" in session:
        del session["user_id"]


def check_errors(form):
    """prints if there is error(s) from given form field"""
    flash(f"Checking Current method {request.method}")
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                f"Error in field '{getattr(form, field).label.text}': {error}",
                "error",
            )


def get_storage_class(storage_text):
    """Assigns class name to storage varible"""
    storage_text = storage_text.lower().strip()
    if storage_text == "json":
        storage = JsonStorage(FILE_NAME)
    elif storage_text == "sqlite":
        storage = SQLITE_STORAGE
    elif storage_text == "csv":
        storage = CsvStorage(FILE_NAME)
    return storage


def get_user_and_storage():
    """Session object user and storage key values"""
    user = session.get("user")
    storage_text = session.get("user").get("storage")
    storage = get_storage_class(storage_text)
    return user, storage


def assign_session_values(data):
    """Creation session flask object values"""
    clean_session_keys()
    session["user"] = {
        "name": data.get("name"),
        "username": data.get("username"),
        "email": data.get("email"),
        "storage": data.get("storage"),
        "password": data.get("password"),
    }


def flash_session_properties():
    """Test purpose flash object where session details can be tracked"""
    user_id = session["user"].get("id")
    storage_type = session["user"].get("storage")
    name = session["user"].get("name")
    flash(
        f"Current Method {request.method}-> ID: {user_id} name: {name} storage: {storage_type}"
    )


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html", title=None, warning=None)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Html page tester"""
    if session.get("user", None) is not None:
        flash("Current user forced to sign out")
        return redirect("signout")
    valid_storage_extensions = ["csv", "json", "sqlite"]
    form = UserForm()
    data = {}
    # Not all field of wtform are neccessary so request.method used
    if form.validate_on_submit():
        name = form.name.data.strip().title()
        username = form.username.data.strip()
        email = form.email.data.strip()
        storage_str = form.storage.data.strip().lower()
        password = form.password.data.strip()
        # storage field DataRequired:
        if storage_str not in valid_storage_extensions:
            flash("Invalid storage type, valid storage are csv, json, sqlite")
            return render_template(
                "signup.html", title="Re-enter", name=data.get("name", None), form=form
            )
        data = {
            "name": name,
            "username": username,
            "email": email,
            "storage": storage_str,
            "password": password,
        }
        storage = get_storage_class(storage_text=storage_str)
        assign_session_values(data)
        try:
            # Data Json serializable version saved
            data["storage"] = storage
            storage.add_new_user(data)
            user = storage.find_user(name=data["name"])
            data["id"] = user.id
            session["user"]["id"] = data["id"]  # addin user id in user of session
            flash_session_properties()
            return redirect(url_for("signin"))
        except IMPORTED_ERRORS as import_er:
            return render_template("index.html", title="WARNING!", warning=import_er)
    check_errors(form=form)
    return render_template(
        "signup.html", title="signup", name=data.get("name", None), form=form
    )


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Render the signin page."""
    users = {}
    form = SigninForm()
    if form.validate_on_submit():
        if session.get("user", None) is not None:
            flash("Current user forced to sign out")
            return redirect("signout")
        storage_str = form.storage.data.lower().strip()
        storage = get_storage_class(storage_text=storage_str)
        users = storage.get_all_users()
        if not storage.check_password(form):
            flash("Either User name or password is incorrect...")
        else:
            user = storage.find_user(name=form.name.data.lower().strip())
            save_to_session = {"id": user.id, "name": user.name, "storage": storage_str}
            session["user"] = save_to_session
            flash_session_properties()
            return redirect(url_for("list_movies"))
    if session.get("user", None) is not None:
        flash_session_properties()
    return render_template("signin.html", title="Sign In", form=form, users=users)


@app.route("/signout")
def signout():
    """Sign out the user."""
    if session.get("user", None) is not None:
        clean_session_keys()
    return redirect(url_for("index"))


@app.route("/movies")
def list_movies():
    """Render the movies page."""
    userdata, storage = get_user_and_storage()
    if not userdata and not storage:
        return redirect(url_for("signin"))
    movies = storage.get_user_movies(userdata.get("id"))
    # flash_session_properties()
    return render_template(
        "movies.html",
        user_name=userdata.get("name"),
        movies=movies,
        user_id=userdata.get("id"),
    )


@app.route("/movies/add", methods=["GET", "POST"])
def add_movie():
    """Render the add movie page."""
    form = MovieForm()
    message = None
    if request.method == "POST":
        title = request.form["title"]
        try:
            movie = extract_movie_data(title)
        except RequestErrors as req_er:
            return render_template("index.html", title="WARNING!", warning=req_er)
        userdata, storage = get_user_and_storage()
        userdata["movie"] = movie
        registered, message = storage.add_movie_in_user_list(userdata)
        if not registered:
            return render_template("index.html", title="WARNING!", warning=message)
        return redirect(url_for("list_movies"))
    return render_template("add_movie.html", form=form, message=message)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    """Render the update movie page."""
    _, storage = get_user_and_storage()
    movie = storage.get_target_movie(user_id, movie_id)
    form = MovieUpdateForm()
    if request.method == "POST":
        try:
            storage.update_movie_in_user_list(user_id, movie_id, form)
            return redirect(url_for("list_movies"))
        except IMPORTED_ERRORS as error:
            return render_template("index.html", title="WARNING!", warning=error)
    return render_template("update_movie.html", movie=movie, form=form)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>")
def delete_movie(user_id, movie_id):
    """Delete the selected movie from the user's list of favorite movies."""
    _, storage = get_user_and_storage()
    try:
        message = storage.delete_movie_from_user_list(user_id, movie_id)
        flash(message)
        return redirect(url_for("list_movies"))
    except IMPORTED_ERRORS as import_er:
        return render_template("index.html", title="WARNING!", warning=import_er)


@app.route("/users")
def list_users():
    """Render the users page."""
    user, storage = get_user_and_storage()
    current_user = user.get("name")
    users = storage.get_all_users()
    flash_session_properties()
    return render_template("users.html", current_user=current_user, users=users)


@app.route("/users/<int:user_id>/movies")
def user_movies(user_id):
    """Render a user's movie list."""
    _, storage = get_user_and_storage()
    user = storage.find_user(user_id=user_id)
    if not user:
        return render_template(
            "index.html", title="WARNING!", warning="User does not exist"
        )
    movies = storage.get_user_movies(user_id=user_id)
    return render_template("user_movies.html", user=user, movies=movies)


# Custom Errors
@app.errorhandler(404)
def page_not_found(e):
    """Page not found error"""
    return render_template("index.html", title="404 Error", warning=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Page not found error"""
    return render_template("index.html", title="500 Error", warning=e), 500


if __name__ == "__main__":
    app.run(debug=True)
