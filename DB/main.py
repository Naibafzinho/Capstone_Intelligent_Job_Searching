from fastapi import FastAPI
from DB_Management import DBManagement
from queue_manager import QueueManager
from pydanticSchemes import FetchRequestScheme, InsertEntryScheme, UpdateValueScheme, DeleteEntryScheme, LoginScheme, EntryExistScheme, AddMatchesScheme

# run: uvicorn main:app --host 127.0.0.1 --port 8000 --reload

app = FastAPI()
db = DBManagement()       # used for reads only
queue = QueueManager()    # used for writes only

@app.post("/login")
async def login(request: LoginScheme):
    success = db.login_check(username=request.username, password=request.password)
    return {"success": success}

@app.post("/fetch")
async def fetch_users(request: FetchRequestScheme):
    users = db.fetch(collection_name=request.collection_name, filter=request.filter, projection=request.projection)
    return {"results": users}

@app.post("/entryExist")
async def entry_exist(request: EntryExistScheme):
    count = db.entry_exists(collection_name=request.collection_name, flt=request.flt)
    return count

# --- writes go through queue ---

@app.post("/insertEntry")
async def insert_entry(request: InsertEntryScheme):
    success = queue.publish("insertEntry", {"entry": request.entry, "collection_name": request.collection_name})
    return {"queued": success}

@app.post("/updateValue")
async def update_value(request: UpdateValueScheme):
    success = queue.publish("updateValue", {"flt": request.flt, "collection_name": request.collection_name, "attribute": request.attribute, "new_value": request.new_value})
    return {"queued": success}

@app.post("/deleteEntry")
async def delete_entry(request: DeleteEntryScheme):
    success = queue.publish("deleteEntry", {"flt": request.flt, "collection_name": request.collection_name})
    return {"queued": success}

@app.post("/addMatches")
async def add_matches(request: AddMatchesScheme):
    success = queue.publish("addMatches", {"resumeId": request.resumeId, "jobPostingId": request.jobPostingId, "matchScore": request.matchScore, "matchedKeywords": request.matchedKeywords})
    return {"queued": success}