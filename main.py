""" "Test User instance"""
from user.user_instance import User
from datamanagement.JSON_Data_Manager import JsonStorage as JS
from backend.request_movie import extract_movie_data
from backend.user_app import 


def user_sample():
    """Dictionary for test"""
    userdata = {"id": "1", "name": "caner", "password": "12345"}
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
    movie = request_movie_data("The Matrix")
    user = set_user_with_json_instance()
    user_storage = user.userdata["storage"]
    user.userdata["movie"] = movie
    user_storage.add_movie_in_user_list(user.userdata)


def test_delete_movie_in_user_list():
    """testing Storage delete method
    params are self, userdata, movie_id"""
    # Test Ok
    movie_id = "3"
    user = set_user_with_json_instance()
    user_storage = user.userdata["storage"]
    user_storage.delete_movie_in_user_list(user.userdata, movie_id)



