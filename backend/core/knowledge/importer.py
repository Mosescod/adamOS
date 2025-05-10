import os
import requests
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging
from enum import Enum
from typing import List, Dict
from dotenv import load_dotenv
from tqdm import tqdm
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('.env')

class KnowledgeSource(Enum):
    QURAN = "quran"
    BIBLE = "bible"
    WIKIPEDIA = "wikipedia"

class VerseImporter:
    def __init__(self, connection_string: str):
        self.client = MongoClient(
            connection_string,
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            serverSelectionTimeoutMS=30000
        )
        self.db = self.client["AdamAI-KnowledgeDB"]
        self.entries = self.db.entries
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database with proper indexes and search configuration"""
        try:
            # Create standard indexes
            self.entries.create_index([("source", 1)])
            self.entries.create_index([("tags", 1)])
            self.entries.create_index([("metadata.reference", 1)])
            
            # Configure Atlas Search index
            self._configure_search_index()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise

    def _configure_search_index(self):
        """Create or update the search index with the specified mapping"""
        index_definition = {
            "name": "adamai_search",
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "content": {
                            "type": "string",
                            "analyzer": "lucene.english",
                            "searchAnalyzer": "lucene.english"
                        },
                        "source": {
                            "type": "string",
                            "analyzer": "lucene.keyword"
                        },
                        "tags": {
                            "type": "string",
                            "analyzer": "lucene.keyword"
                        },
                        "vector": {
                            "type": "knnVector",
                            "dimensions": 384,
                            "similarity": "cosine"
                        },
                        "metadata": {
                            "type": "document",
                            "fields": {
                                "reference": {
                                    "type": "string",
                                    "analyzer": "lucene.keyword"
                                },
                                "surah_number": {"type": "number"},
                                "ayah_number": {"type": "number"},
                                "book": {
                                    "type": "string",
                                    "analyzer": "lucene.keyword"
                                },
                                "chapter": {"type": "number"},
                                "verse": {"type": "number"},
                                "version": {
                                    "type": "string",
                                    "analyzer": "lucene.keyword"
                                },
                                "revelation_type": {
                                    "type": "string",
                                    "analyzer": "lucene.keyword"
                                }
                            }
                        },
                        "created_at": {"type": "date"}
                    }
                }
            }
        }

        # Check if index exists
        existing_indexes = list(self.db.entries.list_search_indexes())
        index_exists = any(idx['name'] == 'adamai_search' for idx in existing_indexes)

        if not index_exists:
            try:
                self.db.command({
                    "createSearchIndexes": "entries",
                    "indexes": [index_definition]
                })
                logger.info("Created new search index with specified mapping")
                # Wait for index to be ready
                time.sleep(30)  # Initial delay for index creation
            except Exception as e:
                logger.warning(f"Index creation initiated. It may take a few minutes to complete. Error: {str(e)}")
        else:
            logger.info("Using existing search index")

    def _generate_tags(self, text: str) -> List[str]:
        """Generate thematic tags using NLP"""
        themes = {
            'mercy': ['mercy', 'forgiv', 'compassion', 'pardon'],
            'faith': ['faith', 'belief', 'trust', 'iman'],
            'prophets': ['prophet', 'muhammad', 'isa', 'musa'],
            'prayer': ['prayer', 'salah', 'worship', 'dua'],
            'ethics': ['good', 'evil', 'moral', 'character']
        }
        text_lower = text.lower()
        return [theme for theme, keywords in themes.items() 
                if any(kw in text_lower for kw in keywords)] or ['general']

    def import_quran_verses(self, translation: str = "en.asad"):
        """Import Quran verses with proper embedding and metadata"""
        try:
            logger.info("Starting Quran import...")
            response = requests.get(f"https://api.alquran.cloud/v1/quran/{translation}")
            data = response.json()['data']['surahs']
            
            operations = []
            for surah in tqdm(data, desc="Importing Surahs"):
                for ayah in surah['ayahs']:
                    doc = {
                        "source": KnowledgeSource.QURAN.value,
                        "content": ayah['text'],
                        "tags": self._generate_tags(ayah['text']),
                        "vector": self.embedder.encode(ayah['text']).tolist(),
                        "metadata": {
                            "reference": f"{surah['number']}:{ayah['numberInSurah']}",
                            "surah_number": surah['number'],
                            "ayah_number": ayah['numberInSurah'],
                            "surah_name": surah['englishName'],
                            "revelation_type": surah['revelationType']
                        },
                        "created_at": datetime.utcnow()
                    }
                    operations.append(doc)
                    
                    # Batch insert for better performance
                    if len(operations) >= 100:
                        self.entries.insert_many(operations)
                        operations = []
            
            # Insert remaining documents
            if operations:
                self.entries.insert_many(operations)
                
            count = self.entries.count_documents({"source": "quran"})
            logger.info(f"✅ Quran import complete: {count} verses")
            return count
            
        except Exception as e:
            logger.error(f"❌ Quran import failed: {str(e)}")
            raise

    def import_bible_verses(self, version: str = "kjv"):
        """Import Bible verses with proper embedding and metadata"""
        try:
            logger.info("Starting Bible import...")
            books = [
                {"name": "Genesis", "chapters": 50},
                {"name": "Exodus", "chapters": 40},
                {"name": "Psalms", "chapters": 150},
                {"name": "Matthew", "chapters": 28},
                {"name": "John", "chapters": 21}
            ]
            base_url = "https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles"

            operations = []
            for book in tqdm(books, desc="Importing Books"):
                book_name = book["name"].lower()
                for chapter in range(1, book["chapters"] + 1):
                    verse = 1
                    while True:
                        try:
                            url = f"{base_url}/{version}/books/{book_name}/chapters/{chapter}/verses/{verse}.json"
                            response = requests.get(url, timeout=10)

                            if response.status_code == 404:
                                break  # No more verses
                                
                            response.raise_for_status()
                            data = response.json()

                            doc = {
                                "source": KnowledgeSource.BIBLE.value,
                                "content": data["text"],
                                "tags": self._generate_tags(data["text"]),
                                "vector": self.embedder.encode(data["text"]).tolist(),
                                "metadata": {
                                    "reference": f"{book['name']} {chapter}:{verse}",
                                    "book": book["name"],
                                    "chapter": chapter,
                                    "verse": verse,
                                    "version": version
                                },
                                "created_at": datetime.utcnow()
                            }
                            operations.append(doc)
                        
                            # Batch insert
                            if len(operations) >= 50:
                                self.entries.insert_many(operations)
                                operations = []
                            
                            verse += 1
                        
                        except requests.exceptions.RequestException as e:
                            logger.error(f"Request failed for {book_name} {chapter}:{verse}: {str(e)}")
                            break
                        except Exception as e:
                            logger.error(f"Error processing {book_name} {chapter}:{verse}: {str(e)}")
                            verse += 1
        
            # Insert remaining documents
            if operations:
                self.entries.insert_many(operations)
            
            count = self.entries.count_documents({"source": "bible"})
            logger.info(f"✅ Bible import complete: {count} verses")
            return count
        
        except Exception as e:
            logger.error(f"❌ Bible import failed: {str(e)}")
            raise

def main():
    atlas_uri = os.getenv("MONGODB_URI")
    if not atlas_uri:
        raise ValueError("MONGODB_URI environment variable not set")
    
    importer = VerseImporter(atlas_uri)
    
    try:
        # Clear existing data for fresh import
        logger.info("Clearing existing data...")
        importer.entries.delete_many({})
        
        # Run imports
        importer.import_quran_verses()
        importer.import_bible_verses()
        
        # Print summary
        stats = {
            "quran_verses": importer.entries.count_documents({"source": "quran"}),
            "bible_verses": importer.entries.count_documents({"source": "bible"})
        }
        logger.info(f"\n📊 Import Summary:\n{json.dumps(stats, indent=2)}")
        
    except Exception as e:
        logger.error(f"🚨 Import failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()