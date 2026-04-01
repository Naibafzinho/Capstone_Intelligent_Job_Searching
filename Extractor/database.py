"""
database.py
-----------
Handles all MongoDB operations.
Stores and retrieves resume analysis results.
"""

from datetime import datetime, timezone
from pymongo import MongoClient


# ── Connect ───────────────────────────────────────────────────────────────────

def get_db(uri: str = "mongodb://localhost:27017", db_name: str = "resume_matcher"):
    """Connect to MongoDB and return the database."""
    client = MongoClient(uri)
    return client[db_name]


# ── Save a result ─────────────────────────────────────────────────────────────

def save_result(db, result: dict) -> str:
    """
    Save one resume-vs-job analysis result to MongoDB.

    Expected result format:
    {
        "candidate"      : "John_Resume.pdf",
        "job_title"      : "Data Scientist",
        "skills_matched" : [...],
        "skills_missing" : [...],
        "match_score"    : 72.5
    }

    Returns the inserted document ID as a string.
    """
    result["created_at"] = datetime.now(timezone.utc)
    inserted = db.results.insert_one(result)
    return str(inserted.inserted_id)


# ── Fetch all results ─────────────────────────────────────────────────────────

def fetch_all_results(db) -> list[dict]:
    """Return all stored results, newest first."""
    return list(db.results.find({}, {"_id": 0}).sort("created_at", -1))


# ── Fetch by job title ────────────────────────────────────────────────────────

def fetch_by_job(db, job_title: str) -> list[dict]:
    """Return all results for a specific job title."""
    return list(
        db.results.find(
            {"job_title": {"$regex": job_title, "$options": "i"}},
            {"_id": 0}
        ).sort("match_score", -1)
    )