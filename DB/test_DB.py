from pymongo import MongoClient
from typing import Any, Dict, List, Optional
from bson import ObjectId
import os

class DBManagement:

    USER_FIELDS = [
        "username",
        "passwordHash",
        "locationConfig:",
        "expectedSalaryConfig",
        "jobTypeConfig",
        "industryConfig",
        "experienceLevelConfig",
        "remoteConfig",
        "companySizeConfig",
        "firstName",
        "lastName",
        "email",
        "phone",
        "dateRegistered",
        "lastLogin",
        "resumes",
    ]

    RESUME_FIELDS = [
        "filename",
        "userId",
        "data",
        "uploadDate",
        "isActive",
        "tags",
        "extractedKeywords",
        "ATSscore",
    ]

    JOB_POSTINGS_FIELDS = [
        "title",
        "datePosted",
        "dateExtracted",
        "dateExpiring",
        "domain",
        "company",
        "location",
        "salaryRange",
        "jobType",
        "industry",
        "experienceLevel",
        "remote",
        "companySize",
        "text",
        "url",
        "keywords"
    ]

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client["TestDB"]

    def fetch(self, collection_name: str, filter: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Fetch documents using an arbitrary filter and optional projection.

        Example: fetch({'userId': 'USR001'}, {'username': 1, 'email': 1})
        """
        self.coll = self.db[collection_name]
        flt = self.prepare_filter(filter)
        docs = list(self.coll.find(flt, projection))
        return [self.stringify_id(d) for d in docs]

    #turn ObjectId to string for JSON serialization
    def stringify_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    def prepare_filter(self, flt: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not flt:
            return {}
        # convert _id string to ObjectId if present
        out = dict(flt)
        if "_id" in out and isinstance(out["_id"], str):
            try:
                out["_id"] = ObjectId(out["_id"])
            except Exception:
                pass
        return out

    def close(self) -> None:
        self.client.close()

    def insert_user(self, user: Dict[str, Any]) -> Optional[str]:
        """Insert a user document into the users collection.

        Ensures all fields listed in `USER_FIELDS` exist on the document; missing
        fields are set to None. Prints upload success/failure to the terminal.

        Returns the inserted document id as a string on success, otherwise None.
        """
        coll = self.db["User"]
        doc = dict(user) if user is not None else {}

        for field in self.USER_FIELDS:
            if field not in doc:
                doc[field] = None
        
        for field in list(doc.keys()):
            print(f"Checking field: '{field}'")
            if field not in self.USER_FIELDS:
                print("popped")
                doc.pop(field)
                print(f"Warning:'{field}' not listed in USER_FIELDS and therefore deleted")

        try:
            res = coll.insert_one(doc)
            print(f"Upload successful: inserted_id={res.inserted_id}")
            return str(res.inserted_id)
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

    def update_user_value(self, flt: Dict[str, Any], attribute: str, new_value: Any, collection_name: str = "User") -> int:
        """Update `attribute` to `new_value` for documents matching `flt` in the User collection.

        - `flt` should be a dict filter (same format accepted by `fetch`).
        - `attribute` is the field name to set; a warning is printed if it's not in `USER_FIELDS`.
        Returns the number of modified documents (int). Prints success/failure to the terminal.
        """
        coll = self.db[collection_name]
        filter_prepared = self.prepare_filter(flt)

        if attribute not in self.USER_FIELDS:
            print(f"Warning: attribute '{attribute}' not listed in USER_FIELDS")

        try:
            res = coll.update_many(filter_prepared, {"$set": {attribute: new_value}})
            print(f"Update successful: matched={res.matched_count}, modified={res.modified_count}")
            return res.modified_count
        except Exception as e:
            print(f"Update failed: {e}")
            return 0