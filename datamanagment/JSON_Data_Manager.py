"""This module is used to store movies in a json file."""
import json
from data_manager_interface import DataManagmentInterface


class JsonStorageErrors(Exception):
    """JsonStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class JsonStorage(DataManagmentInterface):
    """ "This class is used to store movies in a json file."""

    def __init__(self, filename) -> None:
        self._filename = filename

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
        with open(self._filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

    def get_all_users(self):
        """Get all users from storage"""
        data = self._read_file()
        users = data["users"]
        return users

    def get_user_movies(self, user_id):
        """Get all movies for given user"""
        data = self._read_file()
        user = data["users"][user_id]
        return user["movies"]
