"""Sqlite Storage Methods"""
from sqlalchemy import exc
from datamanagement.sqlite_models import db
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI
from datamanagement.sqlite_models import User, Movie, Review


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

    def check_password(self, user_id, password) -> bool:
        """First find user by name
        Calls User Instance to use its verify password method"""
        user = self.find_user(user_id=user_id)
        if user is None:
            return False
        return user.verify_password(password)

    def add_review(self, form, user, movie_id):
        """Uses ORM relationship to create Review instance"""
        content = form.content.data
        movie = self.get_target_movie(user_id=user.id, movie_id=movie_id)
        review = Review(user_id=movie.adder.id, movie_id=movie.id, review_text=content)

        db.session.add(review)
        db.session.commit()

    def all_revies(self):
        """Display all reviews for sqlite database"""
        revies = Review.query.order_by(Review.id).all()
        return revies

    def find_user(self, username: str = None, user_id: int = None) -> User | None:
        """Query for SQL to find user by id"""
        if user_id is not None:
            user = User.query.get(user_id)
            return user
        if username is not None:
            return User.query.filter_by(username=username).first()
        return None

    def update_user_info(self, user_id, form: dict):
        """Update user infor with OREM"""
        userdata = {
            "name": form.name.data.title().strip(),
            "username": form.username.data.strip(),
            "email": form.email.data.strip(),
            "password": form.password.data.strip(),
        }
        if not self.check_password(user_id=user_id, password=userdata.get("password")):
            raise SqliteErrors("Invalid Password")
        # Getting userdata as user instance
        user = self.find_user(user_id=user_id)
        user.name = userdata.get("name", user.name)
        user.username = userdata.get("username", user.username)
        user.email = userdata.get("email", user.email)
        try:
            db.session.commit()
        except Exception as exc_er:
            raise SqliteErrors(
                f"SQLite server closed or error occured {exc_er}"
            ) from exc_er

    def delete_user_info(self, user_id, form):
        """Update user infor with OREM"""
        userdata = {"password": form.password.data.strip()}
        if not self.check_password(user_id=user_id, password=userdata["password"]):
            raise SqliteErrors("Invalid Password")
        user = self.find_user(user_id=user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as exc_er:
            raise SqliteErrors(
                f"SQLite server closed or error occured {exc_er}"
            ) from exc_er

    def get_all_users(self) -> list:
        """ORM query to get the as list of dictionaries like object"""
        users = User.query.order_by(User.name).all()
        return users

    def get_user_movies(self, user_id) -> list | None:
        """Get all movies for given user"""
        user = User.query.get(user_id)
        if user is None:
            return None
        movies = user.movies
        return movies

    def add_new_user(self, userdata: dict) -> None | SqliteErrors:
        """Adding new user to sqlite database"""
        user = User(
            name=userdata.get("name"),
            username=userdata.get("username"),
            email=userdata.get("email"),
            password=userdata.get("password"),
        )
        try:
            # If user exists
            if self.find_user(username=user.username):
                raise SqliteErrors("sqlite3.IntegrityError: User name already existed")
            db.session.add(user)
            db.session.commit()
        except exc.SQLAlchemyError as alchemy_er:
            raise SqliteErrors(
                f"SqliteErrors for adding new user\n\
                {alchemy_er}"
            ) from alchemy_er

    def add_movie_in_user_list(self, userdata) -> tuple[bool, str]:
        """Add a movie to a user's list."""
        user_id = userdata.get("id")
        user = self.find_user(user_id=user_id)
        if not user:
            return False, "User does not exist"
        new_movie = Movie(
            Title=userdata.get("movie").get("Title"),
            Year=userdata.get("movie").get("Year"),
            imdbRating=userdata.get("movie").get("imdbRating"),
            Poster=userdata.get("movie").get("Poster"),
            user_id=user_id,
        )
        try:
            db.session.add(new_movie)
            db.session.commit()
            return True, "New Movie Added Successfully"
        except exc.SQLAlchemyError:
            return False, "SqliteError: adding new movie to user list"

    def get_target_movie(self, user_id, movie_id) -> Movie | None:
        """Get a movie by given movie_id for a specific user"""
        target_movie = Movie.query.filter_by(user_id=user_id, id=movie_id).first_or_404(
            description="Given Movie or User ID Invalid"
        )
        # <class 'Movie'> or None

        return target_movie

    def update_movie_in_user_list(self, user_id, movie_id, form):
        """Update a movie from a user's list."""
        try:
            movie_to_update = self.get_target_movie(user_id, movie_id)
            # if query did not throw 404 Error Update Movie Details
            movie_to_update.Title = form.title.data.title()
            movie_to_update.Year = form.year.data
            movie_to_update.imdbRating = form.rate.data
            db.session.commit()
        except Exception as update_er:
            raise SqliteErrors(f"SQLITE Update Error {update_er}") from update_er

    def delete_movie_from_user_list(self, user_id, movie_id) -> str:
        """Delete a movie from user`s list"""
        target_movie = self.get_target_movie(user_id, movie_id)
        movie_to_delete = target_movie
        try:
            db.session.delete(movie_to_delete)
            db.session.commit()
            return f"{target_movie.Title} deleted"
        except Exception as delete_er:
            raise SqliteErrors(f"SQLITE Delete Error {delete_er}") from delete_er
