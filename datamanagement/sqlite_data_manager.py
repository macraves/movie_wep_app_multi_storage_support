"""Sqlite Storage Methods"""

from datamanagement.sqlite_models import db
from datamanagement.storage_inheritance import os, DataManagmentInterface as DMI
from datamanagement.sqlite_models import UserTable
from sqlalchemy import exc


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

    def find_user(self, user_id: int):
        """Query for SQL to find user by id"""
        user = db.query.get_or_404(user_id)
        return user

    def add_new_user(self, userdata: dict):
        """Adding new user to sqlite database"""
        user = UserTable(
            name=userdata.get("name"),
            username=userdata.get("username"),
            password=userdata.get("password"),
            email=userdata.get("email"),
        )
        try:
            db.session.add(user)
            db.session.commit()
        except exc.SQLAlchemyError as alchemy_er:
            raise SqliteErrors(
                f"Operation failed to add new user\n\
                {alchemy_er}"
            ) from alchemy_er

    def get_all_users(self):
        """Get all users from storage"""
        pass

    def get_user_movies(self, userdata):
        """Get all movies for given user"""
        pass
