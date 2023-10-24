### Scenario

Application will be set on a `user` who will need to have _name_ and _password_ info to `sign in/sign` on the `application` (frontend) to have a list of movies and able to do CRUD operation on the list.

1. Application should support user requested `data management` for json and csv files.
2. Application should supports `Project Files Tree` structure.

# Data Management

The design structure will be defined as an abstract class to support file structures that may be requested later. Current supported structures is json file storage. So for further TODOs key version number added to:

```python
{
	"version": 1.0,
	"users": { "id": { "name": "username", "movies": {"id":"movie data"} } }
}
```

To avoid iterate through all data, data key pairs of management is more time efficient. ID gets its value from `max length of the dictionary + 1` . By default it creates logs directory and saves user and its favorite movies.

# Flask API

Backend method for API routes, current available functions are list users, user movies and add new user. Project itself more abut frontend so frontend will be completed first

# Frontend

Application Interface is the browser localhost, main runs Flask app `app.run(debug=True)` to get interacted with user. Functions creates default User instance, this istance gets its ID form Flask session object and uses User load_record to gets User name and password.

The interactions between the front-end and user parts were prioritized. Thus, any additions that may be required in the future can be taken from the user example.

# User Instances

Where the user gets checked and validated, instance will get user name, password,
and get its storage type by frontend app. The user's information will be stored in registry/regitry.json. Each new login will be compared with the information uploaded here, and those with the same username will be prevented.

User instance is a dictionary, rather than creating properties for every each request, dicitonary can store any further TODOs such, email, image, user info etc.
By default User gets name and password key by user then gets its unique ID from "users" key in movies.json, movies also gets their ID same way but these methods defined in storage class.
