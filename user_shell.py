"""Interactive User Interface for the shell."""
import os
import json
import shutil
from datamanagement import CSV_Data_Manager, JSON_Data_Manager


class ShellErrors(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UserShell:
    """Instance that connects with movies.json and movies.csv files."""

    def __init__(self, user):
        
