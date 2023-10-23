""" "Test User instance"""
from user.user_instance import User
from datamanagement.JSON_Data_Manager import JsonStorage as JS
from backend.request_movie import extract_movie_data


# movie = extract_movie_data("Batman")
# userdata = {"name": "caner", "password": "12345"}
user = User(
    {
        "name": "Mira",
        "password": "12345",
        "id": "2",
        "movie": {
            "Title": "Batman",
            "Director": "Tim Burton",
            "Year": "1989",
            "imdbRating": "7.5",
        },
    }
)
user.userdata["storage"] = JS()
# user.userdata["movie"] = movie
storage = user.userdata["storage"]
# user.get_id()
sample = {k: v for k, v in user.userdata.items() if k != "storage"}
# storage.add_movie_in_user_list(user.userdata)
storage.delete_movie_in_user_list(user.userdata, "2")

# print(sample)
# user_info = {
#     k: {k2: v2 for k2, v2 in v.items() if k2 != "storage"}
#     for k, v in user.userdata.items()
# }
# print(user_info)
# storage.add_new_user(user_info)
# storage.add_movie_in_user_list({"1": {"name": "caner", "movie": "Batman"}})

# user.save_record()
# user_api = user.get_api()
# user_api.app.add_url_rule("/", view_func=user_api.index, methods=["GET"])
# user_api.app.run(debug=True)
