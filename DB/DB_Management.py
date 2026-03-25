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
        """
        Retrieves documents from a specified collection, with optional filtering and field projection.
        Returns a list of matched documents with ObjectId fields converted to strings.

        Example:
            # Fetch only the username and email of a specific user
            db.fetch(
                collection_name="Users",
                filter={"username": "john_doe"},
                projection={"username": 1, "email": 1}
            )
        # Returns: [{"_id": "abc123", "username": "john_doe", "email": "john@example.com"}]
        """
        flt = self.prepare_filter(filter)
        coll = self.db[collection_name]
        docs = list(coll.find(flt, projection))
        return [self.stringify_id(d) for d in docs]

    def insert_entry(self, Entry: Dict[str, Any], collection_name: str) -> Optional[str]:
        """
        Inserts a new document into the specified collection after validating it against
        the collection's Pydantic scheme. Returns the inserted document's ID as a string
        on success, or None on failure.

        Special handling per collection:
            - "Users":    Rejects duplicate usernames. Automatically hashes the plaintext
                        password provided under the "passwordHash" key before insertion.
            - "Resumes":  Rejects insertion if the associated user already has 10 resumes.

        Example:
            # Insert a new user
            inserted_id = db.insert_entry(
                Entry={
                    "username": "john_doe",
                    "email": "john@example.com",
                    "passwordHash": "plaintext_password"  # will be hashed automatically
                },
                collection_name="Users"
            )
        # Returns: "abc123..." on success, or None on failure
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

            #check if title already exist for the same user, if so reject the upload
            title = Entry.get("title")
            if title is None:
                print("Upload failed: title is required for resume entries")
                return None
            existing_resumes = self.fetch(collection_name="Resumes", filter={"userId": userId, "title": title})
            if existing_resumes is None:
                print("Upload failed: could not verify title uniqueness for the user")
                return None
            if existing_resumes:
                print(f"Upload failed: Resume with title '{title}' already exists for user ID:{userId}")
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
        """
        Updates a single field on all documents matching the given filter in the specified
        collection. Validates the new value against the collection's Pydantic scheme before
        applying the update. Returns the number of modified documents, or 0 on failure.

        Special handling per collection:
            - "Users":  If the attribute being updated is "passwordHash", the new value
                        is treated as plaintext and will be hashed automatically before saving.

        Example:
            # Update the email of a specific user
            modified_count = db.update_value(
                flt={"username": "john_doe"},
                attribute="email",
                new_value="newemail@example.com",
                collection_name="Users"
            )
        # Returns: 1 if the update was successful, 0 on failure
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
        """
        Deletes all documents matching the given filter from the specified collection.
        Requires a non-empty filter to prevent accidental mass deletion. If no filter
        is provided, no documents will be deleted. Returns the number of deleted documents,
        or 0 on failure.

        Example:
            # Delete a specific user by username
            deleted_count = db.delete_entry(
                flt={"username": "john_doe"},
                collection_name="Users"
            )
        # Returns: 1 if the user was found and deleted, 0 on failure
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
        """
        Verifies a user's credentials against the Users collection. Looks up the user by
        username and compares the provided plaintext password against the stored hash.
        Returns True if the credentials are valid, False otherwise.

        Example:
            # Check if a user's credentials are valid
            is_authenticated = db.login_check(
                username="john_doe",
                password="plaintext_password"
            )
        # Returns: True if credentials match, False if username not found or password is incorrect
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
        """
        Counts the number of documents matching the given filter in the specified collection.
        Returns the match count as an integer, or None if the check failed.

        Example:
            # Check how many resumes belong to a specific user
            match_count = db.entry_exists(
                flt={"userId": "abc123"},
                collection_name="Resumes"
            )
        # Returns: 2 if two resumes were found, 0 if none exist, None on failure
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
        #convert the _id field to string if it exists, so that the document can be returned in JSON format
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    def prepare_filter(self, flt: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        #prepare the filter by converting any string representations of ObjectIds to actual ObjectId instances, so that they can be used in MongoDB queries. 
        #If no filter is provided, return an empty dictionary to match all documents.
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
        #Return the Pydantic scheme class corresponding to the collection name.
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
        #Closes the MongoDB client connection. Should be called when the DBManagement instance is no longer needed to free up resources.
        self.client.close()