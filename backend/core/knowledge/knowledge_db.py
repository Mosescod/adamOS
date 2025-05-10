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

logger = logging.getLogger(__name__)
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
        Initialize the retriever with MongoDB connection.
        Uses MONGODB_URI from .env if db_uri not provided.
        """
        self.db_uri = db_uri or os.getenv("MONGODB_URI")
        if not self.db_uri:
            raise ValueError("MongoDB URI not provided and MONGODB_URI not found in .env")
            
        self.db_name = db_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._connect()

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
            self.entries = self.db.entries
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the configured model"""
        return self.embedding_model.encode(text).tolist()

    def vector_search(self, query: str, limit: int = 5, source: str = None) -> List[Dict]:
        """Perform vector similarity search with post-filtering"""
        try:
            query_embedding = self._generate_embedding(query)
    
            search_cmd = {
                "index": "adamai_search",
                "path": "vector",
                "queryVector": query_embedding,
                "numCandidates": 150,
                "limit": limit * 5 if source else limit  # Get more candidates if filtering
            }
    
            pipeline = [
                {"$vectorSearch": search_cmd},
                {
                    "$project": {
                        "_id": 1,
                        "content": 1,
                        "source": 1,
                        "metadata": 1,
                        "tags": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
    
            results = list(self.entries.aggregate(pipeline))
        
            # Apply source filter in Python if needed
            if source:
                results = [doc for doc in results if doc.get('source') == source]
        
            return sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []

    def text_search(self, query: str, limit: int = 5, source: str = None) -> List[Dict]:
        """
        Perform text search on the knowledge base.
        
        Args:
            query: The text query to search for
            limit: Maximum number of results to return
            source: Optional source filter (e.g., 'quran', 'bible')
        
        Returns:
            List of matching documents
        """
        try:
            query_filter = {"$text": {"$search": query}}
            if source:
                query_filter["source"] = source
                
            return list(self.entries.find(query_filter, {
                "_id": 1,
                "content": 1,
                "source": 1,
                "metadata": 1,
                "tags": 1,
                "score": {"$meta": "textScore"}
            }).limit(limit))
        except Exception as e:
            logger.error(f"Text search failed for query '{query}': {str(e)}")
            return []

    def hybrid_search(self, query: str, limit: int = 5, source: str = None) -> List[Dict]:
        """
        Perform hybrid search combining vector and text search results.
        
        Args:
            query: The text query to search for
            limit: Maximum number of results to return
            source: Optional source filter (e.g., 'quran', 'bible')
        
        Returns:
            List of matching documents with combined scores
        """
        try:
            # Get results from both methods
            vector_results = self.vector_search(query, limit, source)
            text_results = self.text_search(query, limit, source)
            
            # Combine and deduplicate results
            seen_ids = set()
            combined_results = []
            
            for doc in vector_results + text_results:
                doc_id = str(doc['_id'])
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    combined_results.append(doc)
            
            # Sort by score (prioritize vector results)
            return sorted(combined_results,
                         key=lambda x: x.get('score', 0),
                         reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Hybrid search failed for query '{query}': {str(e)}")
            return []

    def get_by_reference(self, reference: str, source: str) -> Optional[Dict]:
        """
        Retrieve a specific entry by its reference (e.g., "1:1" for Quran)
        
        Args:
            reference: The specific reference to look up
            source: The knowledge source ('quran', 'bible', etc.)
        
        Returns:
            The matching document or None if not found
        """
        try:
            return self.entries.find_one({
                "source": source,
                "metadata.reference": reference
            })
        except Exception as e:
            logger.error(f"Failed to lookup reference {reference}: {str(e)}")
            return None

    def __del__(self):
        """Clean up MongoDB connection when object is destroyed"""
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except:
                pass