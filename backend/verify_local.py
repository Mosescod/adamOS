from pymongo import MongoClient
from pprint import pprint

def verify_local():
    client = MongoClient("mongodb://localhost:27017")
    db = client["AdamAI-KnowledgeDB"]
    
    print("Collections:", db.list_collection_names())
    
    # Check document counts
    print("\nDocument Counts:")
    print("Quran:", db.entries.count_documents({"source": "quran"}))
    print("Bible:", db.entries.count_documents({"source": "bible"}))
    print("Wikipedia:", db.entries.count_documents({"source": "wikipedia"}))
    
    # Check sample documents
    print("\nSample Quran Verse:")
    pprint(db.entries.find_one({"source": "quran"}, {"vector": 0}))
    
    print("\nSample Bible Verse:")
    pprint(db.entries.find_one({"source": "bible"}, {"vector": 0}))
    
    # Verify vectors
    doc = db.entries.find_one()
    print("\nVector Check:")
    print("Vector exists:", "vector" in doc)
    print("Vector length:", len(doc.get("vector", [])))

if __name__ == "__main__":
    verify_local()