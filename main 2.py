"""
main.py
-------
FastAPI entry point for the Job Scraper API.

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Required environment variables:
    GROQ_API_KEY           — your Groq API key
    EXTERNAL_API_ENDPOINT  — DB endpoint (default: http://172.24.165.77:8080/insertEntry)

Install dependencies:
    pip install fastapi uvicorn python-jobspy openai httpx pandas python-dotenv
"""

"""
To run:
    # Install deps
pip install fastapi uvicorn python-jobspy openai httpx pandas python-dotenv

# Set env vars (don't hardcode the key in code)
export GROQ_API_KEY=your_key_here
export EXTERNAL_API_ENDPOINT=http://172.24.165.77:8080/insertEntry

uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
"""

from typing import Annotated

import pandas as pd
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import JSONResponse

from services import (
    insert_jobs_to_db,
    read_skills_file,
    scrape_jobs_for_titles,
    skills_to_job_titles,
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Job Scraper API",
    description=(
        "Upload a .txt file of skills → AI converts them to job titles → "
        "JobSpy scrapes matching postings → results are saved to the database."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Meta"])
async def health():
    """Simple liveness check."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------------------------
@app.post("/scrape-jobs", tags=["Jobs"])
async def scrape_jobs_endpoint(
    # --- required ---
    skills_file: Annotated[
        UploadFile,
        File(description="Plain-text (.txt) file containing the user's skills."),
    ],
    # --- optional search parameters ---
    location: str = Query(
        "San Francisco, CA",
        description="Location to search (e.g. 'Remote', 'New York, NY').",
    ),
    sites: list[str] = Query(
        ["indeed", "linkedin", "zip_recruiter"],
        description="Job boards to scrape.",
    ),
    results_wanted: int = Query(
        20,
        ge=1,
        le=100,
        description="Max results per job title per site.",
    ),
    hours_old: int = Query(
        72,
        ge=1,
        description="Only include postings this many hours old or newer.",
    ),
):
    """
    Full pipeline:

    1. Read skills from the uploaded .txt file.  
    2. Use Groq AI (Llama-3.3-70B) to derive up to 5 job titles from those skills.  
    3. Scrape matching postings from the requested job boards via JobSpy.  
    4. Insert every posting into the database via the configured external API.  
    5. Return the scraped jobs as JSON together with per-job insert results.
    """

    # Step 1 — read skills
    skills_text = await read_skills_file(skills_file)

    # Step 2 — AI: skills → job titles
    job_titles = skills_to_job_titles(skills_text)

    # Step 3 — scrape jobs for each title
    jobs_df: pd.DataFrame = scrape_jobs_for_titles(
        titles=job_titles,
        location=location,
        sites=sites,
        results_wanted=results_wanted,
        hours_old=hours_old,
    )

    # Step 4 — insert into DB and collect per-job results
    db_results = await insert_jobs_to_db(jobs_df)

    # Step 5 — build response
    # Drop internal helper column before serialising
    jobs_df = jobs_df.drop(columns=["_search_term"], errors="ignore")

    # Convert DataFrame to JSON-safe records (NaN → None)
    jobs_records = jobs_df.where(pd.notna(jobs_df), other=None).to_dict(orient="records")

    successful = sum(1 for r in db_results if r["status"] == "success")
    failed = len(db_results) - successful

    return JSONResponse(
        content={
            "message": "Job scraping completed.",
            "derived_job_titles": job_titles,
            "total_jobs_found": len(jobs_df),
            "db_inserts": {
                "successful": successful,
                "failed": failed,
                "details": db_results,
            },
            "jobs": jobs_records,
        }
    )
