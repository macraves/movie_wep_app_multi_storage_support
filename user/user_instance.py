"""Creating User Instance, user info will be saved in registy folder
as json file.
from user folder to chdir to basename"""
import os
import json
from backend.app import AppApi


class UserErrors(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class User:
    """Properties name, password be part of API instance"""

    root_dir = os.path.dirname(os.path.dirname(__file__))
    registry_dir = os.path.join(root_dir, "registry")
    registry_file = os.path.join(registry_dir, "registry.json")

    @staticmethod
    def is_valid_userdata(userdata: dict):
        """Validate username"""
        password = userdata["password"]
        if userdata["name"].strip() == "" or password.strip() == "":
            raise UserErrors("User entry cannot be empty.")
        if not 2 < len(userdata["name"]) < 15:
            raise UserErrors("User entry must be between 4 and 15 characters long.")
        if not 4 < len(password) < 6:
            raise UserErrors("Password must be between 4 and 12 characters long.")
        if not password.isalnum():
            raise UserErrors("User entry must be alphanumeric.")
        return True

    @staticmethod
    def correct_userdata(userdata: dict):
        """Correct userdata"""
        userdata["name"] = userdata["name"].strip()
        userdata["password"] = str(userdata["password"]).strip()
        return userdata

    def __init__(self, userdata: dict):
        """userdata = {"name": name, "password": password, "storage":"storage"}"""
        userdata = self.correct_userdata(userdata)
        if self.is_valid_userdata(userdata):
            self.userdata = userdata

    def save_record(self):
        """Save username and password to registry file"""

        registration = {self.userdata["name"]: self.userdata["password"]}
        if not os.path.exists(self.registry_dir):
            os.makedirs(self.registry_dir)
        if (
            os.path.exists(self.registry_file)
            and os.path.getsize(self.registry_file) > 0
        ):
            users = self.load_records()
        else:
            users = {}
        if self.userdata["name"] in users:
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
        if not self.userdata["name"] in users:
            return False
        if self.userdata["password"] != users[self.userdata["name"]]:
            return False
        return True

    def get_id(self):
        """Adds id key to userdata dict"""
        storage = self.userdata["storage"]
        user_id = storage.user_unique_id()
        self.userdata["id"] = str(user_id)

    def get_api(self):
        """Return API instance"""
        return AppApi(self)

    def frontend(self):
        """Return frontend instance"""
        print("Under the construction")
