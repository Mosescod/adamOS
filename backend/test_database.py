from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Step 1: Load .env
load_dotenv()
uri = os.getenv("MONGODB_URI")

# Step 2: Connect to MongoDB Atlas
try:
    client = MongoClient(uri)
    db = client.get_default_database()  # Uses db in URI (e.g., qurbanDB)

    # Step 3: Insert test data
    test_collection = db["test_agents"]
    test_agent = {
        "name": "Test User",
        "phone": "08000000000"
    }
    insert_result = test_collection.insert_one(test_agent)
    print(f"✅ Inserted Test Agent with ID: {insert_result.inserted_id}")

    # Step 4: Retrieve inserted data
    result = test_collection.find_one({"_id": insert_result.inserted_id})
    print("📦 Retrieved from DB:", result)

except Exception as e:
    print("❌ Error connecting to MongoDB:", e)
