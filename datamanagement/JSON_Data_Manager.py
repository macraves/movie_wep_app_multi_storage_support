"""This module is used to store movies in a json file."""

import json
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI


class JsonStorageErrors(Exception):
    """JsonStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class JsonStorage(DMI):
    """Class for storing movies in a JSON file."""

    def __init__(self) -> None:
        if not os.path.exists(DMI.logs_dir):
            os.makedirs(DMI.logs_dir)
        file_name = os.path.join(DMI.logs_dir, "movies.json")
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

    def find_user(self, userdata: dict):
        """Finds a user by their unique ID."""
        data = self._read_file()
        user_id = userdata["id"]
        return data["users"].get(user_id), user_id, data

    def get_all_users(self):
        """Get all users from storage"""
        data = self._read_file()
        users = data["users"]
        return users

    def get_user_movies(self, userdata):
        """Get all movies for given user"""
        data = self._read_file()
        return data["users"][userdata["id"]]["movies"]

    def user_unique_id(self):
        """Iterate through users dictionary to find
        max key of movie and generate max + 1"""
        data = self._read_file()
        users = data.get("users")
        if users and len(users) > 0:
            return max(int(key) for key in users.keys()) + 1

        return 1

    def add_new_user(self, userdata):
        """Creates a new user in users dictionary"""
        data = self._read_file()
        data["users"][userdata["id"]] = {
            "name": userdata.get("name"),
            "movies": {},
        }
        self._write_file(data)

    def add_movie_in_user_list(self, userdata):
        """Add a movie to a user's list."""
        user, user_id, data = self.find_user(userdata)
        movies = user.get("movies", {})
        mid = max([int(key) for key in movies], default=0) + 1
        data["users"][str(user_id)]["movies"][str(mid)] = userdata["movie"]
        self._write_file(data=data)

    def get_movie(self, userdata, movie_id):
        """Get a movie from a user's list."""
        user, user_id, data = self.find_user(userdata)
        movies = user.get("movies", {})
        if movie_id not in movies:
            raise JsonStorageErrors("Movie ID is not found to delete")
        return movies[movie_id]

    def update_movie_in_user_list(self, userdata, movie_id, movie):
        """Update a movie from a user's list."""
        user, user_id, data = self.find_user(userdata)
        movies = user.get("movies", {})
        if movie_id not in movies:
            raise JsonStorageErrors("Movie ID is not found to delete")
        movies[movie_id] = movie
        data["users"][user_id]["movies"] = movies
        self._write_file(data)

    def delete_movie_from_user_list(self, userdata, movie_id):
        """Delete a movie from a user's list."""
        user, user_id, data = self.find_user(userdata)
        movies = user.get("movies", {})
        if movie_id not in movies:
            raise JsonStorageErrors("Movie ID is not found to delete")
        del movies[movie_id]
        data["users"][user_id]["movies"] = movies
        self._write_file(data)
