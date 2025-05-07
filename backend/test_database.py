import os
from pymongo import MongoClient, errors
from urllib.parse import quote_plus
import sys
from dotenv import load_dotenv


def get_mongo_uri():
    """Get MongoDB URI from environment with validation"""
    
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ MONGODB_URI not set in environment variables")
        print("Please set it or use default local MongoDB")
        uri = "mongodb://localhost:27017"
    
    # Handle password encoding
    if "@" in uri and "://" in uri:
        protocol, rest = uri.split("://", 1)
        if ":" in rest.split("@")[0]:  # Has credentials
            user_pass, host = rest.split("@", 1)
            user, password = user_pass.split(":", 1)
            password = quote_plus(password)
            uri = f"{protocol}://{user}:{password}@{host}"
    
    return uri

def test_database_connection():
    """Test MongoDB connection with error details"""
    uri = get_mongo_uri()
    print(f"Testing connection to: {uri.split('@')[-1]}")
    
    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=3000,
            socketTimeoutMS=3000,
            connectTimeoutMS=3000
        )
        # Force connection attempt
        client.server_info()
        print("✓ Connection successful")
        return client
    except errors.ServerSelectionTimeoutError:
        print("❌ Connection timed out - check if MongoDB is running")
    except errors.ConfigurationError:
        print("❌ Invalid URI format - expected format:")
        print("mongodb://user:pass@host:port/db")
        print("or mongodb+srv://user:pass@cluster/db")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    return None

def verify_database_structure(client, db_name="adam_ai"):
    """Check required collections and indexes exist"""
    if not client:
        return False
        
    try:
        db = client[db_name]
        
        # Required collections
        required_collections = {"verses", "themes", "surahs"}
        existing_collections = set(db.list_collection_names())
        missing = required_collections - existing_collections
        
        if missing:
            print(f"❌ Missing collections: {missing}")
            return False
            
        # Check verses collection
        verses = db.verses
        if verses.count_documents({}) == 0:
            print("⚠️ Verses collection is empty")
            
        # Check critical indexes
        required_indexes = {
            "verses": [("surah_number", 1), ("ayah_number", 1)],
            "themes": [("theme", 1)]
        }
        
        for col, indexes in required_indexes.items():
            current_indexes = db[col].index_information()
            for field, direction in indexes:
                index_name = f"{field}_{direction}"
                if index_name not in current_indexes:
                    print(f"❌ Missing index: {col}.{field}")
                    return False
        
        print("✓ Database structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

def create_sample_data(client, db_name="adam_ai"):
    """Insert minimal required data"""
    if not client:
        return False
        
    try:
        db = client[db_name]
        
        # Insert sample verse
        db.verses.insert_one({
            "surah_number": 1,
            "ayah_number": 1,
            "text": "In the name of God, the Most Gracious, the Most Merciful",
            "translation": "en.sahih"
        })
        
        # Insert sample theme
        db.themes.insert_one({
            "theme": "mercy",
            "keywords": ["mercy", "compassion"],
            "surah_number": 1,
            "ayah_number": 1
        })
        
        print("✓ Inserted sample data")
        return True
        
    except Exception as e:
        print(f"❌ Failed to insert data: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== MongoDB Configuration Test ===")
    
    # Get configuration
    uri = get_mongo_uri()
    db_name = os.getenv("MONGO_DB_NAME", "adam_ai")
    
    # Run tests
    client = test_database_connection()
    if client:
        if verify_database_structure(client, db_name):
            if os.getenv("CREATE_SAMPLE_DATA", "false").lower() == "true":
                create_sample_data(client, db_name)
        else:
            print("Attempting to create required structure...")
            if create_sample_data(client, db_name):
                verify_database_structure(client, db_name)