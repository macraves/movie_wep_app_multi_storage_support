"""This module is used to store movies in a json file."""

import json
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI


class JsonStorageErrors(Exception):
    """JsonStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class JsonStorage(DMI):
    """ "This class is used to store movies in a json file."""

    def __init__(self) -> None:
        file_name = os.path.join(DMI.logs_dir, "movies.json")
        self._filename = file_name

    def _read_file(self):
        """Reads data from file and returns dictionary of dictionaries"""
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

        if not os.path.exists(DMI.logs_dir):
            os.makedirs(DMI.logs_dir)
        if not os.path.exists(self._filename):
            with open(self._filename, "w", encoding="utf-8") as initiate:
                json.dump({"version": 1.0, "users": {}}, initiate, indent=4)
        with open(self._filename, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4)

    def find_user(self, userdata):
        """Finds user by userdata unique id"""
        data = self._read_file()
        user_id = userdata["id"]
        if data["users"][user_id]["name"] == userdata["name"]:
            return data["users"].get(user_id), user_id, data
        raise JsonStorageErrors("Cannot match id and user name")

    def get_all_users(self):
        """Get all users from storage"""
        data = self._read_file()
        users = data["users"]
        return users

    def get_user_movies(self, userdata):
        """Get all movies for given user"""
        user, user_id, data = self.find_user(userdata)
        if user:
            return data["users"][user_id]["movies"]
        raise JsonStorageErrors("User or list of movies does not exist")

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

        if userdata["id"] in data["users"]:
            raise JsonStorageErrors(
                f"User id does exist, cannot add this key {userdata['id']}"
            )
        data["users"][userdata["id"]] = {
            "name": userdata.get("name"),
            "movies": {"1": userdata.get("movie")},
        }
        self._write_file(data)

    def add_movie_in_user_list(self, userdata):
        """Find user by its id and get the size of movies list if exists to assign
        unique key for movie user = {1: {'name': 'caner', 'movie': 'Batman'}}
        """
        user, user_id, data = self.find_user(userdata)
        if not user:
            raise JsonStorageErrors("Not able add movie: user does not exist")
        movies = user.get("movies")
        if movies and len(movies) > 0:
            mid = max(int(key) for key in movies) + 1
        else:
            movies = {}
            mid = len(movies) + 1
        data["users"][str(user_id)]["movies"][mid] = userdata["movie"]
        self._write_file(data=data)

    def delete_movie_in_user_list(self, userdata, movie_id):
        """Find user by its id and get the"""
        user, user_id, data = self.find_user(userdata)
        if not user:
            raise JsonStorageErrors("Not able to delete movie: user does not exist")
        movies = user.get("movies")
        if movies and len(movies) > 0:
            if movie_id not in movies:
                raise JsonStorageErrors("Movie id is not found to delete")
            del movies[movie_id]
        data["users"][user_id]["movies"] = movies
        self._write_file(data)
