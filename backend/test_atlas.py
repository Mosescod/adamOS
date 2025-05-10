from core.knowledge.importer import AtlasImporter
from core.knowledge.knowledge_db import KnowledgeDatabase
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.synthesizer import UniversalSynthesizer
from core.knowledge.mind_integrator import MindIntegrator
import os
from dotenv import load_dotenv

load_dotenv('.env')

def test_system():
    # Initialize with test data
    atlas_uri = os.getenv("MONGODB_URI")
    importer = AtlasImporter(atlas_uri)
    print("Importing test data...")
    importer.import_quran()
    importer.import_bible()
    importer.import_wikipedia()
    
    # Initialize components
    knowledge_db = KnowledgeDatabase(atlas_uri, "AdamAI-KnowledgeDB")
    scanner = SacredScanner(knowledge_db)
    synthesizer = UniversalSynthesizer(knowledge_db)
    mind = MindIntegrator()
    
    # Test questions
    test_questions = [
        "What does Islam say about forgiveness?",
        "Tell me about mercy in Christianity",
        "Who are the prophets in Islam?",
        "How should I pray in Islam?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        
        # 1. Scan for knowledge
        scan_results = scanner.scan(question)
        print(f"Found {len(scan_results['verses'])} Quran verses and {len(scan_results['wisdom'])} other sources")
        
        # 2. Synthesize response
        synthesized = synthesizer.blend(scan_results["verses"], scan_results["wisdom"])
        print(f"Primary theme: {synthesized['primary_theme']}")
        print(f"Confidence: {synthesized['confidence']:.1%}")
        
        # 3. Generate response
        response = mind.integrate(synthesized, {
            "user_id": "test_user",
            "mood": 0.7,
            "religion": "islam"
        })
        print("Adam's response:")
        print(response)
    
    # Cleanup
    knowledge_db.client.drop_database("AdamAI-KnowledgeDB")

if __name__ == "__main__":
    test_system()