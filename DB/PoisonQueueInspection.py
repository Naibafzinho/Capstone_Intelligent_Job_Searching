import redis
import json

client = redis.Redis(host='localhost', port=6379, db=0)
poison_queue = "db_operations_poison"

def list_messages():
    messages = client.lrange(poison_queue, 0, -1)
    for i, msg in enumerate(messages):
        data = json.loads(msg)
        print(f"\n--- Message {i} ---")
        print(json.dumps(data, indent=2))

def peek_message(index=0):
    msg = client.lindex(poison_queue, index)
    if msg:
        print(json.dumps(json.loads(msg), indent=2))

def count_messages():
    print("Poison queue size:", client.llen(poison_queue))


if __name__ == "__main__":
    count_messages()
    list_messages()