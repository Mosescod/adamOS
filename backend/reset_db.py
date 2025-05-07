from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["adam_ai"]

# Clear collections
db.verses.delete_many({})
db.themes.delete_many({})

# Insert test verse
db.verses.insert_one({
    "surah_number": 1,
    "ayah_number": 1,
    "text": "In the name of God, the Most Gracious, the Most Merciful",
    "translation": "en.sahih"
})

# Create theme index
db.themes.insert_one({
    "theme": "mercy",
    "surah_number": 1,
    "ayah_number": 1,
    "keywords": ["mercy", "gracious", "compassion"]
})

print("Database reset with 1 test verse about mercy")