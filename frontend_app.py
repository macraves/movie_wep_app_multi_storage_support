"""Frontend html template rendering"""
# import os
# import sys

# current_dir = os.path.dirname(os.path.abspath(__file__))
# # Add the project directory to the Python path
# project_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.append(project_dir)

from flask import Flask, render_template, request, redirect, url_for
from datamanagement.JSON_Data_Manager import JsonStorage
from user.user_instance import User

app = Flask(__name__)
storage = JsonStorage()


@app.route("/users")
def list_users():
    """Gets storage type list of users"""
    users = storage.get_all_users()
    return render_template("users.html", users=users)


@app.route("/users/<user_id>")
def user_movies(user_id):
    """Gets storage type list of users"""
    user_id = str(user_id)
    users = storage.get_all_users()
    if user_id in users:
        return render_template("movies.html", movies=users[user_id]["movies"])
    return render_template("movies.html", movies={})


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Adds a new user"""
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        storage = request.form["storage"]
        if storage == "json":
            storage = JsonStorage()
        user = User({"name": name, "password": password, "storage": storage})
        if not user.is_there_same_username():
            user.get_id(storage)
            user.save_record()
            storage.add_new_user(user.userdata)
        return redirect(url_for("list_users"))
    return render_template("add_user.html")


if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
