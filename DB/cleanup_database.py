#!/usr/bin/env python3
"""
Database cleanup utility for clearing test data.
Run this to reset the database if you have stale test data.
"""

import os
from dotenv import load_dotenv
from DB_Management import DBManagement

def clear_database():
    """Clear all collections in the test database"""
    db = DBManagement()
    
    print("Connecting to database...")
    try:
        db.client.admin.command('ping')
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    print("\nCollections to clear:")
    collections = db.db.list_collection_names()
    for coll in collections:
        print(f"  - {coll}")
    
    if not collections:
        print("  (no collections found)")
        return True
    
    response = input("\nAre you sure you want to clear ALL data? (yes/no): ").strip().lower()
    if response != "yes":
        print("Cancelled.")
        return False
    
    for collection in collections:
        try:
            db.db.drop_collection(collection)
            print(f"✓ Cleared {collection}")
        except Exception as e:
            print(f"✗ Failed to clear {collection}: {e}")
            return False
    
    print("\n✓ Database cleared successfully")
    return True

def show_database_stats():
    """Show statistics about the current database"""
    db = DBManagement()
    
    try:
        db.client.admin.command('ping')
        print("Database Statistics:")
        print("-" * 40)
        
        collections = db.db.list_collection_names()
        if not collections:
            print("No collections found (database is empty)")
            return
        
        for coll_name in collections:
            coll = db.db[coll_name]
            count = coll.count_documents({})
            print(f"{coll_name}: {count} documents")
        
    except Exception as e:
        print(f"Failed to get stats: {e}")

if __name__ == "__main__":
    import sys
    
    load_dotenv()
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_database_stats()
    else:
        clear_database()
