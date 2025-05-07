from core.knowledge.quran_db import QuranDatabase

db = QuranDatabase()
print("=== Rebuilding Themes ===")
db.themes.delete_many({})  # Clear old
db.themes.insert_one({
    'theme': 'mercy',
    'surah_number': 1,
    'ayah_number': 1,
    'keywords': ['mercy', 'forgive']
})

print("\n=== Theme Search ===")
verses = db.get_verses_by_theme("mercy")
print(f"Found {len(verses)} verses:")
for v in verses:
    print(f"{v['text']} (Surah {v['surah_number']}:{v['ayah_number']})")