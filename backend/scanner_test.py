# test_sacred_scanner.py
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.knowledge_db import KnowledgeDatabase

db = KnowledgeDatabase("mongodb://localhost:27017")
scanner = SacredScanner(db)

# Test scanning
print("Scanning for 'mercy'...")
results = scanner.scan("What does Islam say about mercy?")
print("\nQuran Verses:")
for verse in results['verses'][:3]:  # Show top 3
    print(f"- {verse['content'][:100]}...")

print("\nWisdom from other sources:")
for wisdom in results['wisdom'][:2]:  # Show top 2
    print(f"- {wisdom['content'][:100]}...")