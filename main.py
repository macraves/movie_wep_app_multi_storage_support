""" "Test User instance"""
from user.user_instance import User
from datamanagement.JSON_Data_Manager import JsonStorage as JS
from backend.request_movie import extract_movie_data


def user_sample():
    """Dictionary for test"""
    userdata = {"id": "3", "name": "embieva", "password": "12345"}
    return userdata


def request_movie_data(movie_name):
    """execute api to get movie data and extracts its key"""
    extracted_info = extract_movie_data(movie_name)
    return extracted_info


def set_user_with_json_instance():
    """Repeative lines in func for test"""
    userdata = user_sample()
    user = User(userdata)
    user.userdata["storage"] = JS()
    return user


def add_user_in_json():
    """Test to check JS instance"""
    # Tested OK
    userdata = {"name": "embieva", "password": "12345"}
    user = User(userdata)
    user.userdata["storage"] = JS()
    user_storage = user.userdata["storage"]
    user.get_id(user_storage)
    user_storage.add_new_user(user.userdata)


def get_user_movies_from_json():
    """Test to check JS instance"""
    # Tested OK
    userdata = user_sample()
    user = User(userdata)
    user.userdata["storage"] = JS()
    user_storage = user.userdata["storage"]
    user_movies = user_storage.get_user_movies(user.userdata)
    print(user_movies)


def test_adding_movie_in_user_list():
    """Test to adding a new movie"""
    # Test OK
    movie = request_movie_data("friends")
    user = set_user_with_json_instance()
    user_storage = user.userdata["storage"]
    user.userdata["movie"] = movie
    user_storage.add_movie_in_user_list(user.userdata)


test_adding_movie_in_user_list()


def test_delete_movie_in_user_list():
    """testing Storage delete method
    params are self, userdata, movie_id"""
    # Test Ok
    movie_id = "3"
    user = set_user_with_json_instance()
    user_storage = user.userdata["storage"]
    user_storage.delete_movie_in_user_list(user.userdata, movie_id)
