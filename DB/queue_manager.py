import redis
import json
import uuid

class QueueManager:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0)
        self.queue_name = "db_operations"

    def publish(self, operation: str, payload: dict, timeout: int = 10) -> dict:
        try:
            job_id = str(uuid.uuid4())
            message = json.dumps({"job_id": job_id, "operation": operation, "payload": payload})
            self.client.rpush(self.queue_name, message)

            # wait for the worker to publish the result
            result = self.client.blpop(f"result:{job_id}", timeout=timeout)
            if result is None:
                return {"success": False, "error": "Worker timed out"}

            return json.loads(result[1])
        except Exception as e:
            return {"success": False, "error": str(e)}