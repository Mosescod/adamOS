import os
from pymongo import MongoClient
from pprint import pprint
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('.env')

class AtlasSearchVerifier:
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
        
    def verify_basic_queries(self):
        """Test basic CRUD operations"""
        logger.info("\n🔍 BASIC QUERY VERIFICATION")
        
        # Count documents
        total = self.entries.count_documents({})
        quran_count = self.entries.count_documents({"source": "quran"})
        logger.info(f"Total documents: {total}")
        logger.info(f"Quran verses: {quran_count}")
        
        # Fetch sample documents
        logger.info("\nSample Quran verse:")
        quran_verse = self.entries.find_one({"source": "quran"})
        pprint({k: v for k, v in quran_verse.items() if k != 'vector'})
        
        logger.info("\nSample Bible verse:")
        bible_verse = self.entries.find_one({"source": "bible"})
        pprint({k: v for k, v in bible_verse.items() if k != 'vector'})

    def verify_text_search(self):
        """Test Atlas text search"""
        logger.info("\n🔎 TEXT SEARCH VERIFICATION")
        
        try:
            # Simple text search
            results = list(self.entries.aggregate([
                {
                    "$search": {
                        "index": "adamai_search",
                        "text": {
                            "query": "mercy",
                            "path": "content"
                        }
                    }
                },
                {"$limit": 2},
                {
                    "$project": {
                        "content": 1,
                        "source": 1,
                        "score": {"$meta": "searchScore"}
                    }
                }
            ]))
            
            logger.info("Search results for 'mercy':")
            for doc in results:
                print(f"- Score: {doc['score']:.3f}")
                print(f"  {doc['content'][:80]}...")
                print(f"  Source: {doc['source']}\n")
                
        except Exception as e:
            logger.error(f"Text search failed: {str(e)}")

    def verify_vector_search(self):
        """Test vector similarity search"""
        logger.info("\n🧠 VECTOR SEARCH VERIFICATION")
        
        try:
            # Get a sample query embedding
            query = "forgiveness in Islam"
            query_vector = self.embedder.encode(query).tolist()
            
            results = list(self.entries.aggregate([
                {
                    "$vectorSearch": {
                        "index": "adamai_search",
                        "path": "vector",
                        "queryVector": query_vector,
                        "numCandidates": 50,
                        "limit": 3
                    }
                },
                {
                    "$project": {
                        "content": 1,
                        "source": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]))
            
            logger.info(f"Vector search results for '{query}':")
            for doc in results:
                print(f"- Score: {doc['score']:.3f}")
                print(f"  {doc['content'][:80]}...")
                print(f"  Source: {doc['source']}\n")
                
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")

    def verify_hybrid_search(self):
        """Test combined text + vector search"""
        logger.info("\n🔗 HYBRID SEARCH VERIFICATION")
    
        try:
            query = "prophet Muhammad"
            query_vector = self.embedder.encode(query).tolist()
        
            # Text search
            text_results = list(self.entries.aggregate([
                {
                    "$search": {
                        "index": "adamai_search",
                        "text": {
                            "query": query,
                            "path": "content",
                            "score": {"boost": {"value": 1.5}}
                        }
                    }
                },
                {"$limit": 3},
                {
                    "$project": {
                        "content": 1,
                        "source": 1,
                        "score": {"$meta": "searchScore"}
                    }
                }
            ]))
        
            # Vector search
            vector_results = list(self.entries.aggregate([
                {
                    "$search": {
                        "index": "adamai_search",
                        "knnBeta": {
                            "vector": query_vector,
                            "path": "vector",
                            "k": 50
                        }
                    }
                },
                {"$limit": 3},
                {
                    "$project": {
                        "content": 1,
                        "source": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]))
        
            # Combine and deduplicate results
            combined = text_results + vector_results
            seen_ids = set()
            unique_results = []
            for doc in combined:
                if str(doc['_id']) not in seen_ids:
                    seen_ids.add(str(doc['_id']))
                    unique_results.append(doc)

            logger.info(f"Hybrid search results for '{query}':")
            for doc in unique_results[:3]:  # Show top 3 combined results
                print(f"- Score: {doc.get('score', 0):.3f}")
                print(f"  {doc['content'][:80]}...")
                print(f"  Source: {doc['source']}\n")
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")

def main():
    # Get connection string from environment
    atlas_uri = os.getenv("MONGODB_URI")
    if not atlas_uri:
        raise ValueError("Set MONGODB_URI environment variable")
    
    verifier = AtlasSearchVerifier(atlas_uri)
    
    try:
        logger.info("🚀 Starting Atlas Search Verification")
        
        # Run verification tests
        verifier.verify_basic_queries()
        verifier.verify_text_search()
        verifier.verify_vector_search()
        verifier.verify_hybrid_search()
        
        logger.info("✅ All verification tests completed")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()