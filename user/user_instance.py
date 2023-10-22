"""Creating User Instance, user info will be saved in registy folder
as json file.
from user folder to chdir to basename"""
import os
import json
from api.app import AppApi


class UserErrors(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class User:
    """Properties name, password and filepath
    it instance itself will be part of API instance"""

    root_dir = os.path.dirname(os.path.dirname(__file__))
    registry_dir = os.path.join(root_dir, "registry")
    registry_file = os.path.join(registry_dir, "registry.json")

    @staticmethod
    def is_valid_userdata(userdata: str):
        """Validate username"""
        password = str(userdata["password"])
        if userdata["name"].strip() == "" or password.strip() == "":
            raise UserErrors("User entry cannot be empty.")
        if not 4 < len(userdata["name"]) < 15:
            raise UserErrors("User entry must be between 4 and 15 characters long.")
        if not 4 < len(password) < 6:
            raise UserErrors("Password must be between 4 and 12 characters long.")
        if not password.isalnum():
            raise UserErrors("User entry must be alphanumeric.")
        return True

    def __init__(self, userdata):
        if self.is_valid_userdata(userdata):
            self.name = userdata["name"].strip()
            self.password = userdata["password"]

    def save_record(self):
        """Save username and password to registry file"""

        registration = {self.name: self.password}
        if not os.path.exists(self.registry_dir):
            os.makedirs(self.registry_dir)
        if (
            os.path.exists(self.registry_file)
            and os.path.getsize(self.registry_file) > 0
        ):
            users = self.load_records()
        else:
            users = {}
        if self.name in users:
            raise UserErrors("Username already exist.")
        users.update(registration)
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)

    def load_records(self):
        """Open username and password to registry file"""
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            return users
        except (FileNotFoundError, json.JSONDecodeError) as err:
            raise UserErrors(f"File not found.\n{err}") from err

    def is_password_match(self):
        """Check if password match"""
        users = self.load_records()
        if not self.name in users:
            return False
        if self.password != users[self.name]:
            return False
        return True

    def get_api(self):
        """Return API instance"""
        return AppApi(self)
