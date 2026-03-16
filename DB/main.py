from test_DB import DBManagement as UserDB
import pprint
from bson import ObjectId

db = UserDB()

#projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}
#users = db.fetch(projection=projection)
#pprint.pprint(users)

#db.insert_file()

#db.download_file()

test = db.insert_entry(collection_name="Users", Entry={"username": "testuser", "passwordHash": "hashedpassword123", "firstName": "Test", "lastName": "User", "email": "testuser@example.com", "phone": "123-456-7890", "locationConfig": ["New York", "San Francisco"], "expectedSalaryConfig": ["60K-100K", "100K-150K"], "jobTypeConfig": ["full-time"], "industryConfig": ["finance", "education", "tech", "retail"], "experienceLevelConfig": ["mid-level"], "remoteConfig": ["remote"], "companySizeConfig": ["51-200"]})
pprint.pprint(test)

#db.update_user_value(flt={"username": None}, attribute="lastName", new_value="Smith")

db.close()