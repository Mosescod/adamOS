import os
from typing import Dict, List, Optional
import logging
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
import urllib.parse

logger = logging.getLogger(__name__)

class QuranDatabase:
    def __init__(self, db_uri: str = None, db_name: str = "adam_ai"):
        self.db_uri = db_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.default_translation = "en.sahih"
        self.client = None
        self.db = None
        self.verses = None
        self.surahs = None
        self.themes = None
        
        try:
            self._connect()
            self._initialize_collections()
            
            if not self.is_populated():
                logger.warning("Database empty, loading minimal data...")
                self._load_minimal_data()
                
        except Exception as e:
            logger.critical(f"Database initialization failed: {str(e)}")
            raise RuntimeError("Could not open sacred knowledge repository") from e

    def _connect(self):
        """Establish MongoDB connection with proper encoding"""
        try:
            if "@" in self.db_uri.split("://")[1]:
                protocol, rest = self.db_uri.split("://")
                creds, host = rest.split("@")
                username, password = creds.split(":")
                encoded_pwd = urllib.parse.quote_plus(password)
                self.db_uri = f"{protocol}://{username}:{encoded_pwd}@{host}"

            self.client = MongoClient(
                self.db_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            self.db = self.client[self.db_name]
            
            self.verses = self.db.verses
            self.surahs = self.db.surahs
            self.themes = self.db.themes
            
        except PyMongoError as e:
            logger.error(f"Connection failed: {str(e)}")
            raise

    def _initialize_collections(self):
        """Ensure all collections exist with proper indexes"""
        collections = {
            'verses': [
                [("surah_number", ASCENDING), 
                 ("ayah_number", ASCENDING),
                 ("translation", ASCENDING)],
                {'unique': True}
            ],
            'surahs': [
                [("number", ASCENDING)],
                {'unique': True}
            ],
            'themes': [
                [("theme", ASCENDING),
                 ("surah_number", ASCENDING),
                 ("ayah_number", ASCENDING)],
                {}
            ]
        }
        
        for col_name, (index_fields, index_options) in collections.items():
            if col_name not in self.db.list_collection_names():
                self.db.create_collection(col_name)
                logger.info(f"Created collection: {col_name}")
            
            collection = getattr(self.db, col_name)
            collection.create_index(index_fields, **index_options)

    def _load_minimal_data(self):
        """Load essential verses and themes"""
        minimal_data = {
            'verses': [
                {
                    "surah_number": 1,
                    "ayah_number": 1,
                    "text": "In the name of God, the Most Gracious, the Most Merciful",
                    "translation": self.default_translation,
                    "surah_name": "Al-Fatihah"
                },
                {
                    "surah_number": 2,
                    "ayah_number": 255,
                    "text": "Allah! There is no deity except Him, the Ever-Living...",
                    "translation": self.default_translation,
                    "surah_name": "Al-Baqarah"
                }
            ],
            'themes': [
                {"theme": "mercy", "surah_number": 1, "ayah_number": 1},
                {"theme": "creation", "surah_number": 2, "ayah_number": 30}
            ]
        }
        
        try:
            self.verses.insert_many(minimal_data['verses'])
            self.themes.insert_many(minimal_data['themes'])
            logger.info("Loaded minimal Quran data successfully")
        except Exception as e:
            logger.error(f"Failed to load minimal data: {str(e)}")
            raise

    def is_populated(self) -> bool:
        """Check if database has content"""
        try:
            return self.verses.count_documents({}) > 0
        except Exception as e:
            logger.error(f"Population check failed: {str(e)}")
            return False

    def get_verses_by_theme(self, theme: str, limit: int = None) -> List[Dict]:
        """Get verses by theme with optional limit"""
        try:
            pipeline = [
                {"$match": {"theme": theme}},
                {
                    "$lookup": {
                        "from": "verses",
                        "let": {"surah_num": "$surah_number", "ayah_num": "$ayah_number"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$surah_number", "$$surah_num"]},
                                            {"$eq": ["$ayah_number", "$$ayah_num"]},
                                            {"$eq": ["$translation", self.default_translation]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "verse_data"
                    }
                },
                {"$unwind": "$verse_data"},
                {
                    "$lookup": {
                        "from": "surahs",
                        "localField": "verse_data.surah_number",
                        "foreignField": "number",
                        "as": "surah_info"
                    }
                },
                {"$unwind": "$surah_info"},
                {
                    "$project": {
                        "_id": 0,
                        "surah_number": "$verse_data.surah_number",
                        "ayah_number": "$verse_data.ayah_number",
                        "text": "$verse_data.text",
                        "translation": "$verse_data.translation",
                        "surah_name": "$surah_info.english_name"
                    }
                }
            ]
            
            if limit:
                pipeline.append({"$limit": limit})
                
            return list(self.themes.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Failed to get verses by theme: {str(e)}")
            return []

    def store_entire_quran(self, translations: Dict[str, str]) -> bool:
        """Store complete Quran text with translations"""
        try:
            for name, url in translations.items():
                if not self._store_translation(name, url):
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to store Quran: {str(e)}")
            return False

    def add_theme(self, theme: str, keywords: List[str]):
        """Add thematic index entries"""
        try:
            self.themes.delete_many({"theme": theme})
            
            for keyword in keywords:
                matching_verses = self.verses.find({
                    "text": {"$regex": keyword, "$options": "i"}
                })
                
                theme_entries = [{
                    "theme": theme,
                    "surah_number": verse['surah_number'],
                    "ayah_number": verse['ayah_number']
                } for verse in matching_verses]
                
                if theme_entries:
                    self.themes.insert_many(theme_entries)
        except Exception as e:
            logger.error(f"Failed to add theme: {str(e)}")
            raise

    def __del__(self):
        """Clean up MongoDB connection"""
        if self.client:
            self.client.close()