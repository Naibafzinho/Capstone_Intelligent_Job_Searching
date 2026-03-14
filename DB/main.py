from user_db import UserDB
import pprint

db = UserDB()

projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}

users = db.fetch(projection=projection)

pprint.pprint(users)

db.close()