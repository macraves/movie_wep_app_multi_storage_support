""" "Test User instance"""
from user.user_instance import User
from datamanagement.JSON_Data_Manager import JsonStorage as JS

userdata = {"name": "caner", "password": "12345"}
user = User(userdata)
user.userdata["storage"] = JS()
storage = user.userdata["storage"]
# uid = storage.user_unique_id()
# user.userdata = {uid: userdata}
# user.userdata[uid]["movie"] = "Batman"
# print(user.userdata)
# user_info = {
#     k: {k2: v2 for k2, v2 in v.items() if k2 != "storage"}
#     for k, v in user.userdata.items()
# }
# print(user_info)
# storage.add_new_user(user_info)
storage.add_movie_in_user_list({"1": {"name": "caner", "movie": "Batman"}})

# user.save_record()
# user_api = user.get_api()
# user_api.app.add_url_rule("/", view_func=user_api.index, methods=["GET"])
# user_api.app.run(debug=True)
