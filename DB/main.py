from fastapi import FastAPI
from DB_Management import DBManagement
from pydanticSchemes import FetchRequestScheme, InsertEntryScheme, UpdateValueScheme, DeleteEntryScheme, LoginScheme, EntryExistScheme

app = FastAPI()
db = DBManagement()

#Run: 
#uvicorn main:app --host 127.0.0.1 --port 8000 --reload
#runs this file as a server for FastAPI

@app.post("/login")
async def login(request: LoginScheme):
    success = db.login_check(username=request.username, password=request.password)
    return {"success": success}

@app.post("/updateValue")
async def update_value(request: UpdateValueScheme):
    modified_count = db.update_value(
        flt=request.flt,
        collection_name=request.collection_name,
        attribute=request.attribute,
        new_value=request.new_value
    )
    return {"modified_count": modified_count}

@app.post("/insertEntry")
async def insert_entry(request: InsertEntryScheme):
    inserted_id = db.insert_entry(Entry=request.entry, collection_name=request.collection_name)
    return {"inserted_id": inserted_id}

@app.post("/fetch")
async def fetch_users(request: FetchRequestScheme):
    users = db.fetch(
        collection_name=request.collection_name,
        filter=request.filter,
        projection=request.projection
    )
    return {"results": users}

@app.post("/deleteEntry")
async def delete_entry(request: DeleteEntryScheme):
    deleted_count = db.delete_entry(
        flt=request.flt,
        collection_name=request.collection_name
    )
    return {"deleted_count": deleted_count}

@app.post("/entryExist")
async def entry_exist(request: EntryExistScheme):
    count = db.entry_exists(collection_name=request.collection_name, flt=request.flt)
    return count