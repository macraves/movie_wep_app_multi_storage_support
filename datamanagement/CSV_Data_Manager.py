"""This module is used to store movies in a json file."""
import csv
import json  # for test
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI


class CsvStorageErrors(Exception):
    """CsvStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CsvStorage(DMI):
    """This class is used to store movies in a csv file."""

    def __init__(self, filename) -> None:
        if not os.path.exists(DMI.logs_dir):
            os.makedirs(DMI.logs_dir)
        file_name = os.path.join(DMI.logs_dir, f"{filename}.csv")
        if not os.path.exists(file_name):
            with open(file_name, "w", encoding="utf-8") as initiate:
                json.dump({"version": 1.0, "users": {}}, initiate, indent=4)
        self._filename = file_name

    def _read_file(self):
        """Reads data from file and returns dictionary of dictionaries
        {"version": version, "users": {id: {"user":user_object , "movies":{id:movie_}}}
        """
        try:
            with open(self._filename, "r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                data = {"users": {}}
                for row in reader:
                    # Maybe it will get from movies coloumn, try and see
                    data["version"] = row["version"]
                    data["users"].update(
                        {
                            row["id"]: {
                                "user": row["users"],
                                "movies": row["movies"].split(","),
                            }
                        }
                    )

            return data
        except csv.Error as csv_error:
            raise CsvStorageErrors(
                f"Error decoding csv file {self._filename}:\n\t--> {csv_error}"
            ) from csv_error

    def _write_file(self, data):
        """ "Writes data to file expected structure is:
        {"version": version, "users": {id: {"user":user_object , "movies":{id:movie_}}}
        """
        with open(self._filename, "w", encoding="utf-8") as csv_file:
            fieldnames = ["version", "id", "users", "movies"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for key in data["users"]:
                movies = data["users"][key]["movies"]
                movies_title = ",".join(movie.get("Title", "") for movie in movies)
                writer.writerow(
                    {
                        "version": data["version"],
                        "id": key,
                        "users": data["users"][key].get("user"),
                        "movies": movies_title,
                    }
                )

    def get_all_users(self):
        data = self._read_file()
        users = data["users"]
        return users

    def get_user_movies(self, userdata):
        data = self._read_file()
        user = data["users"][userdata]
        return user["movies"]

    def save_csv(self, data):
        """Write and save method for csv"""
        if not isinstance(data, dict):
            raise CsvStorageErrors("Unknown file type, json object expected")
        self._write_file(data)

    def load_csv(self):
        """Load csv file"""
        return self._read_file()
