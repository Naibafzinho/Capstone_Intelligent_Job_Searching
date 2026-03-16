from test_DB import DBManagement as UserDB
import pprint
from bson import ObjectId

db = UserDB()

#projection = {"lastName": 1, "email": 1, "resumes": 1, "_id": 0}
#users = db.fetch(projection=projection)
#pprint.pprint(users)

#db.insert_file()

#db.download_file()

test = db.insert_JobPosting_entry(Entry={
        "title": "Data Science Intern",
        "datePosted": "2024-03-10",
        "dateExtracted": "2024-03-10",
        "dateExpiring": "2024-03-31",
        "domain": "glassdoor.com",
        "company": "FinanceHub LLC",
        "locationC": ["Chicago, IL", "Remote"],
        "salaryRangeC": ["0-30K", "30K-60K"],
        "jobTypeC": ["intern"],
        "industryC": ["finance"],
        "experienceLevelC": ["entry-level"],
        "remoteC": ["hybrid"],
        "companySizeC": "501-1000",
        "text": "FinanceHub is seeking a Data Science Intern for a 3-month summer program...",
        "url": "https://glassdoor.com/jobs/view/345678",
        "keywords": ["Python", "Pandas", "SQL", "Machine Learning", "Excel"]
    })
pprint.pprint(test)

#db.update_user_value(flt={"username": None}, attribute="lastName", new_value="Smith")

db.close()