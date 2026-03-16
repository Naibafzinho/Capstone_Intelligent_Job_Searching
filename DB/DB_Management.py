from pymongo import MongoClient
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pydanticSchemes import UserScheme, ResumeScheme, JobPostingScheme
import bcrypt
import os

class DBManagement:

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client["TestDB"]

    def fetch(self, collection_name: str, filter: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Fetch documents using an arbitrary filter and optional projection.

        Example: fetch({'userId': 'USR001'}, {'username': 1, 'email': 1})
        """
        flt = self.prepare_filter(filter)
        coll = self.db[collection_name]
        docs = list(coll.find(flt, projection))
        return [self.stringify_id(d) for d in docs]

    def insert_entry(self, Entry: Dict[str, Any], collection_name: str) -> Optional[str]:
        """Insert a user document into the users collection.

        Ensures all fields listed in `UserScheme` exist on the document; missing
        fields are set to None. Prints upload success/failure to the terminal.

        Returns the inserted document id as a string on success, otherwise None.
        """
        
        if collection_name == "Resumes":
            userId = Entry.get("userId")
            if userId is None:
                print("Upload failed: userId is required for resume entries")
                return None
            try:
                #count how many resumes belong to the user with the given username
                docs = self.fetch(collection_name="Resumes", filter={"userId": userId})
            except Exception as e:
                print(f"Upload failed: {e}")
                return None
            if len(docs) >= 10:
                print(f"Upload failed: User with ID:{userId} already has 10 resumes")
                return None              

        if (collection_name == "Users"):
            #use username fetch to check for existing user with same username

            username = Entry.get("username")
            if username is None:
                print("Upload failed: username is required for user entries")
                return None
            existing_users = self.fetch(collection_name="Users", filter={"username": username})
            if existing_users is None:
                print("Upload failed: could not verify username uniqueness")
                return None
            if existing_users:
                print(f"Upload failed: User with username {username} already exists")
                return None
            #hash the password before validation and insertion
            password = Entry.get("passwordHash")
            if password is None:
                print("Upload failed: passwordHash is required for user entries")
                return None
            # hash the password and convert bytes to string
            Entry["passwordHash"] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  

        try:
            validated_Entry = self.get_Scheme(collection_name)(**Entry)
            doc = validated_Entry.model_dump()
        except Exception as e:
            print(f"Validation failed: {e}")
            return None

        try:
            coll = self.db[collection_name]
            res = coll.insert_one(doc)
            print(f"Upload successful: inserted_id={res.inserted_id}")
            return str(res.inserted_id)
        except Exception as e:
            print(f"Upload failed: {e}")
            return None        
    
    def update_value(self, flt: Dict[str, Any], attribute: str, new_value: Any, collection_name: str) -> int:
        """Update `attribute` to `new_value` for documents matching `flt` in the User collection.

        - `flt` should be a dict filter (same format accepted by `fetch`).
        Returns the number of modified documents (int). Prints success/failure to the terminal.
        """
        
        filter_prepared = self.prepare_filter(flt)

        if attribute == "passwordHash" and collection_name == "Users":
            # hash the new password and convert bytes to string
            new_value = bcrypt.hashpw(new_value.encode(), bcrypt.gensalt()).decode()

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
            coll = self.db[collection_name]
            res = coll.update_many(filter_prepared, {"$set": {attribute: new_value}})
            print(f"Update successful: matched={res.matched_count}, modified={res.modified_count}")
            return res.modified_count
        except Exception as e:
            print(f"Update failed: {e}")
            return 0
        
    def delete_entry(self, flt: Optional[Dict[str, Any]], collection_name: str) -> int:
        """Delete documents matching `flt` from `collection_name`.

        - `flt` may be None or a dict filter (same format accepted by `fetch`).
        Returns the number of deleted documents (int). Prints success/failure to the terminal.
        """

        if not flt:
            print("No filter provided, no documents deleted.")
            return 0

        filter_prepared = self.prepare_filter(flt)

        try:
            coll = self.db[collection_name]
            res = coll.delete_many(filter_prepared)
            print(f"Delete successful: deleted={res.deleted_count}")
            return res.deleted_count
        except Exception as e:
            print(f"Delete failed: {e}")
            return 0    

    def login_check(self, username: str, password: str) -> bool:
        """Check if a user with the given username and passwordHash exists in the Users collection.

        Returns True if a matching user is found, otherwise False. Prints success/failure to the terminal.
        """
        try:
            coll = self.db["Users"]
            user = coll.find_one({"username": username})
            stored_hash = user.get("passwordHash") if user else None
            if user and stored_hash and bcrypt.checkpw(password.encode(), stored_hash.encode()):
                print("Login successful")
                return True
            else:
                print("Login failed: invalid username or password")
                return False
        except Exception as e:
            print(f"Login check failed: {e}")
            return False

    def entry_exists(self, flt: Dict[str, Any], collection_name: str) -> Optional[int]:
        """Check if any document matching `flt` exists in `collection_name`.

        - `flt` should be a dict filter (same format accepted by `fetch`).
        Returns the amount of matches. Prints success/failure to the terminal.
        """

        filter_prepared = self.prepare_filter(flt)

        try:
            coll = self.db[collection_name]
            matches = coll.count_documents(filter_prepared)
            print(f"There are {matches} entries matching the filter in {collection_name}")
            return matches
        except Exception as e:
            print(f"Existence check failed: {e}")
            return None

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
        for key in ("_id", "userId"):
            if key in out and isinstance(out[key], str):
                try:
                    out[key] = ObjectId(out[key])
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