""" "Test User instance"""
from user.user_instance import User

userdata = {"name": "caner", "password": "12345"}
user = User(userdata)
user_api = user.get_api()
user_api.app.add_url_rule("/", view_func=user_api.index, methods=["GET"])
user_api.app.run(debug=True)
