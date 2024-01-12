"""Frontend html template rendering"""
from flask import abort, Flask, flash, render_template, redirect, request, url_for
from flask_migrate import Migrate
from flask_login import (
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from datamanagement.sqlite_data_manager import db
from backend.request_movie import extract_movie_data, RequestErrors
import frontend.forms_and_session_methods as ffasm
from frontend.movie_wtf import (
    UserForm,
    UserUpdateForm,
    MovieForm,
    MovieUpdateForm,
    SigninForm,
    ReviewForm,
)


app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{ffasm.SQLITE_STORAGE_PATH}"

db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

# Flask Login Set-Up
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"


def check_html_state(form):
    """prints if there is error(s) from given form field"""
    flash(f"Checking Current method {request.method}")
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                f"Error in field '{getattr(form, field).label.text}': {error}",
                "error",
            )


@login_manager.user_loader
def load_user(user_id):
    """Gets flask sessin object user key to assing storage type"""
    storage_str = ffasm.session["user"].get("storage")
    storage = ffasm.get_storage_class(storage_text=storage_str)
    return storage.find_user(user_id=user_id)


@app.route("/add_review/movie/<int:movie_id>", methods=["GET", "POST"])
def add_review(movie_id):
    """routes only accept if chosen storage SqliteStorage type"""
    storage_type = ffasm.session["user"].get("storage")
    user, storage = ffasm.get_user_and_storage()
    # to get User instance as db.Model
    user = storage.find_user(user_id=user.get("id"))
    # Only sqlite type storage can add review
    if storage_type != "sqlite":
        abort(404, description="Only sqlite type storage can add review")
    if user is None:
        abort(404, description="User ID is not recognized")
    if current_user.id != user.id:
        abort(404, description="Not authorized to access")
    movie = storage.get_target_movie(user_id=user.id, movie_id=movie_id)
    if not movie:
        abort(404, description="Invalid movie ID")
    form = ReviewForm()
    if form.validate_on_submit():
        storage.add_review(form, user, movie_id)
        flash("Form submitted")
        return redirect(f"/users/{user.id}/movies")
    return render_template("add_review.html", movie=movie, form=form)


@app.route("/all-reviews")
def all_reviews():
    """Display all record in reviews table"""
    _, storage = ffasm.get_user_and_storage()
    reviews = storage.all_revies()
    return render_template("all_reviews.html", reviews=reviews)


@app.route("/dashboard")
@login_required
def dashboard():
    """User Information view"""
    _, storage = ffasm.get_user_and_storage()
    movies = storage.get_user_movies(user_id=current_user.id)
    if movies is None:
        movies = []
    return render_template("dashboard.html", movies=movies)


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html", title="index")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Html page tester"""
    valid_storage_extensions = ["csv", "json", "sqlite"]
    form = UserForm()
    data = {}
    if form.validate_on_submit():
        data = ffasm.get_user_form_data(form)
        storage_str = data.get("storage")
        if storage_str not in valid_storage_extensions:
            flash("Invalid storage type, valid storage are csv, json, sqlite")
            return render_template(
                "signup.html", title="Re-enter", name=data.get("name", None), form=form
            )

        # Data Json serializable version saved
        storage = ffasm.get_storage_class(storage_text=storage_str)
        ffasm.assign_session_values(data)
        try:
            # Username uniqueness will be checked in add_new_user methods
            data["storage"] = storage
            storage.add_new_user(data)
            user = storage.find_user(username=data.get("username"))
            # Once user saved get its storage ID to session
            data["id"] = user.id
            ffasm.session["user"]["id"] = data["id"]  # addin user id in user of session
            return redirect(url_for("signin"))
        except ffasm.IMPORTED_ERRORS as import_er:
            return render_template("index.html", title="WARNING!", warning=import_er)
    return render_template(
        "signup.html", title="signup", name=data.get("name", None), form=form
    )


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Render the signin page."""
    form = SigninForm()
    if form.validate_on_submit():
        storage_str = form.storage.data.lower().strip()
        storage = ffasm.get_storage_class(storage_text=storage_str)
        user = storage.find_user(username=form.username.data.strip())
        if user is None:
            flash("Username or password not correct")
            return render_template("signin.html", title="Sign In", form=form)
        if not storage.check_password(user.id, form.password.data):
            flash("Either User name or password is incorrect...")
        else:
            login_user(user)
            save_to_session = {"id": user.id, "name": user.name, "storage": storage_str}
            ffasm.session["user"] = save_to_session
            return redirect(url_for("list_movies"))
    return render_template("signin.html", title="Sign In", form=form)


@app.route("/signout")
@login_required
def signout():
    """Sign out the user."""
    logout_user()
    ffasm.clean_session_keys()
    return redirect(url_for("index"))


@app.route("/movies")
@login_required
def list_movies():
    """Render the movies page."""
    userdata, storage = ffasm.get_user_and_storage()
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
@login_required
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
        userdata, storage = ffasm.get_user_and_storage()
        userdata["movie"] = movie
        registered, message = storage.add_movie_in_user_list(userdata)
        if not registered:
            return render_template("index.html", title="WARNING!", warning=message)
        return redirect(url_for("list_movies"))
    return render_template("add_movie.html", form=form, message=message)


@app.route("/users/<int:user_id>/movies")
@login_required
def user_movies(user_id):
    """Render a user's movie list."""
    _, storage = ffasm.get_user_and_storage()
    user = storage.find_user(user_id=user_id)
    if not user:
        return render_template(
            "index.html", title="WARNING!", warning="User does not exist"
        )
    try:
        movies = storage.get_user_movies(user_id=user_id)
    except ffasm.IMPORTED_ERRORS as movie_err:
        abort(404, description=f"Movie ID is not valid {movie_err}")
    return render_template("user_movies.html", user=user, movies=movies)


@app.route("/user-update/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_update(user_id):
    """Find user by given user_id to update its info"""
    _, storage = ffasm.get_user_and_storage()
    form = UserUpdateForm()
    user = storage.find_user(user_id=user_id)
    if user is None:
        abort(404, description="User does not exist")
    if form.validate_on_submit():
        try:
            storage.update_user_info(user_id=user_id, form=form)
            flash("User Info Updated Successfully")
            return redirect(url_for("dashboard"))
        except ffasm.IMPORTED_ERRORS as update_user:
            flash(str(update_user))
            abort(500, description="Storage update error")
    return render_template("user_update.html", form=form, user=user)


@app.route("/user-delete/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_delete(user_id):
    """Find user by given user_id to delete its info"""
    form = UserUpdateForm()
    _, storage = ffasm.get_user_and_storage()
    # Neccassary label taken from form so validate_on_submit would not work
    if request.method == "POST":
        try:
            storage.delete_user_info(user_id, form)
            flash("User account deleted successfully")
            return redirect(url_for("index"))
        except ffasm.IMPORTED_ERRORS as delete_er:
            flash(str(delete_er))
            abort(500, description="Storage delete error")
    return render_template("user_delete.html", form=form, user_id=user_id)


@app.route("/users")
@login_required
def list_users():
    """Render the users page."""
    user, storage = ffasm.get_user_and_storage()
    users = storage.get_all_users()
    return render_template("users.html", user=user, users=users)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
@login_required
def update_movie(user_id, movie_id):
    """Render the update movie page."""
    _, storage = ffasm.get_user_and_storage()
    movie = storage.get_target_movie(user_id, movie_id)
    form = MovieUpdateForm()
    if request.method == "POST":
        try:
            storage.update_movie_in_user_list(user_id, movie_id, form)
            return redirect(url_for("list_movies"))
        except ffasm.IMPORTED_ERRORS as error:
            return render_template("index.html", title="WARNING!", warning=error)
    return render_template("update_movie.html", movie=movie, form=form, user_id=user_id)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>")
@login_required
def delete_movie(user_id, movie_id):
    """Delete the selected movie from the user's list of favorite movies."""
    if current_user.id != user_id:
        return render_template(
            "index.html", title="WARNING!", warning="You are not allowed"
        )
    _, storage = ffasm.get_user_and_storage()
    try:
        message = storage.delete_movie_from_user_list(user_id, movie_id)
        flash(message)
        return redirect(url_for("list_movies"))
    except ffasm.IMPORTED_ERRORS as import_er:
        return render_template("index.html", title="WARNING!", warning=import_er)


@app.route("/user/<int:user_id>/movie/<int:movie_id>/info")
@login_required
def movie_info(user_id, movie_id):
    """Individual Movie Page"""
    _, storage = ffasm.get_user_and_storage()
    try:
        movie = storage.get_target_movie(user_id, movie_id)
    except ffasm.IMPORTED_ERRORS as user_er:
        abort(404, description=str(user_er))
    # sqlite storage throup up page_not_found error(404)
    if movie is None:
        abort(404, description="Movie does not exist")
    return render_template("movie_info.html", movie=movie, user_id=user_id)


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
