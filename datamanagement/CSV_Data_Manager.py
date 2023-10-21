"""This module is used to store movies in a json file."""
import csv
from data_manager_interface import DataManagmentInterface


class CsvStorageErrors(Exception):
    """CsvStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CsvStorage(DataManagmentInterface):
    """This class is used to store movies in a csv file."""

    def __init__(self, filename) -> None:
        self._filename = filename

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
                        {row["id"]: {"user": row["users"], "movies": "movies"}}
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
                writer.writerow(
                    {
                        "version": data["version"],
                        "id": key,
                        "users": data["users"][key].get("user"),
                        "movies": data["users"][key].get("movies"),
                    }
                )

    def get_all_users(self):
        data = self._read_file()
        users = data["users"]
        return users

    def get_user_movies(self, user_id):
        data = self._read_file()
        user = data["users"][user_id]
        return user["movies"]
