"""This module is used to store movies in a csv file.
Necessitiy to work with other database management forces to require CSV files to be separated 
user and movie attributes and use their relationship just like SQL database
So unlike other data management scripts, read user, read the movie, write user, 
and write movie methods are used and user ID would be the foreign key for 
those relationships"""


import csv
import pandas as pd
from werkzeug.security import check_password_hash


# from .storage_inheritance import os, DataManagmentInterface as DMI

from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI
from user.user_instance import User


class CsvStorageErrors(Exception):
    """CsvStorageErrors is a class for raising errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CsvStorage(DMI):
    """This class is used to store movies in a csv file."""

    def __init__(self, filename) -> None:
        if not os.path.exists(DMI.logs_dir):
            os.makedirs(DMI.logs_dir)
        user_file = os.path.join(DMI.logs_dir, "users.csv")
        self._user_file = user_file
        if not os.path.exists(user_file):
            self.initiate_user_file()
        movie_file = os.path.join(DMI.logs_dir, f"{filename}.csv")
        self._movie_file = movie_file
        if not os.path.exists(movie_file):
            self.initiate_movie_file()

    def get_user_id(self):
        """Reads csv file and return length + 1 value"""
        if os.path.getsize(self._user_file) > 0:
            df = pd.read_csv(self._user_file)
            length = df.shape[0]
            return str(length + 1)
        return 1  # If file is empty, return 1

    def initiate_user_file(self):
        """It writes default movies.csv file wirh its header"""
        with open(self._user_file, "w", encoding="utf-8") as initiated:
            fieldnames = ["id", "name", "username", "email", "password", "movies"]
            writer = csv.DictWriter(initiated, fieldnames=fieldnames)
            writer.writeheader()

    def initiate_movie_file(self):
        """It writes default movies.csv file wirh its header"""
        with open(self._movie_file, "w", encoding="utf-8") as initiated:
            fieldnames = ["id", "Title", "Year", "imdbRating", "Poster", "user_id"]
            writer = csv.DictWriter(initiated, fieldnames=fieldnames)
            writer.writeheader()

    def check_password(self, user_id, password) -> bool:
        """First find user by name
        Calls User Instance to use its verify password method"""
        data = self._read_user_file().get("users")
        user = data.get(str(user_id), None)
        if user is not None:
            return check_password_hash(user.get("password"), str(password))
        return False

    def _write_user_file(self, data, mode):
        """data either could be dictinoary then mode="a" initiated or is a list
        with mode="w". single user data to add in existed file is in form and dictionary,
        updated or changed info in users is in form of list of dictionaries
        """
        backup = self._read_user_file()
        try:
            with open(self._user_file, mode, encoding="utf-8", newline="") as csv_file:
                fieldnames = ["id", "name", "username", "email", "password", "movies"]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if csv_file.tell() == 0:
                    writer.writeheader()
                if mode == "a":
                    row = {
                        "id": data.get("id"),
                        "name": data.get("name").title().strip(),
                        "username": data.get("username").strip(),
                        "email": data.get("email").strip(),
                        "password": data.get("password").strip(),
                    }
                    writer.writerow(row)
                elif mode == "w":
                    writer.writerows(data)
        except Exception as write_user:
            self._write_user_file(backup, mode="w")
            raise CsvStorageErrors(
                f"CSV write user error: {write_user}"
            ) from write_user

    def _write_movie_file(self, data, mode):
        """Either add new movie (mode "a") in movies.csv or overwrite all CSV file with
        assigned new data witm (mode "w")"""
        try:
            with open(
                self._movie_file, mode, encoding="utf-8", newline=""
            ) as csv_write:
                fieldnames = ["id", "Title", "Year", "imdbRating", "Poster", "user_id"]
                writer = csv.DictWriter(csv_write, fieldnames=fieldnames)
                if csv_write.tell() == 0:
                    writer.writeheader()
                if mode == "a":
                    row = {
                        "id": data.get("id"),
                        "Title": data.get("Title"),
                        "Year": data.get("Year"),
                        "imdbRating": data.get("imdbRating"),
                        "Poster": data.get("Poster"),
                        "user_id": data.get("user_id"),
                    }
                    writer.writerow(row)
                else:
                    writer.writerows(data)
        except Exception as movie_write:
            raise CsvStorageErrors(f"Movie write error {movie_write}") from movie_write

    def _read_user_file(self):
        """
        {id, name, username, email, password}
        """
        try:
            with open(self._user_file, "r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                data = {"version": 1.0, "users": {}}
                for row in reader:
                    # Maybe it will get from movies coloumn, try and see
                    data["users"].update(
                        {
                            str(row["id"]): {
                                "id": row["id"],
                                "name": row["name"],
                                "username": row["username"],
                                "email": row["email"],
                                "password": row["password"],
                                "movies": row["movies"],
                            }
                        }
                    )
            return data
        except csv.Error as csv_error:
            raise CsvStorageErrors(
                f"Error decoding csv file {self._user_file}: {csv_error}"
            ) from csv_error

    def _read_movie_file(self) -> list:
        """Loop through movies.csv file to extract movie info in dictionary form
        and save them in list of dictionaries"""
        movies = []
        with open(self._movie_file, "r", encoding="utf-8") as read_csv:
            reader = csv.DictReader(read_csv)

            for row in reader:
                movie = {
                    "id": row["id"],
                    "Title": row["Title"],
                    "Year": row["Year"],
                    "imdbRating": row["imdbRating"],
                    "Poster": row["Poster"],
                    "user_id": row["user_id"],
                }
                movies.append(movie)
        return movies

    def add_movie_id_in_user_list(self, user_id):
        """Opens csv file find user by ID, checks type of movie column
        it is empty it gets None type then produces ID for movie writes movie ID in
        user movie list"""
        movies = self._read_movie_file()
        with open(self._user_file, "r", encoding="utf-8") as read_csv:
            reader = csv.DictReader(read_csv)
            data = []
            for row in reader:
                if row["id"] == user_id:
                    user_movies = row["movies"]
                    if user_movies == "":
                        user_movies = []
                    else:
                        user_movies = user_movies.split(",")
                    movie_id = str(len(movies) + 1)
                    user_movies.append(movie_id)
                    movies_id_line = (",").join(user_movies)
                    row["movies"] = movies_id_line
                data.append(row)
        # overwriting whole data mode="w"
        self._write_user_file(data=data, mode="w")
        return movie_id

    def get_user_movies(self, user_id: int) -> list | None:
        """Get all movies for given user"""
        user = self.find_user(user_id=str(user_id))
        if not user:
            raise CsvStorageErrors("User ID is not valid")
        movies = self._read_movie_file()
        user_movies = []
        for movie in movies:
            if movie.get("user_id") == str(user_id):
                user_movies.append(movie)
        return user_movies

    def add_movie_in_user_list(self, userdata):
        """Operates movies.csv file to create line of movi info: movie_id primary key
        and user_id foreign key to connect with users.csv"""
        movie = userdata.get("movie")
        user_id = str(userdata.get("id"))
        movie_id = self.add_movie_id_in_user_list(user_id=user_id)
        movie["id"] = movie_id
        movie["user_id"] = user_id
        try:
            self._write_movie_file(movie, mode="a")
            return True, "New Movie Added Successfully"
        except CsvStorageErrors as add_movie:
            return False, f"{add_movie}"

    def get_all_users(self) -> list:
        """Get all users as a list from storage"""
        data = self._read_user_file()
        users = data.get("users", {}).values()
        return list(users)

    def get_target_movie(self, user_id: int, movie_id: int) -> dict | None:
        """Get the target movie from a user's list."""
        movies = self.get_user_movies(str(user_id))
        if not movies:
            return None
        target_movie = next(
            (movie for movie in movies if movie["id"] == str(movie_id)), None
        )
        return target_movie

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
        users = self._read_user_file().get("users")
        user_list = self.get_all_users()
        if user_id is not None and len(users) > 0:
            user = users.get(user_id)
        elif username is not None and len(user_list) > 0:
            user = next(
                (user for user in user_list if user.get("username") == username),
                None,
            )
        else:
            user = None
        if user is not None:
            return User(user)
        return None

    def add_new_user(self, userdata: dict) -> None | CsvStorageErrors:
        """Creates a new user in users dictionary, checks if the name does exist"""
        try:
            user = self.find_user(username=userdata.get("username"))
            if user is not None:
                raise CsvStorageErrors("username exists, choose different one")
            user = User(userdata=userdata)
            user.password = userdata.get("password")
            user_id = self.get_user_id()
            userdata["id"] = user_id
            userdata["password"] = user.password_hash
        except Exception as err:
            raise CsvStorageErrors(f"Adding new user error: {err}") from err
        self._write_user_file(userdata, mode="a")

    def update_user_info(self, user_id, form: dict):
        """Update user info in saved JSON file"""
        userdata = {
            "name": form.name.data.title().strip(),
            "username": form.username.data.strip(),
            "email": form.email.data.strip(),
            "password": form.password.data.strip(),
        }
        if not self.check_password(user_id=user_id, password=userdata.get("password")):
            raise CsvStorageErrors("Invalid Password")
        # Getting userdata as user instance
        data = self._read_user_file()
        users = list(data["users"].values())
        updated_user_list = []
        for user in users:
            if user.get("id") == str(user_id):
                user["name"] = userdata.get("name")
                user["username"] = userdata.get("username")
                user["email"] = userdata.get("email")
            updated_user_list.append(user)
        self._write_user_file(updated_user_list, mode="w")

    def delete_user_info(self, user_id, form):
        """Update user in user.csv"""
        userdata = {"password": form.password.data.strip()}
        if not self.check_password(user_id=user_id, password=userdata["password"]):
            raise CsvStorageErrors("Invalid Password")
        data = self._read_user_file()
        users = list(data["users"].values())
        new_user_list = []
        for user in users:
            if user.get("id") != str(user_id):
                new_user_list.append(user)
        self._write_user_file(new_user_list, mode="w")

    def update_movie_in_user_list(self, _, movie_id, form):
        """Update a movie from a movies' list."""
        movies = self._read_movie_file()
        updated_movie_list = []
        for movie in movies:
            if str(movie_id) == movie.get("id"):
                movie["Title"] = form.title.data.title().strip()
                movie["Year"] = form.year.data.strip()
                movie["imdbRating"] = form.rate.data
            updated_movie_list.append(movie)
        self._write_movie_file(updated_movie_list, mode="w")

    def delete_movie_in_user_list(self, user_id: int, movie_id: int):
        """Delete movie ID from user movies columns"""
        data = self._read_user_file()
        users = list(data["users"].values())
        new_user_list = []
        for user in users:
            if str(user_id) == user.get("id"):
                user_movies = user.get("movies")
                if user_movies == "":
                    raise CsvStorageErrors("User movie list is empty")
                movie_list = user_movies.split(",")
                movie_index = movie_list.index(str(movie_id))
                movie_list.pop(movie_index)
                new_movie_line = (",").join(movie_list)
                user["movies"] = new_movie_line
            new_user_list.append(user)
        self._write_user_file(new_user_list, mode="w")

    def delete_movie_from_user_list(self, user_id: int, movie_id: int) -> str:
        """Delete a movie from a user's as its ID and also from movie list."""
        movies = self._read_movie_file()
        new_movie_list = []
        for movie in movies:
            if movie.get("id") != str(movie_id):
                new_movie_list.append(movie)
        self._write_movie_file(new_movie_list, mode="w")
        self.delete_movie_in_user_list(user_id, movie_id)
