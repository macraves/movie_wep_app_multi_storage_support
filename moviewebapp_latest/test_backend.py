"""testing backend.backend_api.py to run to this script flask app has to be run
then you can run this script"""
import types
from flask import Flask
from backend.request_movie import requests, extract_movie_data
from datamanagement.sqlite_data_manager import SqliteStorage

app = Flask(__name__)
session = requests.Session()
storage = SqliteStorage("movies")


def api_login_test():
    """Send request http://127.0.0.1:5000/api/login"""
    api_login = session.post(
        url="http://127.0.0.1:5000/api/login",
        timeout=5,
        json={"username": "admin", "password": "123", "storage": "sqlite"},
    ).json()
    print(api_login)


def api_list_users():
    """url='http://127.0.0.1:5000/api/users'"""
    api_login_test()
    response = session.get(url="http://127.0.0.1:5000/api/users")
    print(response.text)
    users = response.json()
    print(users)


def api_add_user():
    """url =http://127.0.0.1:5000/api/user/add"""
    api_login_test()
    new_user_data = {"name": "1.Tester", "username": "test", "password": "123"}
    response = session.post(
        url="http://127.0.0.1:5000/api/user/add", json=new_user_data
    )
    print(response.json())


def api_user_update():
    """Test url= http://127.0.0.1:5000/api/user-update/{}"""
    api_login_test()
    url = "http://127.0.0.1:5000/api/user-update/{}"
    user_id = int(input("Check users sqlite database and enter the ID: "))
    end_point = url.format(user_id)
    data = {"password": "123", "name": "1 updated", "username": "update"}
    response = session.put(url=end_point, json=data)
    print(response.json())


def api_user_delete():
    """User delete endpoint tester"""
    api_login_test()
    url = "http://127.0.0.1:5000/api/user-delete/{}"
    user_id = int(input("Check users sqlite database and enter the ID: "))
    end_point = url.format(user_id)
    data = {"password": "123"}
    response = session.delete(url=end_point, json=data)
    print(response.json())


def api_user_movies():
    """/api/users/<int:user_id>/movies", methods=["GET"]"""
    api_login_test()
    endpoint = "http://127.0.0.1:5000/api/users/1/movies"
    response = session.get(url=endpoint)
    print(response.text)
    print(response.json())


def api_add_movie():
    """Request movi data by name"""
    api_login_test()
    endpoint = "http://127.0.0.1:5000/api/movies/add"
    movie_name = input("Enter a movie name: ")
    movie_data = extract_movie_data(movie_name)
    response = session.post(url=endpoint, json=movie_data)
    print(response.json())


def main():
    """Run the test according user choice"""

    functions = [
        f
        for f in globals().values()
        if isinstance(f, types.FunctionType)
        and f.__name__.replace("_", " ") not in ["main", "extract movie data"]
    ]
    function_dict = dict(enumerate(functions, start=1))
    key_max = max(function_dict.keys())
    menu = ("\n").join(
        f"{k}: {v.__name__.replace('_',' ')}"
        for k, v in enumerate(function_dict.values(), start=1)
    )
    while True:
        try:
            command = int(
                input(
                    f"""{menu}
Any entry more than {key_max} or non number entry exit the app                            
Enter your command: """
                )
            )
            if command > key_max:
                break
            function_dict[command]()
        except ValueError:
            break


main()
