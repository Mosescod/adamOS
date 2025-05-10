import os
from core.knowledge.knowledge_db import KnowledgeRetriever
import logging
from pprint import pprint
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_retriever():
    """Comprehensive test for KnowledgeRetriever"""
    print("\n=== Starting KnowledgeRetriever Tests ===\n")
    
    # Initialize with longer timeout
    retriever = KnowledgeRetriever()
    
    # Test 1: Verify connection and basic collection stats
    print("1. Testing database connection and collection...")
    try:
        count = retriever.entries.count_documents({})
        quran_count = retriever.entries.count_documents({"source": "quran"})
        print(f"✅ Found {count} total documents ({quran_count} Quran verses)")
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return
    
    # Test 2: Verify vectors exist
    print("\n2. Checking for vector embeddings...")
    try:
        with_vector = retriever.entries.count_documents({"vector": {"$exists": True}})
        print(f"✅ {with_vector} documents have vector embeddings")
        if with_vector == 0:
            print("❌ No vectors found - run backfill_embeddings() first")
            return
    except Exception as e:
        print(f"❌ Vector check failed: {str(e)}")
        return
    
    # Test 3: Basic vector search without filters
    print("\n3. Testing basic vector search...")
    try:
        results = retriever.vector_search("mercy", limit=3, source=None)
        print(f"Found {len(results)} results:")
        for i, doc in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Source: {doc.get('source')}")
            print(f"Content: {doc.get('content')[:80]}...")
            print(f"Score: {doc.get('score'):.3f}")
        
        if len(results) == 0:
            print("❌ No results - possible index issues")
    except Exception as e:
        print(f"❌ Basic search failed: {str(e)}")
        return
    
    # Test 4: Filtered vector search
    print("\n4. Testing filtered vector search (Quran only)...")
    try:
        results = retriever.vector_search("mercy", limit=3, source="quran")
        print(f"Found {len(results)} Quran results:")
        for doc in results:
            print(f"- {doc.get('metadata', {}).get('reference')}: {doc.get('content')[:60]}...")
        
        if len(results) == 0:
            print("⚠️ No filtered results - checking why...")
            # Debug why filtering failed
            sample_doc = retriever.entries.find_one({"source": "quran"})
            if not sample_doc:
                print("❌ No Quran documents found in collection")
            else:
                print("ℹ️ Sample Quran document exists but not returned in search")
    except Exception as e:
        print(f"❌ Filtered search failed: {str(e)}")
        return
    
    # Test 5: Verify document structure
    print("\n5. Verifying document structure...")
    try:
        sample = retriever.entries.find_one({"source": "quran"})
        if sample:
            print("✅ Sample Quran document structure:")
            print(f"Content length: {len(sample.get('content', ''))} chars")
            print(f"Vector length: {len(sample.get('vector', []))} dimensions")
            print(f"Metadata: {list(sample.get('metadata', {}).keys())}")
        else:
            print("❌ No Quran documents found to verify structure")
    except Exception as e:
        print(f"❌ Structure check failed: {str(e)}")
        return
    
    print("\n=== Test Summary ===")
    print("Run these diagnostic commands if any tests failed:")
    print("1. Check index status: db.entries.getSearchIndexes()")
    print("2. Verify vectors: db.entries.countDocuments({vector: {$exists: true}})")
    print("3. Check sample doc: db.entries.findOne({source: 'quran'})")

if __name__ == "__main__":
    test_retriever()