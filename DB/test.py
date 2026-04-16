"""
from DB_Management import DBManagement as UserDB
import pprint
from bson import ObjectId

db = UserDB()

#projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}
#users = db.fetch(projection=projection)
#pprint.pprint(users)

#db.insert_file()

#db.download_file()

test = db.fetch(collection_name= "Resumes",filter={"filename": "resumeMatchTest.pdf"}, projection= {"_id": 0, "data": 1, "atsScore": 1})
pprint.pprint(test)

#db.update_user_value(flt={"username": None}, attribute="lastName", new_value="Smith")

db.close()
"""

import httpx

response = httpx.post("http://localhost:8000/updateValue", json={"collection_name": "Users", "flt": {"username": "Iannn"}, "attribute": "passwordHash", "new_value": "lolll"}, timeout=15)

print(response.json())
