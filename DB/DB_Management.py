from pymongo import MongoClient
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pydantic import ValidationError, create_model
from pydanticSchemes import MatchEntry, UserScheme, ResumeScheme, JobPostingScheme
from dotenv import load_dotenv
import certifi
import bcrypt
import os

class TransientDBError(Exception):
    """DB is temporarily unavailable, should retry"""
    pass

class PermanentDBError(Exception):
    """Business logic or validation failure, should discard"""
    pass

class DBManagement:

    def __init__(self):
        load_dotenv()
        self.client = MongoClient(
            os.getenv("MONGODB_URI"), 
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
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
                raise PermanentDBError("userId is required for resume entries")
            try:
                #count how many resumes belong to the user with the given username
                docs = self.fetch(collection_name="Resumes", filter={"userId": userId})
            except Exception as e:
                print(f"Upload failed")
                raise TransientDBError(str(e))
            if len(docs) >= 10:
                raise PermanentDBError(f"User with ID:{userId} already has 10 resumes")

            #check if filename already exist for the same user, if so reject the upload
            filename = Entry.get("filename")
            if filename is None:
                raise PermanentDBError("filename is required for resume entries")
            try:
                existing_resumes = self.fetch(collection_name="Resumes", filter={"userId": userId, "filename": filename})
            except Exception as e:
                raise TransientDBError(str(e))
            if existing_resumes is None:
                raise PermanentDBError("could not verify filename uniqueness for the user")
            if existing_resumes:
                raise PermanentDBError(f"Resume with filename '{filename}' already exists for user ID:{userId}")

        if (collection_name == "Users"):
            #use username fetch to check for existing user with same username
            username = Entry.get("username")
            if username is None:
                raise PermanentDBError("username is required for user entries")
            try:
                existing_users = self.fetch(collection_name="Users", filter={"username": username})
            except Exception as e:
                raise TransientDBError(str(e))
            if existing_users is None:
                raise PermanentDBError("could not verify username uniqueness")
            if existing_users:
                raise PermanentDBError(f"User with username {username} already exists")
            #hash the password before validation and insertion
            password = Entry.get("passwordHash")
            if password is None:
                raise PermanentDBError("passwordHash is required for user entries")
            # hash the password and convert bytes to string
            Entry["passwordHash"] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  

        try:
            validated_Entry = self.get_Scheme(collection_name)(**Entry)
            doc = validated_Entry.model_dump()
        except Exception as e:
            print(f"Validation failed: {e}")
            raise PermanentDBError(str(e))

        try:
            coll = self.db[collection_name]
            res = coll.insert_one(doc)
            print(f"Upload successful: inserted_id={res.inserted_id}")
            return str(res.inserted_id)
        except Exception as e:
            print(f"Upload failed")
            raise  TransientDBError(str(e))      
    
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
            scheme = self.get_Scheme(collection_name)
            field = scheme.model_fields.get(attribute)
            if field is None:
                raise PermanentDBError(f"unknown attribute '{attribute}' for collection '{collection_name}'")
            TempModel = create_model("TempModel", **{attribute: (field.annotation, ...)})
            validation = TempModel(**{attribute: new_value})
            new_value = validation.model_dump()[attribute]
        except PermanentDBError:
            raise
        except ValidationError as e:
            print(f"Validation failed: {e}")
            raise PermanentDBError(str(e))
        except Exception as e:
            raise TransientDBError(str(e))
            
        try:
            coll = self.db[collection_name]
            res = coll.update_many(filter_prepared, {"$set": {attribute: new_value}})
            print(f"Update successful: matched={res.matched_count}, modified={res.modified_count}")
            return res.modified_count
        except Exception as e:
            print(f"Update failed")
            raise TransientDBError(str(e))
        
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
            raise PermanentDBError("No filter provided, no documents deleted.")

        filter_prepared = self.prepare_filter(flt)

        try:
            coll = self.db[collection_name]
            res = coll.delete_many(filter_prepared)
            print(f"Delete successful: deleted={res.deleted_count}")
            return res.deleted_count
        except Exception as e:
            print(f"Delete failed")
            raise TransientDBError(str(e))

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
        
    def add_matches(self, resumeId: str, jobPostingId: str, matchScore: int, matchedKeywords: List[str]) -> bool:
        """
        Adds a match entry to a resume's matches array, keeping only the top 10 highest scoring matches.
        Validates the match entry against the MatchEntry scheme before insertion.
        Returns True on success, False on failure.

        Example:
            # Add a match entry to a resume
            success = db.add_matches(
                resumeId="abc123",
                jobPostingId="xyz789",
                matchScore=85,
                matchedKeywords=["python", "mongodb", "fastapi"]
            )
        # Returns: True if the match entry was added successfully, False on failure
        """
        # validate match entry
        try:
            match_entry = MatchEntry(
                jobPostingId=ObjectId(jobPostingId),
                matchScore=matchScore,
                matchedKeywords=matchedKeywords
            ).model_dump()
        except Exception as e:
            raise PermanentDBError(str(e))
            

        try:
            coll = self.db["Resumes"]
            resume = coll.find_one({"_id": ObjectId(resumeId)}, {"matches": 1})
            if resume is None:
                raise PermanentDBError(f"Resume {resumeId} not found")

            matches = resume.get("matches", [])

            # check if jobPostingId already exists
            if any(str(m["jobPostingId"]) == jobPostingId for m in matches):
                raise PermanentDBError(f"Job posting {jobPostingId} already matched to resume {resumeId}")

            matches.append(match_entry)

            # keep only top 10 by score
            matches = sorted(matches, key=lambda x: x["matchScore"], reverse=True)[:10]

            res = coll.update_one({"_id": ObjectId(resumeId)}, {"$set": {"matches": matches}})
            if res.modified_count == 1:
                print(f"Match added successfully to resume {resumeId}")
                return True
            else:
                print(f"Failed to add match to resume {resumeId}")
                return False
        except PermanentDBError:
            raise
        except Exception as e:
            raise TransientDBError(str(e))

    def stringify_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, dict):
                doc[key] = self.stringify_id(value)
            elif isinstance(value, list):
                doc[key] = [
                    self.stringify_id(i) if isinstance(i, dict)
                    else str(i) if isinstance(i, ObjectId)
                    else i
                    for i in value
                ]
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