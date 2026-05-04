#!/usr/bin/env python3
"""
Service health check utility.
Verifies that MongoDB, Redis, and all services are running correctly.
"""

import redis
import time
from dotenv import load_dotenv
from DB_Management import DBManagement

def check_redis():
    """Check if Redis is running"""
    print("\nChecking Redis...")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is running on localhost:6379")
        return True
    except redis.exceptions.ConnectionError as e:
        print(f"✗ Redis connection failed: {e}")
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    print("\nChecking MongoDB...")
    try:
        db = DBManagement()
        db.client.admin.command('ping')
        print("✓ MongoDB is running")
        print(f"  Database: TestDB")
        
        collections = db.db.list_collection_names()
        print(f"  Collections: {', '.join(collections) if collections else 'None'}")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def check_db_api(port=8000):
    """Check if DB API is running"""
    print(f"\nChecking DB API on port {port}...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        print(f"✓ DB API is running on http://127.0.0.1:{port}")
        return True
    else:
        print(f"✗ DB API is not running on port {port}")
        print(f"  Start it with: uvicorn main:app --host 127.0.0.1 --port {port} --reload")
        return False

def check_webserver(port=5168):
    """Check if WebServer is running"""
    print(f"\nChecking WebServer on port {port}...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        print(f"✓ WebServer is running on http://localhost:{port}")
        return True
    else:
        print(f"✗ WebServer is not running on port {port}")
        print(f"  Start it with: dotnet watch run")
        return False

def main():
    load_dotenv()
    
    print("=" * 50)
    print("JobRush Service Health Check")
    print("=" * 50)
    
    redis_ok = check_redis()
    mongo_ok = check_mongodb()
    api_ok = check_db_api()
    web_ok = check_webserver()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    print(f"Redis:     {'✓' if redis_ok else '✗'}")
    print(f"MongoDB:   {'✓' if mongo_ok else '✗'}")
    print(f"DB API:    {'✓' if api_ok else '✗'}")
    print(f"WebServer: {'✓' if web_ok else '✗'}")
    
    all_ok = redis_ok and mongo_ok and api_ok and web_ok
    
    if all_ok:
        print("\n✓ All services are running!")
        print("\nYou can access the application at: http://localhost:5168")
    else:
        print("\n✗ Some services are not running. See above for details.")
    
    return all_ok

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
