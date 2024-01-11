"""User instance where taken from html form"""

import os
import json
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

# Constants
REGISTRY_FILE = "registry.json"
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 100
MIN_PASSWORD_LENGTH = 3


class UserErrors(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class User(UserMixin):
    """Class for managing user registration and authentication."""

    root_dir = os.path.dirname(os.path.dirname(__file__))
    registry_dir = os.path.join(root_dir, "registry")
    registry_file = os.path.join(registry_dir, REGISTRY_FILE)

    def __init__(self, userdata: dict):
        """Initialize a User instance with userdata."""
        if self.is_valid_userdata(userdata):
            self.userdata = userdata
            self.id = userdata.get("id")
            self.name = userdata.get("name")
            self.username = userdata.get("username")
            self.email = userdata.get("email")
            self.storage = userdata.get("storage")

    # login user method questionaire get_id and is_active method

    @property
    def password(self):
        """Passward getter method, if it got called
        raises Attribute Exception"""
        raise AttributeError("Password is not callable attribute")

    @password.setter
    def password(self, password):
        """Password setter method to set password attribute"""
        self.password_hash = generate_password_hash(password=password)

    @staticmethod
    def is_valid_userdata(userdata: dict):
        """Validate user data."""
        name = userdata["name"]
        password = str(userdata["password"])

        if not MIN_USERNAME_LENGTH <= len(name) < MAX_USERNAME_LENGTH:
            raise UserErrors("Username must be between 3 and 15 characters long.")
        if MIN_PASSWORD_LENGTH > len(password):
            raise UserErrors("Password must be between 3 and 12 characters long.")
        if name.isdigit():
            raise UserErrors("Username must be alphabetical.")

        return True

    def save_record(self) -> dict:
        """Save username and password to the registry file."""

        if not os.path.exists(self.registry_dir):
            os.makedirs(self.registry_dir)

        if (
            os.path.exists(self.registry_file)
            and os.path.getsize(self.registry_file) > 0
        ):
            users = self.load_records()
        else:
            # registry.json not exists
            users = {}
            with open(self.registry_file, "w", encoding="utf-8") as handle:
                json.dump(users, handle, indent=4)
        # checking registry.json for unique name
        storage = self.userdata["storage"]
        user_id = self.assign_id(storage, self.userdata["username"])
        # save the user name and password in dictionary
        registration = {
            self.userdata["username"]: {
                "name": self.userdata["name"],
                "password": self.userdata["password"],
            }
        }
        registration[self.userdata["username"]]["id"] = user_id
        self.userdata["id"] = user_id
        users.update(registration)

        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        return self.userdata

    def load_records(self):
        """Load usernames and passwords from the registry file."""
        try:
            if not os.path.exists(self.registry_file):
                self.save_record()
            with open(self.registry_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            return users
        except (FileNotFoundError, json.JSONDecodeError) as err:
            raise UserErrors(f"File not found.\n{err}") from err

    def assign_id(self, storage, username):
        """Add an 'id' key to the userdata dictionary."""
        user_id = storage.user_unique_id(username)
        return user_id

    def frontend(self):
        """Return frontend instance."""
        print("Under construction")
