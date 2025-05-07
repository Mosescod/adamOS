# scanner_test.py
from core.knowledge.quran_db import QuranDatabase
from core.knowledge.sacred_scanner import SacredScanner

print("=== Testing SacredScanner ===")

# 1. Initialize database first
try:
    print("Initializing QuranDatabase...")
    quran_db = QuranDatabase()
    
    # Ensure minimal data exists
    if not quran_db.is_populated():
        print("Loading test data...")
        quran_db.verses.insert_one({
            "surah_number": 1,
            "ayah_number": 1,
            "text": "In the name of God, the Most Gracious, the Most Merciful"
        })
        quran_db.themes.insert_one({
            "theme": "mercy",
            "keywords": ["mercy", "compassion"]
        })

    # 2. Test scanner
    print("Initializing SacredScanner...")
    scanner = SacredScanner(quran_db)
    print("✓ Scanner initialized successfully")
    print("Themes:", list(scanner.thematic_index.keys()))
    
except Exception as e:
    print(f"Error: {str(e)}")