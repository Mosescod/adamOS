from logging.handlers import RotatingFileHandler
import os
import logging
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from sentence_transformers import SentenceTransformer
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from enum import Enum
import numpy as np

def configure_logging():
    """Configure dual logging - file and console"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Main logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler (for all logs)
    file_handler = RotatingFileHandler(
        'logs/adam_system.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler (only ERROR and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Only show errors in console
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Special ready logger for console
    ready_logger = logging.getLogger('adam_ready')
    ready_logger.propagate = False
    ready_handler = logging.StreamHandler()
    ready_handler.setLevel(logging.INFO)
    ready_handler.setFormatter(logging.Formatter('%(message)s'))
    ready_logger.addHandler(ready_handler)

    # Suppress sentence_transformers logs
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)

# Call this at the start of your application
configure_logging()

load_dotenv()

class KnowledgeSource(Enum):
    QURAN = "quran"
    BIBLE = "bible"
    BOOK = "book"
    DOCUMENT = "document"
    ARTICLE = "article"
    WIKIPEDIA = "wikipedia"

class KnowledgeRetriever:
    def __init__(self, db_uri: str = None, db_name: str = "AdamAI-KnowledgeDB"):
        """
        Initialize the retriever with existing MongoDB collection.
        Uses MONGODB_URI from .env if db_uri not provided.
        """
        self.db_uri = db_uri or os.getenv("MONGODB_URI")
        if not self.db_uri:
            raise ValueError("MongoDB URI not provided and MONGODB_URI not found in .env")
            
        self.db_name = db_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._connect()
        self._ensure_indexes()

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=(retry_if_exception_type(ConnectionFailure) |
                  retry_if_exception_type(OperationFailure)))
    def _connect(self):
        """Establish MongoDB connection with retry logic"""
        try:
            self.client = MongoClient(
                self.db_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=30000,
                retryWrites=True,
                retryReads=True,
                appname="AdamAI-KnowledgeDB"
            )
            self.client.admin.command('ping')  # Test connection
            self.db = self.client[self.db_name]
            self.collection = self.db.entries  # Using existing collection
            logging.getLogger("Successfully connected to MongoDB with existing collection")
        except Exception as e:
            logging.getLogger(f"Connection failed: {str(e)}")
            raise

    def _ensure_indexes(self):
        """Internal method to create all required indexes"""
        try:
            # Text index
            existing = self.collection.index_information()
            if not any(idx.get('text') for idx in existing.values()):
                self.collection.create_index([("content", "text")])
                logging.getLogger("Created text index on content field")
            
            # Other indexes
            self.collection.create_index([("source", 1)])
            self.collection.create_index([("metadata.reference", 1)])
            logging.getLogger("Database indexes verified")
        except Exception as e:
            logging.getLogger(f"Index creation failed: {str(e)}")
            raise RuntimeError("Database index initialization failed")

    def _verify_vector_index(self):
        """Check if vector index exists (for Atlas)"""
        try:
            # This assumes you've already created the index via Atlas UI or importer
            if not list(self.collection.list_search_indexes(name="adamai_search")):
                logging.getLogger("Vector search index not found - some features may be limited")
        except Exception as e:
            logging.getLogger(f"Vector index check failed: {str(e)}")

    # Add this method to the KnowledgeRetriever class
    def create_text_index(self):
        """Public method to create text index if needed"""
        try:
            # Check if text index already exists
            existing_indexes = self.collection.index_information()
            text_index_exists = any(
                idx.get('text') for idx in existing_indexes.values()
            )
        
            if not text_index_exists:
                logging.getLogger("Creating text index on content field")
                self.collection.create_index([("content", "text")])
                return True
            logging.getLogger("Text index already exists")
            return False
        except Exception as e:
            logging.getLogger(f"Text index creation failed: {str(e)}")
            raise RuntimeError("Failed to create text index") from e

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the configured model"""
        return self.embedding_model.encode(text).tolist()

    def text_search(self, query: str, limit: int = 5, source: str = None) -> List[Dict]:
        """
        Perform text search on the existing knowledge base.
        Uses the existing text index on 'content' field.
        """
        try:
            query_filter = {"$text": {"$search": query}}
            if source:
                query_filter["source"] = source
                
            return list(self.collection.find(
                query_filter,
                {
                    "_id": 1,
                    "content": 1,
                    "source": 1,
                    "tags": 1,
                    "metadata": 1,
                    "score": {"$meta": "textScore"}
                }
            ).sort([("score", -1)]).limit(limit))
        except Exception as e:
            logging.getLogger(f"Text search failed for query '{query}': {str(e)}")
            return []

    def vector_search(self, query: str, limit: int = 5, source: str = None) -> List[Dict]:
        """
        Perform vector similarity search using existing embeddings.
        Works with both Atlas vector search and local approximate search.
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            if os.getenv("USE_ATLAS_VECTOR_SEARCH", "false").lower() == "true":
                # Atlas vector search
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": "adamai_search",
                            "path": "vector",
                            "queryVector": query_embedding,
                            "numCandidates": 150,
                            "limit": limit
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "content": 1,
                            "source": 1,
                            "tags": 1,
                            "metadata": 1,
                            "score": {"$meta": "vectorSearchScore"}
                        }
                    }
                ]
                results = list(self.collection.aggregate(pipeline))
            else:
                # Local approximate search (slower)
                results = list(self.collection.aggregate([
                    {
                        "$addFields": {
                            "similarity": {
                                "$let": {
                                    "vars": {
                                        "dotProduct": {"$dotProduct": ["$vector", query_embedding]},
                                        "magnitudeA": {"$sqrt": {"$dotProduct": ["$vector", "$vector"]}},
                                        "magnitudeB": {"$sqrt": {"$dotProduct": [query_embedding, query_embedding]}}
                                    },
                                    "in": {
                                        "$divide": [
                                            "$$dotProduct",
                                            {"$multiply": ["$$magnitudeA", "$$magnitudeB"]}
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {"$sort": {"similarity": -1}},
                    {"$limit": limit},
                    {
                        "$project": {
                            "_id": 1,
                            "content": 1,
                            "source": 1,
                            "tags": 1,
                            "metadata": 1,
                            "score": "$similarity"
                        }
                    }
                ]))
            
            if source:
                results = [doc for doc in results if doc.get('source') == source]
            
            return results
        except Exception as e:
            logging.getLogger(f"Vector search failed: {str(e)}")
            return []

    def hybrid_search(self, query: str, limit: int = 5, source: str = None) -> List[Dict]:
        """
        Combine text and vector search results from existing data.
        """
        try:
            vector_results = self.vector_search(query, limit, source)
            text_results = self.text_search(query, limit, source)
            
            # Combine and deduplicate
            seen_ids = set()
            combined = []
            
            for doc in vector_results + text_results:
                doc_id = str(doc['_id'])
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    combined.append(doc)
            
            # Normalize and combine scores
            max_vector = max(doc.get('score', 0) for doc in vector_results) or 1
            max_text = max(doc.get('score', 0) for doc in text_results) or 1
            
            for doc in combined:
                vector_score = next(
                    (d['score']/max_vector for d in vector_results 
                    if str(d['_id']) == str(doc['_id'])), 0)
                text_score = next(
                    (d['score']/max_text for d in text_results 
                    if str(d['_id']) == str(doc['_id'])), 0)
                doc['combined_score'] = (0.6 * vector_score) + (0.4 * text_score)
            
            return sorted(combined, key=lambda x: x['combined_score'], reverse=True)[:limit]
        except Exception as e:
            logging.getLogger(f"Hybrid search failed: {str(e)}")
            return []

    def get_by_reference(self, reference: str, source: str) -> Optional[Dict]:
        """
        Retrieve document by its reference using existing metadata.
        """
        try:
            if source == KnowledgeSource.QURAN.value:
                parts = reference.split(':')
                if len(parts) == 2:
                    return self.collection.find_one({
                        "source": source,
                        "metadata.surah_number": int(parts[0]),
                        "metadata.ayah_number": int(parts[1])
                    })
            elif source == KnowledgeSource.BIBLE.value:
                return self.collection.find_one({
                    "source": source,
                    "metadata.reference": reference
                })
            return None
        except Exception as e:
            logging.getLogger(f"Reference lookup failed: {str(e)}")
            return None

    def __del__(self):
        """Clean up MongoDB connection"""
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except:
                pass