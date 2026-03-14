from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from bson import ObjectId
import os


class UserDB:
    """Simple wrapper around a MongoDB collection for user documents.

    Methods:
    - insert_user(user_doc): insert a user with full schema (missing fields set to None).
    - fetch_all(): return all documents (with stringified _id).
    - fetch(filter=None, projection=None): flexible fetch by filter and projection.
    - update(filter, updates): update one document using $set (validates resumes if present).
    - close(): close underlying client.
    """

    # Define required top-level user fields and resume schema
    USER_FIELDS = [
        "userId",
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
        "resumeId",
        "title",
        "uploadDate",
        "isActive",
        "tags",
        "extractedKeywords",
        "ATSscore",
    ]

    def __init__(self, uri: Optional[str] = None, db_name: str = "TestDB", collection_name: str = "User"):
        uri = os.getenv("MONGODB_URI")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.coll = self.db[collection_name]

    #turn ObjectId to string for JSON serialization
    def stringify_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def normalize_resume(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for f in self.RESUME_FIELDS:
            # keep lists as lists, others default to None
            res[f] = raw.get(f, None)
        return res

    def validate_and_fill_user(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Return a new user dict containing all required top-level fields.

        Missing fields are set to None. The `resumes` field is normalized to a list
        of resume objects (0..10) each containing all resume fields.
        """
        user = {}
        for f in self.USER_FIELDS:
            if f == "resumes":
                raw_resumes = raw.get("resumes") or []
                if not isinstance(raw_resumes, list):
                    raise ValueError("resumes must be a list")
                if len(raw_resumes) > 10:
                    raise ValueError("resumes cannot contain more than 10 items")
                user_resumes: List[Dict[str, Any]] = []
                for r in raw_resumes:
                    if not isinstance(r, dict):
                        raise ValueError("each resume must be a dict")
                    user_resumes.append(self._normalize_resume(r))
                user["resumes"] = user_resumes
            else:
                user[f] = raw.get(f, None)
        return user

    def insert_user(self, user_doc: Dict[str, Any]) -> str:
        """Insert a user document ensuring full schema. Returns inserted id as str."""
        validated = self._validate_and_fill_user(user_doc)
        result = self.coll.insert_one(validated)
        return str(result.inserted_id)

    def fetch_all(self) -> List[Dict[str, Any]]:
        docs = list(self.coll.find())
        return [self.stringify_id(d) for d in docs]

    def fetch(self, filter: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Fetch documents using an arbitrary filter and optional projection.

        Example: fetch({'userId': 'USR001'}, {'username': 1, 'email': 1})
        """
        flt = self.prepare_filter(filter)
        docs = list(self.coll.find(flt, projection))
        return [self.stringify_id(d) for d in docs]

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

    def update(self, filter: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update one document matched by `filter` with fields in `updates`.

        `updates` should be a plain dict of fields to set. If it contains a
        `resumes` key, the resumes list will be validated (<=10, proper structure).
        Returns a dict with matched_count and modified_count.
        """
        if not filter:
            raise ValueError("filter must be provided for update")
        flt = self._prepare_filter(filter)

        # If resumes provided, validate/normalize them before applying
        to_set = dict(updates)
        if "resumes" in to_set:
            normalized = []
            raw_resumes = to_set["resumes"] or []
            if not isinstance(raw_resumes, list):
                raise ValueError("resumes must be a list when updating")
            if len(raw_resumes) > 10:
                raise ValueError("resumes cannot contain more than 10 items")
            for r in raw_resumes:
                if not isinstance(r, dict):
                    raise ValueError("each resume must be a dict")
                normalized.append(self._normalize_resume(r))
            to_set["resumes"] = normalized

        result = self.coll.update_one(flt, {"$set": to_set})
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    def close(self) -> None:
        self.client.close()


if __name__ == "__main__":
    # Minimal usage example
    import pprint

    db = UserDB()
    pprint.pprint({"All documents": db.fetch_all()})
    db.close()