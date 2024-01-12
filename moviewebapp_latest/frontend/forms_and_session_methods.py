"""Form and Flask session object related methods gathered here"""
from flask import session

from datamanagement.json_data_manager import JsonStorage, JsonStorageErrors
from datamanagement.sqlite_data_manager import SqliteStorage, SqliteErrors
from datamanagement.csv_data_manager import CsvStorage, CsvStorageErrors
from user.user_instance import UserErrors

FILE_NAME = "movies"
SQLITE_STORAGE = SqliteStorage(FILE_NAME)
SQLITE_STORAGE_PATH = SQLITE_STORAGE.filename

IMPORTED_ERRORS = (CsvStorageErrors, JsonStorageErrors, SqliteErrors, UserErrors)


def clean_user_form(form):
    """WTFORM cleaner"""
    form.name.data = ""
    form.username.data = ""
    form.email.data = ""
    form.storage.data = ""
    form.password.data = ""


def clean_session_keys():
    """Previously assingend key deleted"""
    if "user" in session:
        del session["user"]
    if "storage" in session:
        del session["storage"]


def get_storage_class(storage_text):
    """Assigns class name to storage varible"""
    storage_text = storage_text.lower().strip()
    if storage_text == "json":
        storage = JsonStorage(FILE_NAME)
    elif storage_text == "sqlite":
        storage = SQLITE_STORAGE
    elif storage_text == "csv":
        storage = CsvStorage(FILE_NAME)
    return storage


def get_user_and_storage():
    """Session object user and storage key values"""
    user = session.get("user")
    if not user:
        return None, SQLITE_STORAGE
    storage_text = session.get("user").get("storage")
    storage = get_storage_class(storage_text)
    return user, storage


def assign_session_values(data):
    """Creation session flask object values"""
    clean_session_keys()
    session["user"] = {
        "name": data.get("name"),
        "username": data.get("username"),
        "email": data.get("email"),
        "storage": data.get("storage"),
    }


def get_user_form_data(form) -> dict:
    """UserForm object fields data get saved in a dictionary"""
    name = form.name.data.title().strip()
    username = form.username.data.strip()
    email = form.email.data.strip()
    storage_str = form.storage.data.strip().lower()
    password = form.password.data.strip()
    return {
        "name": name,
        "username": username,
        "email": email,
        "storage": storage_str,
        "password": password,
    }
