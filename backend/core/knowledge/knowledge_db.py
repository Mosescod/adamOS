import os
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import numpy as np
from pymongo import UpdateOne, monitoring
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from sentence_transformers import SentenceTransformer
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import requests
import urllib.parse
import time
from dotenv import load_dotenv
from dataclasses import dataclass
from enum import Enum
from pymongo.errors import ConnectionFailure, OperationFailure
from motor.motor_asyncio import AsyncIOMotorClient 


logger = logging.getLogger(__name__)
load_dotenv()

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
    def __init__(self, db_uri: str, db_name: str):
        self.db_uri = os.getenv("MONGODB_URI")
        self.db_name = "AdamAI-KnowledgeDB"
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[db_name]
        self.entries = self.db.enteries
        self.indexes = None
        self.connection_pool_size = 10  
        self.retry_writes = True  
        self.max_pool_size = 100  
        self.min_pool_size = 5

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
        self._connect()

    def _connect(self):
        """Safe connection method with proper SRV URI handling"""
        @retry(stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=(retry_if_exception_type(ConnectionFailure) |
                    retry_if_exception_type(OperationFailure) |
                    retry_if_exception_type(TimeoutError)))
        def connect_with_retry():
            try:
                # Remove any existing modification attempts
                if self.db_uri.startswith("mongodb://mongodb+srv"):
                    self.db_uri = "mongodb+srv://" + self.db_uri.split("mongodb+srv://")[1]
            
                # For SRV records, use the proper format
                if "mongodb+srv://" in self.db_uri:
                    # Don't modify SRV connection strings
                    connect_opts = {
                        "serverSelectionTimeoutMS": 10000,
                        "connectTimeoutMS": 10000,
                        "socketTimeoutMS": 30000,
                        "retryWrites": True,
                        "retryReads": True,
                        "appname": "AdamAI-KnowledgeDB"
                    }
                else:
                    # Standard connection string
                    connect_opts = {
                        "serverSelectionTimeoutMS": 10000,
                        "connectTimeoutMS": 10000,
                        "socketTimeoutMS": 30000,
                        "maxPoolSize": self.max_pool_size,
                        "minPoolSize": 5,
                        "retryWrites": True,
                        "retryReads": True,
                        "appname": "AdamAI-KnowledgeDB"
                    }

                self.client = MongoClient(self.db_uri, **connect_opts)
            
                # Test connection with simple command
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.entries = self.db.entries
                self.indexes = self.db.indexes
            
                logger.info(f"Successfully connected to MongoDB at {self.db_uri}")
            
            except Exception as e:
                logger.error(f"Connection attempt failed: {str(e)}")
                raise

        connect_with_retry()

    def _ensure_connection(self):
        if not self.client or not self.is_healthy():
            logger.warning("Connection lost, reconnecting...")
            self._connect()

        # In knowledge_db.py
    def is_empty(self) -> bool:
        """Check if database has no entries"""
        try:
            return self.entries.count_documents({}) == 0
        except Exception as e:
            logger.error(f"Failed to check if database is empty: {str(e)}")
            return True  # Assume empty if check fails

    def _register_event_listeners(self):
        """Register MongoDB event listeners for monitoring"""
        def command_started(event):
            logger.debug(f"MongoDB command started: {event.command_name}")

        def command_succeeded(event):
            logger.debug(f"MongoDB command succeeded: {event.command_name} in {event.duration_micros}μs")

        def command_failed(event):
            logger.error(f"MongoDB command failed: {event.command_name} with {event.failure}")

        self.client.add_event_listener(command_started)
        self.client.add_event_listener(command_succeeded)
        self.client.add_event_listener(command_failed)
        logger.info("Registered MongoDB event listeners")

    def is_healthy(self) -> bool:
        """Check if database connection is healthy"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
            return False
        
    def import_quran(self, translation: str = "en.asad"):
        """Enhanced Quran importer with vector embeddings"""
        try:
            api_base = "https://api.alquran.cloud/v1"
        
            # Get Quran text
            quran_response = requests.get(f"{api_base}/quran/{translation}")
            quran_response.raise_for_status()
            quran_data = quran_response.json()['data']['surahs']
        
            # Initialize embedding model
            model = SentenceTransformer('all-MiniLM-L6-v2')
        
            # Process verses with embeddings
            verse_ids = []
            for surah in quran_data:
                for ayah in surah['ayahs']:
                    # Generate embedding
                    embedding = model.encode(ayah['text']).tolist()
                
                    # Prepare metadata
                    metadata = {
                        "reference": f"{surah['number']}:{ayah['numberInSurah']}",
                        "surah_name": surah['englishName'],
                        "translation": translation,
                        "revelation_type": surah['revelationType']
                    }
                
                    # Auto-generate tags
                    tags = self._generate_tags(ayah['text'])
                
                    # Store with embedding
                    verse_ids.append(self.store_knowledge(
                        source=KnowledgeSource.QURAN,
                        content=ayah['text'],
                        metadata=metadata,
                        tags=tags,
                        vector=embedding
                    ))
        
            logger.info(f"Imported Quran with {len(verse_ids)} verses and embeddings")
            return verse_ids
        
        except Exception as e:
            logger.error(f"Quran import failed: {str(e)}")
            raise

    def import_bible(self, version: str = "kjv"):
        """Import Bible verses from API"""
        try:
            api_base = "https://bible-api.com"
            model = SentenceTransformer('all-MiniLM-L6-v2')
        
            # Example books to import
            books = ["genesis", "psalms", "matthew"]  
            verse_ids = []
        
            for book in books:
                response = requests.get(f"{api_base}/{book}")
                data = response.json()
            
                for verse in data['verses']:
                    embedding = model.encode(verse['text']).tolist()
                    tags = self._generate_tags(verse['text'])
                
                    verse_ids.append(self.store_knowledge(
                        source=KnowledgeSource.BIBLE,
                        content=verse['text'],
                        metadata={
                            "book": verse['book_name'],
                            "chapter": verse['chapter'],
                            "verse": verse['verse'],
                            "version": version
                        },
                        tags=tags,
                        vector=embedding
                    ))
        
            logger.info(f"Imported {len(verse_ids)} Bible verses")
            return verse_ids
        
        except Exception as e:
            logger.error(f"Bible import failed: {str(e)}")
            raise

    def import_wikipedia(self, topics: List[str]):
        """Import Wikipedia summaries"""
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            entry_ids = []
        
            for topic in topics:
                response = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
                )
                data = response.json()
            
                if 'extract' in data:
                    embedding = model.encode(data['extract']).tolist()
                    tags = [topic.lower().replace(" ", "_")]
                
                    entry_ids.append(self.store_knowledge(
                        source=KnowledgeSource.WIKIPEDIA,
                        content=data['extract'],
                        metadata={
                            "title": data.get('title', topic),
                            "url": data.get('content_urls', {}).get('desktop', {}).get('page')
                        },
                        tags=tags,
                        vector=embedding
                    ))
        
            logger.info(f"Imported {len(entry_ids)} Wikipedia entries")
            return entry_ids
        
        except Exception as e:
            logger.error(f"Wikipedia import failed: {str(e)}")
            raise

    def _generate_tags(self, text: str) -> List[str]:
        """Auto-generate thematic tags from text"""
        themes = {
            'mercy': ['forgiv', 'merciful', 'compassion'],
            'faith': ['believe', 'faith', 'trust'],
            'wisdom': ['wisdom', 'knowledge', 'understand']
        }
    
        text_lower = text.lower()
        return [theme for theme, keywords in themes.items() 
                if any(kw in text_lower for kw in keywords)]

    def _initialize_collections(self):
        """Initialize collections with proper indexes"""
        # Standard indexes
        self.entries.create_index([("source", ASCENDING)])
        self.entries.create_index([("content", "text")])
    
        # No need to create vector index here - it's created in Atlas UI
        logger.info("Standard indexes created - vector index must be created via Atlas UI")

    def _index_exists(self, collection, fields) -> bool:
        """Check if an index already exists"""
        existing = collection.index_information()
        field_keys = [f[0] for f in fields]
        return any(set(field_keys) == set(idx['key'].keys()) for idx in existing.values())

    def store_knowledge(self, source: KnowledgeSource, content: str, 
                   metadata: Dict, tags: List[str], vector: List[float]):
        """Store knowledge with all required fields"""
        doc = {
            "source": source.value,
            "content": content,
            "metadata": metadata,
            "tags": tags,
            "vector": vector,
            "created_at": datetime.utcnow(),
            "modified_at": datetime.utcnow()
        }
    
        result = self.entries.insert_one(doc)
        self.index_content(result.inserted_id, "thematic", tags)
        return result.inserted_id
        
    def update_knowledge(self, knowledge_id: str, new_content: str, 
                    new_metadata: Dict = None, new_version: str = None):
        """Update knowledge entry with version control"""
        try:
            # Mark old version as not current
            self.entries.update_one(
                {"_id": knowledge_id},
                {"$set": {"is_current": False}}
            )
        
            # Get old entry to copy fields
            old_entry = self.entries.find_one({"_id": knowledge_id})
            if not old_entry:
                raise ValueError("Knowledge entry not found")
        
            # Create new version
            new_version = new_version or self._increment_version(old_entry.get("version", "1.0"))
        
            new_entry = {
                "source": old_entry["source"],
                "content": new_content,
                "metadata": new_metadata or old_entry["metadata"],
                "version": new_version,
                "created_at": time.time(),
                "modified_at": time.time(),
                "is_current": True,
                "previous_version": knowledge_id  # Track version chain
            }
        
            new_id = self.entries.insert_one(new_entry).inserted_id
            logger.info(f"Updated knowledge {knowledge_id} to version {new_version}")
            return new_id
        
        except Exception as e:
            logger.error(f"Failed to update knowledge: {str(e)}")
            raise

    def _increment_version(self, current_version: str) -> str:
        """Simple version incrementer (1.0 -> 1.1)"""
        try:
            major, minor = current_version.split('.')
            return f"{major}.{int(minor)+1}"
        except:
            return "1.1"

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

    def hybrid_search(self, query: str, source: str = None, limit: int = 5) -> List[Dict]:
        """Hybrid search that accepts source filtering"""
        # Create base query filter
        query_filter = {}
        if source:
            query_filter["source"] = source
    
        # Vector search pipeline
        query_embedding = self.embedding_model.encode(query).tolist()
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "vector",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": limit,
                    "filter": query_filter  # Add source filter here
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "content": 1,
                    "source": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
    
        return list(self.entries.aggregate(pipeline))

    def vector_search(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Perform vector search using Atlas"""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",  # Must match your Atlas index name
                    "path": "vector",        # Field containing embeddings
                    "queryVector": query_vector,
                    "numCandidates": 100,    # Number of potential matches
                    "limit": limit            # Final results
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "content": 1,
                    "source": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
    
        try:
            return list(self.entries.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []

    def get_by_id(self, knowledge_id: str) -> Optional[Dict]:
        """Retrieve knowledge entry by ID"""
        try:
            return self.entries.find_one({"_id": knowledge_id})
        except Exception as e:
            logger.error(f"Failed to get entry {knowledge_id}: {str(e)}")
            return None

    def search(self, query: str = None, source: KnowledgeSource = None, 
           tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """Improved search with proper source handling"""
        query_filter = {}
    
        if source:
            query_filter["source"] = source.value  # Convert enum to string
        
        if tags:
            query_filter["tags"] = {"$in": tags}
        
        if query:
            query_filter["$text"] = {"$search": query}
    
        return list(self.entries.find(query_filter).limit(limit))

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for vector search"""
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()

    def get_all_sources(self) -> List[str]:
        """Get list of all knowledge sources in database"""
        try:
            return self.entries.distinct("source")
        except Exception as e:
            logger.error(f"Failed to get sources: {str(e)}")
            return []

    def backfill_embeddings(self):
        """Generate embeddings for existing documents"""
        model = SentenceTransformer('all-MiniLM-L6-v2')
    
        for doc in self.entries.find({"vector": {"$exists": False}}):
            embedding = model.encode(doc['content']).tolist()
            self.entries.update_one(
                {"_id": doc['_id']},
                {"$set": {"vector": embedding}}
            )
        
            
    def _batch_cursor(self, cursor, batch_size):
        """Helper to batch cursor results"""
        batch = []
        for doc in cursor:
            batch.append(doc)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def get_all_entries(self, limit: int = 1000) -> List[Dict]:
        """Get all knowledge entries with basic fields"""
        return list(self.entries.find({}, limit=limit))

    def vector_search(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Perform vector similarity search"""
        try:
            # Convert numpy array to list if needed
            if isinstance(query_vector, np.ndarray):
                query_vector = query_vector.tolist()
        
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "vector",
                        "queryVector": query_vector,
                        "numCandidates": 100,
                        "limit": limit
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "content": 1,
                        "source": 1,
                        "metadata": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            return list(self.entries.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
        
    def create_backup(self, backup_path: str):
        """Create a JSON backup of the knowledge base"""
        try:
            all_entries = list(self.entries.find())
            with open(backup_path, 'w') as f:
                json.dump(all_entries, f, default=str)
            logger.info(f"Created backup with {len(all_entries)} entries at {backup_path}")
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise

    def restore_from_backup(self, backup_path: str):
        """Restore knowledge base from backup"""
        try:
            with open(backup_path) as f:
                entries = json.load(f)
        
            # Clear existing data
            self.entries.delete_many({})
        
            # Insert in batches
            batch_size = 100
            for i in range(0, len(entries), batch_size):
                self.entries.insert_many(entries[i:i+batch_size])
        
            logger.info(f"Restored {len(entries)} entries from backup")
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise

    def __del__(self):
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except:
                pass

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            return {
                "total_entries": self.entries.count_documents({}),
                "by_source": dict(self.entries.aggregate([
                    {"$group": {"_id": "$source", "count": {"$sum": 1}}}
                ])),
                "last_updated": self.entries.find_one(
                    {}, 
                    sort=[("modified_at", -1)]
                )["modified_at"]
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {}
