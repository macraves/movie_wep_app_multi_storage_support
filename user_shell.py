"""Interactive User Interface for the shell."""
import os
import json
import shutil
from datamanagement import CSV_Data_Manager, JSON_Data_Manager


class UserErrors(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UserShell:
    """Where get Username and password and filepaht
    Planing to keep user info in users file"""

    folder_name = "registry"
    registry_path = os.path.join(os.path.dirname(__file__), folder_name)
    registry_dir = os.path.join(registry_path, "registry.json")

    @staticmethod
    def validate_entry(user_entry: str):
        """Validate username"""
        if user_entry.strip() == "":
            raise UserErrors("Username cannot be empty.")
        if len(user_entry) < 4:
            raise UserErrors("userentry must be at least 4 characters long.")
        if len(user_entry) > 20:
            raise UserErrors("userentry must be less than 20 characters long.")
        if not user_entry.isalnum():
            raise UserErrors("Username must be alphanumeric.")
        return True

    def __init__(self, user_data: dict):
        self.username = user_data["username"].title.strip()
        self.password = user_data["password"]

        @property
        def username(self):
            return self._username

        @username.setter
        def username(self, username):
            if self.validate_entry(username):
                self._username = username

        @property
        def password(self):
            return self._password

        @password.setter
        def password(self, password):
            if self.validate_entry(password):
                self._password = password

        def save_record(self):
            """Save username and password to registry file"""
            with open(UserShell.registry_path, "w", encoding="utf-8") as json_file:
                json.dump(
                    {"username": self.username, "password": self.password},
                    json_file,
                    indent=4,
                )

        def is_password_valid(self):
            """Checks registry file and compare username and password
            {"id": {"username": "user", "password": "pass", "filename":filename}}"""
            if not os.path.exists(UserShell.folder_path):
                os.makedirs(UserShell.folder_path)
            if not os.path.exists(UserShell.registry_dir):
                with open(UserShell.registry_dir, "w", encoding="utf-8") as json_file:
                    json.dump({}, json_file, indent=4)
