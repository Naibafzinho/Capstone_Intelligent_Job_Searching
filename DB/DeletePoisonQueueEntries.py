import redis

client = redis.Redis(host='localhost', port=6379, db=0)
poison_queue = "db_operations_poison"

def clear_queue():
    count = client.llen(poison_queue)
    client.delete(poison_queue)
    print(f"Deleted {count} messages from {poison_queue}")

if __name__ == "__main__":
    clear_queue()