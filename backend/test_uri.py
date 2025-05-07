import os
from pymongo import MongoClient
from urllib.parse import quote_plus

def test_uri(uri):
    try:
        # Test connection
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Forces a connection attempt
        print(f"✓ URI Valid: {uri.split('@')[0]}...@{uri.split('@')[-1]}")
        return True
    except Exception as e:
        print(f"❌ Invalid URI: {str(e)}")
        return False

if __name__ == "__main__":
    uri = input("mongodb+srv://mosescod:Kp92kmDQcQneZJph@cluster0.plf9450.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0").strip()
    test_uri(uri)