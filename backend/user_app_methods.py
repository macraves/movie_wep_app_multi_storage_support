"""Methods for the app."""


def load_user_data(user):
    """user.userdata = {"id" , "name", "password", "storage"}"""
    # user = AppApi.user
    user_storage = user.userdata["storage"]
    user_movies = user_storage.get_user_movies(user.userdata)
    user_movies["name"] = f"Hello {user.userdata['name'].title().strip()}"
    return user_movies
