"""Data managment interface"""
from abc import ABC, abstractmethod


class DataManagmentInterface(ABC):
    """Main framework for data managment"""

    @abstractmethod
    def get_all_users(self):
        """Get all users from storage"""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Get all movies for given user"""
        pass
