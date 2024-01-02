"""Sqlite Storage Methods"""
from sqlalchemy import exc
from datamanagement.sqlite_models import db
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI
from datamanagement.sqlite_models import UserTable, MovieTable


class SqliteErrors(Exception):
    """Sqlite Error class"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class SqliteStorage(DMI):
    """Sqlite ORM properties and methods"""

    def __init__(self, filename) -> None:
        if not os.path.exists(DMI.logs_dir):
            os.makedirs(DMI.logs_dir)
        file_path = os.path.join(DMI.logs_dir, f"{filename}.db")
        self.filename = file_path

    def find_user(self, name: str = None, user_id: int = None) -> list | None:
        """Query for SQL to find user by id"""
        user = None
        if user_id:
            user = UserTable.query.get_or_404(
                user_id, description="User Does Not Exist"
            )
        elif name:
            user = UserTable.query.filter_by(name=name).first()
        return user

    def get_all_users(self) -> list:
        """ORM query to get the as list of dictionaries like object"""
        users = UserTable.query.order_by(UserTable.name).all()
        return users

    def get_user_movies(self, userdata) -> list | None:
        """Get all movies for given user"""
        user_id = userdata.get("id")
        user = UserTable.query.get(user_id)
        if user is None:
            return None
        movies = user.movies
        return movies

    def add_new_user(self, userdata: dict) -> None | SqliteErrors:
        """Adding new user to sqlite database"""
        user = UserTable(
            name=userdata.get("name"),
            username=userdata.get("username"),
            email=userdata.get("email"),
            password=userdata.get("password"),
        )
        try:
            db.session.add(user)
            db.session.commit()
        except exc.SQLAlchemyError as alchemy_er:
            raise SqliteErrors(
                f"SqliteErrors for adding new user\
                {alchemy_er}"
            ) from alchemy_er

    def add_movie_in_user_list(self, userdata) -> bool & str:
        """Add a movie to a user's list."""
        user_id = userdata.get("id")
        UserTable.query.get_or_404(user_id, description="User does not exist")
        new_movie = MovieTable(
            title=userdata.get("movie").get("title"),
            director=userdata.get("movie").get("director"),
            year=userdata.get("movie").get("year"),
            imdbRating=userdata.get("movie").get("imdbRating"),
            poster=userdata.get("movie").get("poster"),
            user_id=user_id,
        )
        try:
            db.session.add(new_movie)
            db.session.commit()
            return True, "New Movie Added Successfully"
        except exc.SQLAlchemyError:
            return False, "SqliteError: adding new movie to user list"

    def get_target_movie(self, userdata, movie_id) -> MovieTable | None:
        """Get a movie by given movie_id for a specific user"""
        user_id = userdata.get("id")
        target_movie = MovieTable.query.filter_by(
            user_id=user_id, id=movie_id
        ).first_or_404(description="Given Movie or User ID Invalid")
        # <class 'MovieTable'> or None
        return target_movie

    def update_movie_in_user_list(self, userdata, movie_id, movie):
        """Update a movie from a user's list."""
        movie_to_update = self.get_target_movie(userdata, movie_id)
        # if query did not throw 404 Error Update Movie Details
        movie_to_update.title = movie.get("title", movie_to_update.title)
        movie_to_update.director = movie.get("director", movie_to_update.director)
        movie_to_update.year = movie.get("year", movie_to_update.year)
        movie_to_update.imdbRating = movie.get("imdbRating", movie_to_update.imdbRating)
        movie_to_update.poster = movie.get("poster", movie_to_update.poster)
        db.session.commit()

    def delete_movie_from_user_list(self, userdata, movie_id) -> str:
        """Delete a movie from user`s list"""
        target_movie = self.get_target_movie(userdata, movie_id)
        movie_to_delete = target_movie
        db.session(movie_to_delete)
        db.session.commit()
        return f"{target_movie.title} deleted"
