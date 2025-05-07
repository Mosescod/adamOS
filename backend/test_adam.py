from core.knowledge.quran_db import QuranDatabase
from pymongo import MongoClient

def test_connection():
    print("=== Database Connection Test ===")
    
    # Test 1: Local connection
    print("\n[1] Testing local MongoDB...")
    try:
        local_db = QuranDatabase(db_name="adam_ai_test")
        print(f"✓ Local connection OK (DB: {local_db.db.name})")
        print(f"Verses count: {local_db.verses.count_documents({})}")
    except Exception as e:
        print(f"Local connection failed: {str(e)}")
    
    # Test 2: Direct pymongo check
    print("\n[2] Direct pymongo test...")
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
        db = client["adam_ai_test"]
        print(f"✓ Direct connection OK (Collections: {db.list_collection_names()})")
    except Exception as e:
        print(f"Direct connection failed: {str(e)}")
    
    # Test 3: Theme verification
    print("\n[3] Testing theme lookup...")
    try:
        verses = local_db.get_verses_by_theme("mercy")
        print(f"Found {len(verses)} mercy verses")
        for v in verses[:2]:
            print(f"- {v['surah_number']}:{v['ayah_number']} {v['text'][:30]}...")
    except Exception as e:
        print(f"Theme lookup failed: {str(e)}")

if __name__ == "__main__":
    test_connection()