from pymongo import MongoClient
from pprint import pprint
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInspector:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database("AdamAI-KnowledgeDB")
    
    def check_collections(self):
        """List all collections"""
        collections = self.db.list_collection_names()
        logger.info(f"Collections: {collections}")
        return collections
    
    def check_indexes(self, collection_name):
        """Show indexes for a collection"""
        indexes = self.db[collection_name].index_information()
        logger.info(f"Indexes for {collection_name}:")
        pprint(indexes)
        return indexes
    
    def sample_documents(self, collection_name, n=2):
        """Show sample documents"""
        docs = list(self.db[collection_name].find().limit(n))
        logger.info(f"Sample documents from {collection_name}:")
        for doc in docs:
            pprint({k: v for k, v in doc.items() if k != 'vector'})
            print(f"Vector length: {len(doc.get('vector', [])) if 'vector' in doc else 0}")
        return docs
    
    def count_documents(self, collection_name, query=None):
        """Count documents matching query"""
        count = self.db[collection_name].count_documents(query or {})
        logger.info(f"Documents in {collection_name}: {count}")
        return count
    
    def check_search_index(self):
        """Verify Atlas Search index exists"""
        try:
            # This requires MongoDB 4.4+ and proper permissions
            indexes = self.db.command("listSearchIndexes")
            logger.info("Atlas Search indexes:")
            pprint(indexes)
            return indexes
        except Exception as e:
            logger.error(f"Failed to check search indexes: {str(e)}")
            return None

if __name__ == "__main__":
    # Replace with your actual connection string
    inspector = DatabaseInspector(
        "mongodb+srv://mosescod:Kp92kmDQcQneZJph@cluster0.plf9450.mongodb.net"
    )
    
    print("\n=== DATABASE DIAGNOSTICS ===\n")
    
    # 1. Check collections
    collections = inspector.check_collections()
    
    # 2. Check indexes for each collection
    for col in collections:
        inspector.check_indexes(col)
    
    # 3. Sample documents
    for col in collections:
        inspector.sample_documents(col)
    
    # 4. Document counts by source
    print("\n=== DOCUMENT COUNTS ===")
    inspector.count_documents("entries")
    inspector.count_documents("entries", {"source": "quran"})
    inspector.count_documents("entries", {"source": "bible"})
    inspector.count_documents("entries", {"source": "wikipedia"})
    
    # 5. Check search index (Atlas only)
    print("\n=== SEARCH INDEX STATUS ===")
    inspector.check_search_index()