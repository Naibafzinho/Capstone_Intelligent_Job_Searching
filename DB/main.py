from test_DB import DBManagement as UserDB
import pprint

db = UserDB()

#projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}
#users = db.fetch(projection=projection)
#pprint.pprint(users)

#db.insert_file()

#db.download_file()

#test = db.insert_user({"userId": "USR002",})
#pprint.pprint(test)

db.update_user_value(flt={"username": None}, attribute="lastName", new_value="Smith")

db.close()