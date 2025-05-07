from main import AdamAI
from core.knowledge.knowledge_db import KnowledgeDatabase

# Initialize Adam
adam = AdamAI(KnowledgeDatabase(), user_id="test_user")

# Test queries
print("=== Testing Query ===")
print(adam.query("mercy"))
print("\n=== Testing Prophetic Response ===")
print(adam.query("who are you"))