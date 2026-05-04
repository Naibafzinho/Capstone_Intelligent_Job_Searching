from fastapi import FastAPI, HTTPException
from DB_Management import DBManagement
from pydanticSchemes import (
    FetchRequestScheme,
    InsertEntryScheme,
    UpdateValueScheme,
    DeleteEntryScheme,
    LoginScheme,
    EntryExistScheme,
    AddMatchesScheme
)
import requests

# run: uvicorn main:app --port 8000 --reload

app = FastAPI()
db = DBManagement()

EXTRACTOR_URL = "http://127.0.0.1:8001/extract"


@app.post("/login")
async def login(request: LoginScheme):
    success = db.login_check(username=request.username, password=request.password)
    return {"result": success}


@app.post("/fetch")
async def fetch_users(request: FetchRequestScheme):
    users = db.fetch(
        collection_name=request.collection_name,
        filter=request.filter,
        projection=request.projection
    )
    return {"result": users}


@app.post("/entryExist")
async def entry_exist(request: EntryExistScheme):
    count = db.entry_exists(
        collection_name=request.collection_name,
        flt=request.filter
    )
    return {"result": count}


# -----------------------------
# DIRECT DB WRITES (NO REDIS)
# -----------------------------

@app.post("/insertEntry")
async def insert_entry(request: InsertEntryScheme):
    try:
        inserted_id = db.insert_entry(
            Entry=request.entry,
            collection_name=request.collection_name
        )

        # ✅ NEW: trigger extractor automatically for resumes
        if request.collection_name == "Resumes":
            try:
                requests.post(
                    EXTRACTOR_URL,
                    json={"resumeId": inserted_id}
                )
            except Exception as e:
                print(f"Extractor call failed: {e}")

        return {"result": inserted_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/updateValue")
async def update_value(request: UpdateValueScheme):
    try:
        result = db.update_value(
            flt=request.filter,
            attribute=request.attribute,
            new_value=request.new_value,
            collection_name=request.collection_name
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deleteEntry")
async def delete_entry(request: DeleteEntryScheme):
    try:
        result = db.delete_entry(
            flt=request.filter,
            collection_name=request.collection_name
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/addMatches")
async def add_matches(request: AddMatchesScheme):
    try:
        result = db.add_matches(
            resumeId=request.resumeId,
            jobPostingId=request.jobPostingId,
            matchScore=request.matchScore,
            matchedKeywords=request.matchedKeywords
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# ANALYZE ENDPOINT
# -----------------------------
@app.post("/analyze/{resume_id}")
async def analyze_resume(resume_id: str):
    try:
        response = requests.post(
            EXTRACTOR_URL,
            json={"resumeId": resume_id}
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))