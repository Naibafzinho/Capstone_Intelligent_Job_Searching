from DB_Management import DBManagement as UserDB
import pprint
from bson import ObjectId

db = UserDB()

#projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}
#users = db.fetch(projection=projection)
#pprint.pprint(users)

#db.insert_file()

#db.download_file()

test = db.add_matches(resumeId="69d18b202e2fd7551366436d", jobPostingId="69b75ce6190bf80afef9f0d3", matchScore=85, matchedKeywords=["python", "mongodb", "fastapi"])
pprint.pprint(test)

#db.update_user_value(flt={"username": None}, attribute="lastName", new_value="Smith")

db.close()