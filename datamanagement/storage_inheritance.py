"""Data managment interface"""
import os
from abc import ABC, abstractmethod


class DataManagmentInterface(ABC):
    """Main framework for data managment"""

    root_dir = os.path.dirname(os.path.dirname(__file__))
    logs_dir = os.path.join(root_dir, "logs")

    @abstractmethod
    def get_all_users(self):
        """Get all users from storage"""
        pass

    @abstractmethod
    def get_user_movies(self, userdata):
        """Get all movies for given user"""
        pass
