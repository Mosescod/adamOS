import os
from typing import Dict, List, Optional, Union
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
import urllib.parse
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class KnowledgeSource(Enum):
    QURAN = "quran"
    BIBLE = "bible"
    BOOK = "book"
    DOCUMENT = "document"
    ARTICLE = "article"

@dataclass
class KnowledgeEntry:
    source: KnowledgeSource
    content: str
    metadata: Dict
    vector: Optional[List[float]] = None

class KnowledgeDatabase:
    def __init__(self, db_uri: str = None, db_name: str = "adam_knowledge"):
        self.db_uri = db_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.client = None
        self.db = None
        self.entries = None
        self.indexes = None
        
        try:
            self._connect()
            self._initialize_collections()
        except Exception as e:
            logger.critical(f"Database initialization failed: {str(e)}")
            raise RuntimeError("Could not open knowledge repository") from e

    def _connect(self):
        """Safe connection method with retries"""
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def connect_with_retry():
            try:
                if not self.db_uri or "://" not in self.db_uri:
                    self.db_uri = "mongodb://localhost:27017"
                
                protocol, rest = self.db_uri.split("://", 1)
            
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    username, password = auth_part.split(":", 1)
                    password = urllib.parse.quote_plus(password)
                    self.db_uri = f"{protocol}://{username}:{password}@{host_part}"
                
                self.client = MongoClient(
                    self.db_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000
                )
                self.client.server_info()  # Test connection
                self.db = self.client[self.db_name]
                self.entries = self.db.entries
                self.indexes = self.db.indexes
            except Exception as e:
                logger.error(f"Connection attempt failed: {str(e)}")
                raise

        connect_with_retry()

    def _initialize_collections(self):
        """Ensure all collections exist with proper indexes"""
        collections = {
            'entries': [
                [
                    ("source", ASCENDING),
                    ("metadata.title", ASCENDING),
                    ("metadata.author", ASCENDING)
                ],
                {'unique': False}
            ],
            'indexes': [
                [
                    ("knowledge_id", ASCENDING),
                    ("index_type", ASCENDING),
                    ("tags", ASCENDING)
                ],
                {'unique': False}
            ]
        }
        
        for col_name, (index_fields, index_options) in collections.items():
            if col_name not in self.db.list_collection_names():
                self.db.create_collection(col_name)
                logger.info(f"Created collection: {col_name}")
            
            collection = getattr(self.db, col_name)
            collection.create_index(index_fields, **index_options)

    def store_knowledge(self, source: KnowledgeSource, content: Union[str, List[str]], metadata: Dict) -> List[str]:
        """
        Store knowledge content with metadata
        Returns list of inserted IDs
        """
        try:
            if isinstance(content, str):
                content = [content]
            
            entries_to_insert = []
            for idx, text in enumerate(content):
                entry = {
                    "source": source.value,
                    "content": text,
                    "metadata": metadata,
                    "created_at": time.time(),
                    "modified_at": time.time()
                }
                
                # Handle special metadata for different sources
                if source == KnowledgeSource.QURAN:
                    entry["metadata"]["type"] = "verse"
                elif source == KnowledgeSource.BIBLE:
                    entry["metadata"]["type"] = "verse"
                
                entries_to_insert.append(entry)
            
            # Insert in batches
            batch_size = 100
            inserted_ids = []
            for i in range(0, len(entries_to_insert), batch_size):
                result = self.entries.insert_many(entries_to_insert[i:i+batch_size])
                inserted_ids.extend(result.inserted_ids)
                time.sleep(0.1)
            
            logger.info(f"Stored {len(inserted_ids)} entries from {source.value}")
            return inserted_ids
            
        except Exception as e:
            logger.error(f"Failed to store knowledge: {str(e)}")
            raise

    def index_content(self, knowledge_id: str, index_type: str, tags: List[str], vector: Optional[List[float]] = None):
        """
        Create search index for content
        Args:
            knowledge_id: ID of the knowledge entry
            index_type: 'thematic', 'semantic', 'keyword', etc.
            tags: List of tags/categories
            vector: Optional embedding vector
        """
        try:
            index_entry = {
                "knowledge_id": knowledge_id,
                "index_type": index_type,
                "tags": tags,
                "created_at": time.time()
            }
            
            if vector:
                index_entry["vector"] = vector
            
            self.indexes.insert_one(index_entry)
            logger.debug(f"Created index for {knowledge_id} with {len(tags)} tags")
            
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise

    def get_by_id(self, knowledge_id: str) -> Optional[Dict]:
        """Retrieve knowledge entry by ID"""
        try:
            return self.entries.find_one({"_id": knowledge_id})
        except Exception as e:
            logger.error(f"Failed to get entry {knowledge_id}: {str(e)}")
            return None

    def search(
        self,
        query: Optional[str] = None,
        source: Optional[KnowledgeSource] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Flexible search across knowledge base
        Args:
            query: Text search query (optional)
            source: Filter by source (optional)
            tags: Filter by tags (optional)
            limit: Maximum results to return
        """
        try:
            search_filter = {}
            
            if source:
                search_filter["source"] = source.value
            
            if query:
                search_filter["$text"] = {"$search": query}
            
            if tags:
                search_filter["indexes.tags"] = {"$in": tags}
            
            pipeline = [
                {"$match": search_filter},
                {"$limit": limit}
            ]
            
            # If searching by tags, join with indexes collection
            if tags:
                pipeline.insert(0, {
                    "$lookup": {
                        "from": "indexes",
                        "localField": "_id",
                        "foreignField": "knowledge_id",
                        "as": "indexes"
                    }
                })
            
            return list(self.entries.aggregate(pipeline))
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def get_all_sources(self) -> List[str]:
        """Get list of all knowledge sources in database"""
        try:
            return self.entries.distinct("source")
        except Exception as e:
            logger.error(f"Failed to get sources: {str(e)}")
            return []

    def import_quran(self, translation: str = "en.asad"):
        """Helper method to import Quran from API"""
        try:
            api_base = "https://api.alquran.cloud/v1"
            
            # Get surahs metadata
            surahs_response = requests.get(f"{api_base}/meta")
            surahs_response.raise_for_status()
            surahs_data = surahs_response.json()['data']['surahs']['references']
            
            # Get Quran text
            quran_response = requests.get(f"{api_base}/quran/{translation}")
            quran_response.raise_for_status()
            quran_data = quran_response.json()['data']['surahs']
            
            # Process and store verses
            verse_ids = []
            for surah in quran_data:
                metadata = {
                    "title": surah['englishName'],
                    "author": "Allah",
                    "language": "en",
                    "translation": translation,
                    "surah_number": surah['number'],
                    "surah_name": surah['name'],
                    "revelation_type": surah['revelationType']
                }
                
                verses = [ayah['text'] for ayah in surah['ayahs']]
                verse_ids.extend(self.store_knowledge(
                    source=KnowledgeSource.QURAN,
                    content=verses,
                    metadata=metadata
                ))
            
            logger.info(f"Imported Quran with {len(verse_ids)} verses")
            return verse_ids
            
        except Exception as e:
            logger.error(f"Failed to import Quran: {str(e)}")
            raise

    def __del__(self):
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except:
                pass