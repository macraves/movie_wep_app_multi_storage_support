import os
import json

# Constants
REGISTRY_FILE = "registry.json"
MIN_USERNAME_LENGTH = 2
MAX_USERNAME_LENGTH = 15
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 12


class UserErrors(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class User:
    """Class for managing user registration and authentication."""

    root_dir = os.path.dirname(os.path.dirname(__file__))
    registry_dir = os.path.join(root_dir, "registry")
    registry_file = os.path.join(registry_dir, REGISTRY_FILE)

    def __init__(self, userdata: dict):
        """Initialize a User instance with userdata."""
        userdata = self.correct_userdata(userdata)
        if self.is_valid_userdata(userdata):
            self.userdata = userdata

    @staticmethod
    def is_valid_userdata(userdata: dict):
        """Validate user data."""
        name = userdata["name"].strip()
        password = str(userdata["password"]).strip()

        if not MIN_USERNAME_LENGTH < len(name) < MAX_USERNAME_LENGTH:
            raise UserErrors("Username must be between 4 and 15 characters long.")
        if not MIN_PASSWORD_LENGTH < len(password) < MAX_PASSWORD_LENGTH:
            raise UserErrors("Password must be between 4 and 12 characters long.")
        if not name.isalnum():
            raise UserErrors("Username must be alphanumeric.")

        return True

    @staticmethod
    def correct_userdata(userdata: dict):
        """Strip and normalize user data."""
        userdata["name"] = userdata["name"].strip()
        userdata["password"] = str(userdata["password"]).strip()
        return userdata

    def save_record(self):
        """Save username and password to the registry file."""
        registration = {self.userdata["name"]: {"password": self.userdata["password"]}}
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
            raise UserErrors("Username already exists.")

        user_id = self.get_id(self.userdata["storage"])
        registration[self.userdata["name"]]["id"] = user_id
        self.userdata["id"] = user_id
        users.update(registration)

        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        return "User successfully registered."

    def load_records(self):
        """Load usernames and passwords from the registry file."""
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            return users
        except (FileNotFoundError, json.JSONDecodeError) as err:
            raise UserErrors(f"File not found.\n{err}") from err

    def is_password_match(self):
        """Check if the entered password matches the stored password."""
        users = self.load_records()
        if not self.userdata["name"] in users:
            return False
        return self.userdata["password"] == users[self.userdata["name"]]["password"]

    def get_id(self, storage):
        """Add an 'id' key to the userdata dictionary."""
        user_id = storage.user_unique_id()
        return str(user_id)

    def frontend(self):
        """Return frontend instance."""
        print("Under construction")
