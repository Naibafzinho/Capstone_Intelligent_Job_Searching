"""
services.py
-----------
All business logic for the Job Scraper API:
  - Read skills from an uploaded .txt file
  - Convert skills → job titles via Groq AI
  - Scrape jobs via JobSpy
  - Format each job row into the target JSON schema
  - POST each entry to the external database endpoint
"""

import ast
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import os
from datetime import datetime, date
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
import httpx
import pandas as pd
from fastapi import HTTPException, UploadFile
from openai import OpenAI

# How long to wait (seconds) for a single site/title scrape before giving up
SCRAPE_TIMEOUT: int = int(os.getenv("SCRAPE_TIMEOUT", "45"))
 

# ---------------------------------------------------------------------------
# Configuration (override via environment variables in production)
# ---------------------------------------------------------------------------
load_dotenv()  # Load .env file if present
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

EXTERNAL_API_ENDPOINT: str = os.getenv(
    "EXTERNAL_API_ENDPOINT", "http://127.0.0.1:8000/insertEntry"
)
COLLECTION_NAME: str = "JobPostings"
 
 
# ---------------------------------------------------------------------------
# Internal helper: build a Groq client (raises 500 if key is missing)
# ---------------------------------------------------------------------------
def _get_groq_client() -> OpenAI:
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY environment variable is not set.",
        )
    return OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


# ---------------------------------------------------------------------------
# 1. Read skills from the uploaded .txt file
# ---------------------------------------------------------------------------
async def read_skills_file(file: UploadFile) -> str:
    """Decode and return the raw text from the uploaded skills file."""
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Skills file must be a .txt file.")
    content = await file.read()
    return content.decode("utf-8")


# ---------------------------------------------------------------------------
# 2. Convert raw skills text → up to 5 job title strings via Groq AI
# ---------------------------------------------------------------------------
def skills_to_job_titles(skills: str) -> list[str]:
    """
    Ask Groq to map the skills text to relevant job titles.
    Returns a list[str]; raises HTTPException(502) on failure.
    """
    if not skills.strip():
        return []

    client = _get_groq_client()
    prompt = (
        f"Given these skills:\n{skills}\n\n"
        "Return a list of up to 5 relevant job titles. "
        "Only return a Python list of strings and nothing else."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful career assistant. "
                        "Your response MUST be a valid Python list of strings, e.g. "
                        '["Software Engineer", "Data Scientist"]. '
                        "No explanation, no markdown, no extra text."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list) and all(isinstance(t, str) for t in parsed):
            return parsed
        raise ValueError(f"Unexpected AI response format: {raw}")
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI title generation failed: {exc}",
        )


# ---------------------------------------------------------------------------
# 3. Scrape jobs for each job title via JobSpy
# ---------------------------------------------------------------------------
def scrape_jobs_for_titles(
    titles: list[str],
    location: str,
    sites: list[str],
    results_wanted: int,
    hours_old: int,
) -> pd.DataFrame:
    """
    Iterates over job titles, scrapes each, and returns a combined DataFrame.
    Raises HTTPException(404) if no results are found at all.
    """
    try:
        from jobspy import scrape_jobs
    except ValueError as exc:
        if "numpy.dtype size changed" in str(exc):
            raise HTTPException(
                status_code=500,
                detail=(
                    "NumPy/JobSpy version conflict. Fix with: "
                    "pip install 'numpy>=2.0.0' --force-reinstall && "
                    "pip install pandas --force-reinstall"
                ),
            )
        raise

    frames: list[pd.DataFrame] = []

    def _scrape(term: str, site: str) -> pd.DataFrame | None:
        """Scrape a single term/site combination — runs in a thread."""
        try:
            df = scrape_jobs(
                site_name=[site],
                search_term=term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed="USA",
            )
            return df if not df.empty else None
        except Exception as exc:
            print(f"[scrape_jobs] Error for term='{term}' site='{site}': {exc}")
            return None

    for term in set(titles):  # deduplicate titles
        for site in sites:
            print(f"[scrape_jobs] Scraping term='{term}' site='{site}' ...")
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_scrape, term, site)
                try:
                    df = future.result(timeout=SCRAPE_TIMEOUT)
                    if df is not None:
                        df["_search_term"] = term
                        frames.append(df)
                        print(f"[scrape_jobs] Got {len(df)} results for term='{term}' site='{site}'")
                except FuturesTimeoutError:
                    print(f"[scrape_jobs] Timed out after {SCRAPE_TIMEOUT}s for term='{term}' site='{site}', skipping.")

    valid_frames = [f for f in frames if not f.empty and not f.isna().all().all()]

    if not valid_frames:
        raise HTTPException(
            status_code=404,
            detail="No jobs found for the provided skills / location.",
        )

    return pd.concat(valid_frames, ignore_index=True)


# ---------------------------------------------------------------------------
# 4. Format one job row into the target DB JSON schema
# ---------------------------------------------------------------------------
def format_job_entry(job_row: pd.Series) -> dict:
    """Map a single JobSpy DataFrame row to the JobPostings entry structure."""

    def to_list_or_empty(value) -> list:
        if value is None or (isinstance(value, float) and pd.isna(value)) or value == "":
            return []
        return [str(value)]

    def safe_str(value) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        return str(value)

    # Resolve the best URL and derive the domain from it
    direct_url = job_row.get("job_url_direct")
    fallback_url = job_row.get("job_url")
    best_url = (
        direct_url if pd.notna(direct_url)
        else fallback_url if pd.notna(fallback_url)
        else None
    )
    domain = urlparse(best_url).netloc if best_url else "unknown.com"

    # Description
    description = job_row.get("description", "")
    if not description or pd.isna(description):
        description = "No description provided."

    # Date posted — normalise to ISO string
    date_posted_str = None
    raw_date = job_row.get("date_posted")
    if raw_date is not None and pd.notna(raw_date):
        if isinstance(raw_date, (datetime, date, pd.Timestamp)):
            date_posted_str = pd.Timestamp(raw_date).isoformat()
        else:
            date_posted_str = str(raw_date)

    return {
        "title": job_row.get("title") or "Untitled Job",
        "datePosted": date_posted_str or "",
        "dateExtracted": datetime.now().isoformat(),
        "dateExpiring": "",
        "domain": domain,
        "company": job_row.get("company") or "Unknown Company",
        "locationC": to_list_or_empty(job_row.get("location")),
        "salaryRangeC": to_list_or_empty(job_row.get("salary_range")),
        "jobTypeC": to_list_or_empty(job_row.get("job_type")),
        "industryC": [],
        "experienceLevelC": [],
        "remoteC": to_list_or_empty(job_row.get("work_from_home_type")),
        "companySizeC": safe_str(job_row.get("company_num_employees")),
        "text": str(description),
        "url": str(best_url) if best_url else "",
        "keywords": [],
    }


# ---------------------------------------------------------------------------
# 5. POST every job to the external DB and return per-job results
# ---------------------------------------------------------------------------
async def insert_jobs_to_db(jobs_df: pd.DataFrame) -> list[dict]:
    """
    Formats and POSTs each row to EXTERNAL_API_ENDPOINT.
    Returns a list of result dicts: {title, status, http_code?, message?}
    """
    results: list[dict] = []

    async with httpx.AsyncClient(timeout=3) as http:
        for _, row in jobs_df.iterrows():
            entry = format_job_entry(row)
            payload = {"collection_name": COLLECTION_NAME, "entry": entry}
            title = entry["title"]
            try:
                resp = await http.post(EXTERNAL_API_ENDPOINT, json=payload)
                resp.raise_for_status()
                results.append({
                    "title": title,
                    "status": "success",
                    "http_code": resp.status_code,
                })
            except httpx.RequestError as exc:
                results.append({"title": title, "status": "failed", "message": str(exc)})
            except httpx.HTTPStatusError as exc:
                results.append({
                    "title": title,
                    "status": "failed",
                    "http_code": exc.response.status_code,
                    "message": exc.response.text,
                })
            except Exception as exc:
                results.append({"title": title, "status": "error", "message": str(exc)})

    return results
