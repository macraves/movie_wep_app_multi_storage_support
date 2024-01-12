"""This module is used to store movies in a json file."""

import json
from werkzeug.security import check_password_hash
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI
from user.user_instance import User


class JsonStorageErrors(Exception):
    """JsonStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class JsonStorage(DMI):
    """Class for storing movies in a JSON file."""

    def __init__(self, filename) -> None:
        if not os.path.exists(DMI.logs_dir):
            os.makedirs(DMI.logs_dir)
        file_name = os.path.join(DMI.logs_dir, f"{filename}.json")
        if not os.path.exists(file_name):
            with open(file_name, "w", encoding="utf-8") as initiate:
                json.dump({"version": 1.0, "users": {}}, initiate, indent=4)
        self._filename = file_name

    def _read_file(self):
        """Reads data from the JSON file and returns a dictionary."""
        try:
            with open(self._filename, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        except json.decoder.JSONDecodeError as jdecoder:
            raise JsonStorageErrors(
                f"Error decoding json file {self._filename}:\n\t--> {jdecoder}"
            ) from jdecoder

    def _write_file(self, data):
        """Writes data to file expected structure is:
        {"version": version, "users": {id: {"user":user_object , "movies":{id:movie_}}}
        """
        with open(self._filename, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4)

    def check_password(self, user_id, password) -> bool:
        """First find user by name
        Calls User Instance to use its verify password method"""
        data = self._read_file().get("users")
        user = data.get(str(user_id), None)
        if user is not None:
            return check_password_hash(user.get("password"), password)
        return False

    def find_user(self, username: str = None, user_id: int = None) -> User | None:
        """Find user by either name or user ID info then
        extract a user form list of dictionaries by given name
        extract a user from dictionary by given user ID
        and returns user info as dict

        Args:
            userdata (dict): user information container with keys
            id, name, password, email(optional), storage values
        Returns:
            obj | None: user object
        """
        user_id = str(user_id) if user_id is not None else None
        users = self._read_file().get("users")
        user_list = self.get_all_users()
        if user_id is not None:
            user = users.get(user_id)
        elif username is not None:
            user = next(
                (user for user in user_list if user.get("username") == username),
                None,
            )
        else:
            user = None
        if user is not None:
            return User(userdata=user)
        return None

    def update_user_info(self, user_id, form: dict):
        """Update user info in saved JSON file"""
        userdata = {
            "name": form.name.data.title().strip(),
            "username": form.username.data.strip(),
            "email": form.email.data.strip(),
            "password": form.password.data.strip(),
        }
        if not self.check_password(user_id=user_id, password=userdata.get("password")):
            raise JsonStorageErrors("Invalid Password")
        # Getting userdata as user instance
        data = self._read_file()
        user = data["users"].get(str(user_id))
        user["name"] = userdata.get("name", userdata.get("name"))
        user["username"] = userdata.get("username", userdata.get("username"))
        user["email"] = userdata.get("email", userdata.get("email"))
        self._write_file(data)

    def delete_user_info(self, user_id, form):
        """Update user infor with OREM"""
        userdata = {"password": form.password.data.strip()}
        if not self.check_password(user_id=user_id, password=userdata["password"]):
            raise JsonStorageErrors("Invalid Password")
        data = self._read_file()
        del data["users"][str(user_id)]
        self._write_file(data)

    def get_all_users(self):
        """returns storage saved user records"""
        users = self._read_file().get("users", None)
        if users is None:
            users = []
        return list(users.values())

    def get_user_movies(self, user_id: int) -> list | None:
        """Get all movies for given user"""
        data = self._read_file()
        user = data["users"].get(str(user_id))
        if not user:
            raise JsonStorageErrors("User ID is not valid")
        return user.get("movies")

    def user_unique_id(self, username) -> int | Exception:
        """Iterate through users dictionary to find
        max key of movie and generate max + 1
        if name already exist raise JsonStorageErrors"""
        username = username.strip()
        data = self._read_file()
        users = data.get("users")
        for user in users.values():
            if username == user.get("username"):
                raise JsonStorageErrors(
                    "JsonStorage: User name is already in json movie database"
                )
        return max((int(key) for key in users.keys()), default=0) + 1

    def add_new_user(self, userdata: dict) -> None | JsonStorageErrors:
        """Creates a new user in users dictionary, checks if the name does exist"""
        try:
            user = User(userdata=userdata)
            user_with_id = user.save_record()
            user_id = user_with_id.get("id")
            userdata["id"] = user_id
            user.password = userdata.get("password")
            data = self._read_file()
            data["users"][str(user_id)] = {
                "id": userdata.get("id"),
                "name": userdata.get("name"),
                "username": userdata.get("username"),
                "email": userdata.get("email"),
                "password": user.password_hash,
                "movies": [],
            }
        except Exception as err:
            raise JsonStorageErrors(f"Adding new user error: {err}") from err
        self._write_file(data)

    def movie_unique_id(self, user_id) -> int:
        """Create ID for movie according length of list of movies"""
        users = self._read_file().get("users")
        movies = users.get(user_id).get("movies")
        return len(movies) + 1

    def add_movie_in_user_list(self, userdata) -> tuple[bool, str]:
        """Add a movie to a user's list."""
        data = self._read_file()
        user_id = str(userdata.get("id"))
        new_movie = userdata.get("movie")
        movie_id = self.movie_unique_id(user_id)
        new_movie["id"] = movie_id

        if user_id in data["users"]:
            data["users"][user_id]["movies"].append(new_movie)
            self._write_file(data)
            return True, "New Movie Added Successfully"
        return (
            False,
            "User ID is not valid to add new movie to the list.",
        )

    def get_target_movie(self, user_id: int, movie_id: int) -> dict | JsonStorageErrors:
        """Get the target movie from a user's list."""
        movies = self.get_user_movies(user_id)
        if not movies:
            return None
        target_movie = next(
            (movie for movie in movies if movie["id"] == movie_id), None
        )
        if not target_movie:
            return None
        return target_movie

    def update_movie_in_user_list(self, user_id, movie_id, form):
        """Update a movie from a user's list."""
        data = self._read_file()
        target_movie = self.get_target_movie(user_id, movie_id)
        movie_index = data["users"].get(str(user_id)).get("movies").index(target_movie)
        target_movie = {
            "Title": form.title.data.title().strip(),
            "Year": form.year.data,
            "imdbRating": form.rate.data,
        }
        data["users"].get(str(user_id)).get("movies")[movie_index].update(target_movie)
        self._write_file(data)

    def delete_movie_from_user_list(self, user_id: int, movie_id: int) -> str:
        """Delete a movie from a user's list."""
        data = self._read_file()
        target_movie = self.get_target_movie(user_id, movie_id)
        deleted_movie = data["users"][str(user_id)]["movies"].pop(
            data["users"][str(user_id)]["movies"].index(target_movie)
        )
        self._write_file(data)
        return f"{deleted_movie.get('Title')} deleted."
