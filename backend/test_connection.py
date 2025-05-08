import pymongo
import sys
from pymongo.errors import ConnectionFailure
from config import Config
import os

uri = Config.MONGODB_URI

try:
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Connection successful!")
    print(f"MongoDB version: {client.server_info()['version']}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)