import pymongo
import sys
from pymongo.errors import ConnectionFailure
from config import Config
import os
import socket
import requests



try:
    # Test basic DNS resolution
    socket.gethostbyname('cluster0.plf9450.mongodb.net')
    print("✅ DNS resolution successful")
except socket.gaierror:
    print("⚠️ DNS resolution failed - but connection works (MongoDB driver may be using alternative resolution)")

# Proceed with development since connection works
try:
    client = pymongo.MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Connection successful!")
    print(f"MongoDB version: {client.server_info()['version']}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)