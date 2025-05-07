from main import AdamAI
from core.knowledge.quran_db import QuranDatabase

# Initialize
adam = AdamAI(quran_db=QuranDatabase(), user_id="tester")

# Test cases
tests = {
    "direct mercy query": "mercy",
    "synonym query": "compassion",
    "prophetic pattern": "who are you",
    "non-themed query": "physics"
}

print("=== Starting Verification Test ===")
for name, query in tests.items():
    print(f"\nTEST: {name} ('{query}')")
    response = adam.query(query)
    print("RESPONSE:", response)
    print("VALID:", "✅" if response and "mercy" in response.lower() else "❌")