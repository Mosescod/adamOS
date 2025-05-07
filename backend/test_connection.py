import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from core.knowledge.quran_db import QuranDatabase

def get_connection_uri():
    """Get URI from input with local fallback"""
    uri = input("mongodb+srv://mosescod:Kp92kmDQcQneZJph@cluster0.plf9450.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0").strip()
    if not uri:
        return "mongodb://localhost:27017"
    
    # Auto-correct common issues
    if "@" in uri and "://" not in uri:
        uri = "mongodb+srv://" + uri
    elif not uri.startswith(("mongodb://", "mongodb+srv://")):
        uri = f"mongodb+srv://{uri}"
    
    return uri

def test_database():
    print("=== Database Connection Test ===")
    uri = get_connection_uri()
    print(f"\nTesting with URI: {uri.split('@')[-1]}")  # Hide credentials
    
    try:
        # 1. Test direct connection
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db_name = uri.split("/")[-1].split("?")[0] if "/" in uri else "adam_ai"
        db = client[db_name]
        print("\n[1] Direct connection:")
        print(f"✓ Connected to {db.name}")
        print(f"Collections: {db.list_collection_names()}")
        
        # 2. Test QuranDatabase
        print("\n[2] QuranDatabase test:")
        quran_db = QuranDatabase(db_uri=uri, db_name=db_name)
        print("✓ Initialized successfully")
        
        # 3. Test queries
        print("\n[3] Query tests:")
        print(f"Verses: {quran_db.verses.count_documents({})}")
        print(f"Themes: {quran_db.themes.count_documents({})}")
        
        mercy_verses = quran_db.get_verses_by_theme("mercy")
        print(f"Mercy verses found: {len(mercy_verses)}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("- For cloud: Check URI format (mongodb+srv://user:pass@cluster/db)")
        print("- For local: Ensure MongoDB service is running")
        print("- Check firewall/network permissions")

if __name__ == "__main__":
    test_database()