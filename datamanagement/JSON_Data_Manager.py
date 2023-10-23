"""This module is used to store movies in a json file."""

import json
from storage_inheritance import os, DataManagmentInterface as DMI


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
        with open(self._filename, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4)

    def get_all_users(self):
        """Get all users from storage"""
        data = self._read_file()
        users = data["users"]
        return users

    def get_user_movies(self, user):
        """Get all movies for given user"""
        data = self._read_file()
        user_id = list(user.keys())[0]
        user = data["users"][user_id]
        return user["movies"]

    def user_unique_id(self):
        """Iterate through users dictionary to find
        max key of movie and generate max + 1"""
        data = self._read_file()
        users = data.get("users")
        if users and len(users) > 0:
            return max(int(key) for key in users.keys()) + 1
        return 1

    def add_new_user(self, user):
        """Creates a new user in users dictionary
        user ={id: name}"""
        data = self._read_file()
        user_id = list(user.keys())[0]
        data["users"][user_id] = {
            "name": user[user_id],
            "movies": {},
        }
        self._write_file(data=data)

    def find_user(self, userdata):
        """Finds user by userdata unique id"""
        data = self._read_file()
        user_id = list(userdata.keys())[0]
        return data["users"].get(user_id, False), user_id, data

    def add_movie_in_user_list(self, userdata):
        """Find user by its id and get the size of movies list if exists to assign
        unique key for movie user = {1: {'name': 'caner', 'movie': 'Batman'}}
        """
        user, data, user_id = self.find_user(userdata)
        if not user:
            raise JsonStorageErrors("Not able add movie: user does not exist")
        movies = user.get("movies")
        if movies and len(movies) > 0:
            mid = max(int(key) for key in movies) + 1
        else:
            mid = len(movies) + 1
        data["users"][user_id]["movies"][mid] = userdata[user_id]["movie"]
        self._write_file(data=data)

    def delete_movie_in_user_list(self, userdata):
        """Find user by its id and get the"""
        user, data, user_id = self.find_user(userdata)
        if not user:
            raise JsonStorageErrors("Not able to delete movie: user does not exist")
        movies = user.get("movies")
        if movies and len(movies) > 0:
            for k, v in movies:
                if v["Title"] == userdata[user_id["movie"]]:
                    del movies[k]
                    break
        data["users"][user_id["movies"]] = movies
        self._write_file(data)


def test_json_storage():
    """Create a user dictionary that gets its ID from user_id instance"""
    # user = {"name": "caner", "movie": "Batman"}
    user1 = {"1": {"name": "caner", "movie": "Batman"}}
    storage = JsonStorage()
    # user_id = storage.user_unique_id()
    # user = {user_id: user}
    # print(user)
    # user_info = {user_id: user[user_id]["name"]}
    # storage.add_new_user(user_info)
    # print(storage.get_all_users())
    # storage.add_movie_in_user_list(user1)
    # print(storage.get_user_movies(user1))
