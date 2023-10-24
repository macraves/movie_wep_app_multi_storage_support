"""Frontend html template rendering"""
from flask import Flask, render_template, request, session, redirect, url_for
from datamanagement.JSON_Data_Manager import JsonStorage
from user.user_instance import User
from backend.request_movie import extract_movie_data

app = Flask(__name__)
app.secret_key = "mysecretkey"


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html")


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
        user.userdata["movie"] = movie
        storage.add_movie_in_user_list(user.userdata)
        return redirect(url_for("list_movies"))
    if not session.get("user_id"):
        return redirect(url_for("signin"))
    return render_template("add_movie.html")


if __name__ == "__main__":
    app.run(debug=True)
