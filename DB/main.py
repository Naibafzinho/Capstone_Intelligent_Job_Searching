from DB_Management import DBManagement as UserDB
import pprint
from bson import ObjectId

db = UserDB()

#projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}
#users = db.fetch(projection=projection)
#pprint.pprint(users)

#db.insert_file()

#db.download_file()

test = db.insert_entry(Entry={
        "username": "Timmy_dev",
        "passwordHash": "$2b$12$MQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5BIDO",
        "locationConfig": ["Chicago, IL"],
        "expectedSalaryConfig": ["30K-60K", "60K-100K"],
        "jobTypeConfig": ["PART-time", "intern", "contract"],
        "industryConfig": ["education", "tech"],
        "experienceLevelConfig": ["entry-level", "mid-level"],
        "remoteConfig": ["on-site", "hybrid"],
        "companySizeConfig": ["201-500", "501-1000"],
        "firstName": "Marcos",
        "lastName": "Rivera",
        "email": "marcos.dev@gmail.com",
        "phone": "555-456-7890"
    }, collection_name="Users")
pprint.pprint(test)

#db.update_user_value(flt={"username": None}, attribute="lastName", new_value="Smith")

db.close()