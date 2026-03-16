from unittest import case

from pymongo import MongoClient
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pydanticSchemes import UserScheme, ResumeScheme, JobPostingScheme
import os

class DBManagement:

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client["TestDB"]

    def fetch(self, collection_name: str, filter: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Fetch documents using an arbitrary filter and optional projection.

        Example: fetch({'userId': 'USR001'}, {'username': 1, 'email': 1})
        """
        coll = self.db[collection_name]
        flt = self.prepare_filter(filter)
        docs = list(coll.find(flt, projection))
        return [self.stringify_id(d) for d in docs]
    
    def insert_entry(self, collection_name: str, Entry: Dict[str, Any]) -> Optional[str]:
        """Insert a user document into the users collection.

        Ensures all fields listed in `UserScheme` exist on the document; missing
        fields are set to None. Prints upload success/failure to the terminal.

        Returns the inserted document id as a string on success, otherwise None.
        """
        coll = self.db[collection_name]
        try:
            validated_Entry = self.get_Scheme(collection_name)(**Entry)
            doc = validated_Entry.model_dump()
        except Exception as e:
            print(f"Validation failed: {e}")
            return None

        try:
            res = coll.insert_one(doc)
            print(f"Upload successful: inserted_id={res.inserted_id}")
            return str(res.inserted_id)
        except Exception as e:
            print(f"Upload failed: {e}")
            return None
        
    def update_value(self, flt: Dict[str, Any], attribute: str, new_value: Any, collection_name: str = "User") -> int:
        """Update `attribute` to `new_value` for documents matching `flt` in the User collection.

        - `flt` should be a dict filter (same format accepted by `fetch`).
        Returns the number of modified documents (int). Prints success/failure to the terminal.
        """
        coll = self.db[collection_name]
        filter_prepared = self.prepare_filter(flt)

        try:
            validation = self.get_Scheme(collection_name)(**{attribute: new_value})  # validate the new value for the given attribute
            validated_dict = validation.model_dump(exclude_unset=True).items()  # get the validated attribute and value
            for attr, val in validated_dict:
                attribute = attr
                new_value = val
        except Exception as e:
            print(f"Validation failed: {e}")
            return 0
            
        try:
            res = coll.update_many(filter_prepared, {"$set": {attribute: new_value}})
            print(f"Update successful: matched={res.matched_count}, modified={res.modified_count}")
            return res.modified_count
        except Exception as e:
            print(f"Update failed: {e}")
            return 0
        
    """
    def lowercase_strings(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        '''Lowercase all string values in the document.'''
        for key, value in doc.items():
            if key.endswith("Config") | key.endswith("C"):
                doc[key] = value.lower() if isinstance(value, str) else value  
        return doc
    """
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
    
    def get_Scheme(self, collection_name: str):
        """Return the Pydantic scheme class corresponding to the collection name."""
        match collection_name:
            case "Users":
                return UserScheme
            case "Resumes":
                return ResumeScheme
            case "JobPostings":
                return JobPostingScheme
            case _:
                raise ValueError(f"No scheme defined for collection: {collection_name}")

    def close(self) -> None:
        self.client.close()