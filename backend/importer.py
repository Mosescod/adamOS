import os
import requests
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging
from enum import Enum
from typing import List
from dotenv import load_dotenv
from tqdm import tqdm  # For progress bars

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('.env')

class KnowledgeSource(Enum):
    QURAN = "quran"
    BIBLE = "bible"
    WIKIPEDIA = "wikipedia"

class AtlasImporter:
    def __init__(self, connection_string: str):
        """Initialize with Atlas connection and verify setup"""
        self.client = MongoClient(
            connection_string,
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            serverSelectionTimeoutMS=30000
        )
        self.db = self.client["AdamAI-KnowledgeDB"]
        self.entries = self.db.entries
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        self._verify_connection()
        self._verify_search_index()
        self._ensure_indexes()

    def _verify_connection(self):
        """Verify Atlas connection works"""
        try:
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error("❌ Failed to connect to Atlas")
            raise ConnectionError(f"Atlas connection failed: {str(e)}")

    def _ensure_indexes(self):
        """Create necessary database indexes"""
        self.entries.create_index([("source", 1)], background=True)
        self.entries.create_index([("tags", 1)], background=True)
        logger.info("✅ Created basic indexes")

    def _verify_search_index(self):
        """Check or create Atlas Search index"""
        try:
            # Check if index exists
            indexes = list(self.db.entries.list_search_indexes())
            
            if not any(idx['name'] == 'adamai_search' for idx in indexes):
                logger.info("🛠 Creating Atlas Search index...")
                self.db.entries.create_search_index(
                    name="adamai_search",
                    definition={
                        "mappings": {
                            "dynamic": True,
                            "fields": {
                                "content": {
                                    "type": "string",
                                    "analyzer": "lucene.english"
                                },
                                "tags": {
                                    "type": "string",
                                    "analyzer": "lucene.keyword"
                                },
                                "vector": {
                                    "type": "knnVector",
                                    "dimensions": 384,
                                    "similarity": "cosine"
                                }
                            }
                        }
                    }
                )
                logger.info("🔄 Atlas Search index is building... (this takes ~2 minutes)")
            else:
                logger.info("✅ Atlas Search index verified")
                
        except Exception as e:
            logger.error(f"⚠️ Search index verification failed: {str(e)}")
            if "Operation not supported" in str(e):
                logger.warning("This cluster may not have Atlas Search enabled")

    def _generate_tags(self, text: str) -> List[str]:
        """Generate Islamic-themed tags from text"""
        themes = {
            'mercy': ['forgiv', 'merciful', 'rahman', 'raheem', 'compassion'],
            'faith': ['iman', 'belief', 'islam', 'deen', 'tawheed'],
            'prophets': ['muhammad', 'isa', 'musa', 'ibrahim', 'prophet'],
            'prayer': ['salah', 'prayer', 'dua', 'supplication']
        }
        text_lower = text.lower()
        return [theme for theme, keywords in themes.items() 
                if any(kw in text_lower for kw in keywords)] or ['general']

    def import_quran(self):
        """Import Quran verses with embeddings"""
        try:
            logger.info("📖 Starting Quran import...")
            api_base = "https://api.alquran.cloud/v1"
            response = requests.get(f"{api_base}/quran/en.asad", timeout=30)
            data = response.json()['data']['surahs']
            
            batch = []
            for surah in tqdm(data, desc="Importing Surahs"):
                for ayah in surah['ayahs']:
                    batch.append({
                        "source": KnowledgeSource.QURAN.value,
                        "content": ayah['text'],
                        "metadata": {
                            "surah": surah['englishName'],
                            "ayah": ayah['numberInSurah'],
                            "revelation": surah['revelationType']
                        },
                        "tags": self._generate_tags(ayah['text']),
                        "vector": self.embedder.encode(ayah['text']).tolist(),
                        "created_at": datetime.utcnow()
                    })
                    
                    # Insert in batches of 100
                    if len(batch) >= 100:
                        self.entries.insert_many(batch)
                        batch = []
            
            if batch:  # Insert remaining
                self.entries.insert_many(batch)
            
            logger.info(f"✅ Quran import complete: {self.entries.count_documents({'source': 'quran'})} verses")
            
        except Exception as e:
            logger.error(f"❌ Quran import failed: {str(e)}")
            raise

    def import_bible(self):
        """Import key Bible verses about mercy/forgiveness"""
        try:
            logger.info("✝️ Starting Bible import...")
            verses = [
                ("John 3:16", "For God so loved the world that he gave his one and only Son..."),
                ("Psalm 23:1", "The Lord is my shepherd, I lack nothing..."),
                ("Matthew 5:7", "Blessed are the merciful, for they will be shown mercy..."),
                ("Ephesians 4:32", "Be kind and compassionate to one another, forgiving each other...")
            ]
            
            operations = []
            for ref, text in tqdm(verses, desc="Importing Bible verses"):
                operations.append({
                    "source": KnowledgeSource.BIBLE.value,
                    "content": text,
                    "metadata": {"reference": ref},
                    "tags": self._generate_tags(text),
                    "vector": self.embedder.encode(text).tolist(),
                    "created_at": datetime.utcnow()
                })
            
            self.entries.insert_many(operations)
            logger.info(f"✅ Bible import complete: {len(verses)} verses")
            
        except Exception as e:
            logger.error(f"❌ Bible import failed: {str(e)}")
            raise

    def import_wikipedia(self):
        """Import Islamic knowledge from Wikipedia"""
        try:
            logger.info("🌐 Starting Wikipedia import...")
            topics = [
                ("Islamic_view_of_forgiveness", "In Islam, forgiveness is a critical virtue..."),
                ("Mercy_in_Islam", "The concept of mercy (rahma) in Islam is fundamental..."),
                ("Prophets_in_Islam", "Muslims believe in many prophets including Adam, Moses, Jesus and Muhammad...")
            ]
            
            operations = []
            for title, text in tqdm(topics, desc="Importing Wikipedia"):
                operations.append({
                    "source": KnowledgeSource.WIKIPEDIA.value,
                    "content": text,
                    "metadata": {"title": title},
                    "tags": [title.lower().replace("_", " ")],
                    "vector": self.embedder.encode(text).tolist(),
                    "created_at": datetime.utcnow()
                })
            
            self.entries.insert_many(operations)
            logger.info(f"✅ Wikipedia import complete: {len(topics)} articles")
            
        except Exception as e:
            logger.error(f"❌ Wikipedia import failed: {str(e)}")
            raise

def main():
    # Get connection string from environment
    atlas_uri = os.getenv("MONGODB_URI")
    if not atlas_uri:
        raise ValueError("Set MONGODB_URI environment variable")
    
    importer = AtlasImporter(atlas_uri)
    
    try:
        logger.info("\n🚀 Starting AdamAI Knowledge Base Import")
        
        # Run imports
        importer.import_quran()
        importer.import_bible()
        importer.import_wikipedia()
        
        # Final summary
        logger.info("\n📊 Import Summary:")
        for source in KnowledgeSource:
            count = importer.entries.count_documents({"source": source.value})
            logger.info(f"- {source.value.upper()}: {count} documents")
        
        logger.info("\n🎉 All imports completed successfully!")
        
    except Exception as e:
        logger.error(f"\n💥 Critical error during import: {str(e)}")
        raise

if __name__ == "__main__":
    main()