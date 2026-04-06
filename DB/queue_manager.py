import redis
import json

class QueueManager:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0)
        self.queue_name = "db_operations"

    def publish(self, operation: str, payload: dict) -> bool:
        """
        Publishes a write operation to the Redis queue.
        The worker will pick it up and execute it against the database.

        Example:
            queue.publish(
                operation="insertEntry",
                payload={"collection_name": "Users", "entry": {...}}
            )
        # Returns: True if published successfully, False on failure
        """
        try:
            message = json.dumps({"operation": operation, "payload": payload})
            self.client.rpush(self.queue_name, message)
            print(f"Published to queue: {operation}")
            return True
        except Exception as e:
            print(f"Failed to publish to queue: {e}")
            return False