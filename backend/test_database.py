# test_knowledge_db.py
from core.knowledge.knowledge_db import KnowledgeDatabase, KnowledgeSource

# Initialize with test MongoDB (make sure you have a running instance)
db = KnowledgeDatabase("mongodb://localhost:27017")

# Test storing and retrieving knowledge
print("Storing test knowledge...")
ids = db.store_knowledge(
    source=KnowledgeSource.BOOK,
    content=["Test wisdom: Patience is a virtue"],
    metadata={"title": "Test Book", "author": "Tester"}
)
print(f"Stored with IDs: {ids}")

# Test search
print("\nSearching for 'patience'...")
results = db.search(query="patience")
for item in results:
    print(f"- {item['content']} (Source: {item['source']})")

# Test Quran import (requires internet)
print("\nImporting Quran verses...")
quran_ids = db.import_quran()
print(f"Imported {len(quran_ids)} Quran verses")