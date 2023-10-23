""" "Test User instance"""
from user.user_instance import User
from datamanagement.JSON_Data_Manager import JsonStorage as JS

userdata = {"name": "caner", "password": "12345"}
user = User(userdata)
user.userdata["storage"] = JS()
storage = user.userdata["storage"]
uid = storage.user_unique_id()
user.userdata = {uid: userdata}


# user.save_record()
# user_api = user.get_api()
# user_api.app.add_url_rule("/", view_func=user_api.index, methods=["GET"])
# user_api.app.run(debug=True)
