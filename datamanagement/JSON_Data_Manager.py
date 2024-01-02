"""This module is used to store movies in a json file."""

import json
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI


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

    def find_user(self, name: str = None, user_id: int = None) -> dict | None:
        """Find user by either name or user ID info then
        extract a user form list of dictionaries by given name
        extract a user from dictionary by given user ID
        and returns user info as dict

        Args:
            userdata (dict): user information container with keys
            id, name, password, email(optional), storage values
        Returns:
            dict | None: {"id", "name", }
        """
        user = None
        users = self._read_file().get("users")
        user_list = self.get_all_users()
        if user_id:
            user = users.get(user_id)
        elif name:
            user = [user for user in user_list if user.get("name") == name]
        return user

    def get_all_users(self) -> list:
        """Get all users as a list from storage"""
        data = self._read_file()
        users = data.get("users", {}).values()
        return list(users)

    def get_user_movies(self, userdata: dict) -> list | None:
        """Get all movies for given user"""
        user_id = userdata.get("id")
        user = self.find_user(user_id=user_id)
        if not user:
            return None
        return user.get("movies")

    def user_unique_id(self, name) -> int | Exception:
        """Iterate through users dictionary to find
        max key of movie and generate max + 1
        if name already exist raise JsonStorageErrors"""
        name = name.strip().lower()
        data = self._read_file()
        users = data.get("users")
        for user in users.values():
            if name == user["name"]:
                raise JsonStorageErrors(
                    "JsonStorage: User name is already in json movie database"
                )
        return max((int(key) for key in users.keys()), default=0) + 1

    def add_new_user(self, userdata: dict) -> None | JsonStorageErrors:
        """Creates a new user in users dictionary"""
        data = self._read_file()
        user = self.find_user(user_id=userdata.get("id"))
        if user:
            raise JsonStorageErrors("JsonStorage: User already exists")
        data["users"][userdata.get("id")] = {
            "id": userdata.get("id"),
            "name": userdata.get("name"),
            "username": userdata.get("username"),
            "email": userdata.get("email"),
            "movies": [],
        }
        self._write_file(data)

    def add_movie_in_user_list(self, userdata) -> bool & str:
        """Add a movie to a user's list."""
        data = self._read_file()
        user_id = userdata.get("id")
        new_movie = userdata.get("movie")

        if user_id in data["users"]:
            data["users"][user_id]["movies"].append(new_movie)
            self._write_file(data)
            return True, "New Movie Added Successfully"
        return (
            False,
            "User ID is not valid to add new movie to the list.",
        )

    def get_target_movie(self, userdata, movie_id) -> dict | JsonStorageErrors:
        """Get the target movie from a user's list."""
        movies = self.get_user_movies(userdata=userdata)
        if not movies:
            raise JsonStorageErrors(
                "Either User or User`s movie list given ID is not valid"
            )
        target_movie = next(
            (movie for movie in movies if movie["id"] == movie_id), None
        )
        if not target_movie:
            raise JsonStorageErrors("Cannot find the movie by given Movie ID")
        return target_movie

    def update_movie_in_user_list(self, userdata, movie_id, movie):
        """Update a movie from a user's list."""
        data = self._read_file()
        target_movie = self.get_target_movie(userdata, movie_id)
        target_movie.update(movie)
        self._write_file(data)

    def delete_movie_from_user_list(self, userdata, movie_id) -> str:
        """Delete a movie from a user's list."""
        user_id = userdata.get("id")
        data = self._read_file()
        target_movie = self.get_target_movie(userdata, movie_id)
        deleted_movie = data["users"][user_id]["movies"].pop(
            data["users"][user_id]["movies"].index(target_movie)
        )
        self._write_file(data)
        return f"{deleted_movie.get('title')} deleted."
