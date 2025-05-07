from core.knowledge.quran_db import QuranDatabase

db = QuranDatabase()
verses = db.get_verses_by_theme("mercy")
print(f"Found {len(verses)} verses:")
for v in verses:
    print(f"{v['surah_number']}:{v['ayah_number']} - {v['text']}")

db.themes.insert_one({
    'theme': 'mercy',
    'surah_number': 1,
    'ayah_number': 1,
    'keywords': ['mercy', 'gracious']
})