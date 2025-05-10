import logging
from core.knowledge.knowledge_db import KnowledgeDatabase, KnowledgeSource
from core.knowledge.sacred_scanner import SacredScanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_system():
    # Initialize components
    mongodb_uri = "mongodb+srv://mosescod:Kp92kmDQcQneZJph@cluster0.plf9450.mongodb.net/Adam_AIOS?retryWrites=true&w=majority"
    db = KnowledgeDatabase(mongodb_uri, "AdamAI-KnowledgeDB")
    scanner = SacredScanner(db)
    
    # 1. Verify database connection
    logger.info("\n=== DATABASE CONNECTION TEST ===")
    logger.info(f"Total documents: {db.entries.count_documents({})}")
    
    # 2. Test sample search
    logger.info("\n=== BASIC SEARCH TEST ===")
    results = db.search(tags=["mercy"], limit=2)
    logger.info(f"Found {len(results)} mercy documents:")
    for doc in results:
        logger.info(f"- {doc['content'][:50]}... (source: {doc['source']})")
    
    # 3. Test vector search
    logger.info("\n=== VECTOR SEARCH TEST ===")
    test_query = "forgiveness in Islam"
    vector_results = db.vector_search(
        db.embedding_model.encode(test_query).tolist(),
        limit=2
    )
    logger.info(f"Vector search results for '{test_query}':")
    for doc in vector_results:
        logger.info(f"- {doc['content'][:50]}... (score: {doc.get('score', 0):.2f})")
    
    # 4. Test thematic scanner
    logger.info("\n=== THEMATIC SCANNER TEST ===")
    scan_results = scanner.scan("What does Islam say about forgiveness?")
    logger.info("Quran results:")
    for verse in scan_results.get('quran', [])[:2]:
        logger.info(f"- {verse['content'][:50]}...")
    
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(f"Database entries: {db.entries.count_documents({})}")
    logger.info(f"Thematic index size: {sum(len(v) for v in scanner.thematic_index.values())}")
    logger.info("Tests completed!")

if __name__ == "__main__":
    test_system()