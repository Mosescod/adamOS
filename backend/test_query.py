from main import AdamAI
from core.knowledge.quran_db import QuranDatabase

# Initialize Adam
adam = AdamAI(quran_db=QuranDatabase(), user_id="test_user")

# Test queries
print("=== Testing Query ===")
print(adam.query("mercy"))
print("\n=== Testing Prophetic Response ===")
print(adam.query("who are you"))