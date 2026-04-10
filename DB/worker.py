import redis
import json
import time
import signal
from DB_Management import DBManagement, TransientDBError, PermanentDBError

#run: python worker.py

db = DBManagement()
client = redis.Redis(host='localhost', port=6379, db=0)
queue_name = "db_operations"
dead_letter_queue = "db_operations_failed"
db_healthy = True
MAX_RETRIES = 3
poison_queue = "db_operations_poison"

def check_db_health() -> bool:
    """
    Pings the MongoDB server to check if the connection is available.
    Returns True if healthy, False otherwise.
    """
    try:
        db.client.admin.command('ping')
        return True
    except Exception:
        return False

def dispatch(operation: str, payload: dict):
    """
    Dispatches a message to the correct DBManagement method.
    Raises TransientDBError for DB connection issues, PermanentDBError for business logic failures.
    """
    print(f"Processing operation: {operation}")
    if operation == "insertEntry":
        db.insert_entry(Entry=payload["entry"], collection_name=payload["collection_name"])
    elif operation == "updateValue":
        db.update_value(flt=payload["flt"], attribute=payload["attribute"], new_value=payload["new_value"], collection_name=payload["collection_name"])
    elif operation == "deleteEntry":
        db.delete_entry(flt=payload["flt"], collection_name=payload["collection_name"])
    elif operation == "addMatches":
        db.add_matches(resumeId=payload["resumeId"], jobPostingId=payload["jobPostingId"], matchScore=payload["matchScore"], matchedKeywords=payload["matchedKeywords"])
    else:
        raise PermanentDBError(f"Unknown operation: {operation}")

def process_message(message) -> bool:
    """
    Processes a single message. Returns True on success, False on permanent failure.
    Raises TransientDBError if the DB is unavailable so the caller can handle it.
    """
    data = json.loads(message)
    operation = data["operation"]
    payload = data["payload"]

    try:
        dispatch(operation, payload)
        return True
    except PermanentDBError as e:
        print(f"Permanent failure, discarding: {e}")
        return False
    # TransientDBError propagates up to the caller

def drain_dead_letter_queue():
    """
    Attempts to reprocess all messages in the dead letter queue.
    Stops immediately if a transient error is encountered — DB is still down.
    """
    dead_count = client.llen(dead_letter_queue)
    if dead_count == 0:
        return

    print(f"Found {dead_count} failed messages, retrying...")
    for _ in range(dead_count):
        message = client.lpop(dead_letter_queue)
        if message is None:
            break
        try:
            if process_message(message):
                print("Dead letter message recovered successfully")
            # if False it was a permanent failure, already discarded
        except TransientDBError:
            # DB went down again mid-drain, put message back and stop
            print("Transient error during dead letter queue processing")
            handle_retry(json.loads(message))
            continue

def handle_retry(message_data: dict):
    retries = message_data.get("retries", 0) + 1
    message_data["retries"] = retries

    if retries > MAX_RETRIES:
        print(f"Message exceeded max retries ({MAX_RETRIES}), moving to poison queue")
        client.rpush(poison_queue, json.dumps(message_data))
    else:
        print(f"Retrying message ({retries}/{MAX_RETRIES})")
        client.rpush(dead_letter_queue, json.dumps(message_data))

# check dead letter queue on startup
print("Worker started, checking dead letter queue...")
try:
    drain_dead_letter_queue()
except TransientDBError:
    print("DB is down at startup, will retry...")
    db_healthy = False

print("Listening for new messages...")

running = True

def shutdown(sig, frame):
    global running
    print("Shutting down worker...")
    running = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

while running:
    if not db_healthy:
        print("DB is down, checking health...")
        db_healthy = check_db_health()
        if db_healthy:
            print("DB recovered, draining dead letter queue...")
            drain_dead_letter_queue()
        else:
            time.sleep(3)  # wait before checking again
        continue

    if client.llen(dead_letter_queue) > 0:
        drain_dead_letter_queue()  # check for any failed messages before processing new ones

    # DB is healthy, process normally
    result = client.blpop(queue_name, timeout=5)
    if result is not None:
        _, message = result
        try:
            if not process_message(message):
                pass  # permanent failure, already discarded
        except TransientDBError as e:
            print(f"DB went down: {e}")
            data = json.loads(message)
            handle_retry(data)
            db_healthy = False

db.close()
client.close()
print("Worker stopped.")