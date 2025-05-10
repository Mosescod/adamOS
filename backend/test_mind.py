import pytest
from core.knowledge.importer import AtlasImporter
from core.knowledge.knowledge_db import KnowledgeDatabase
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.synthesizer import UniversalSynthesizer
from core.knowledge.mind_integrator import MindIntegrator
import os
from dotenv import load_dotenv

load_dotenv('.env')

@pytest.fixture
def test_system():
    # Setup test environment
    atlas_uri = os.getenv("MONGODB_URI")
    importer = AtlasImporter(atlas_uri)
    importer.import_quran()
    importer.import_bible()
    importer.import_wikipedia()
    
    # Initialize components
    knowledge_db = KnowledgeDatabase(atlas_uri, "AdamAI-KnowledgeDB")
    scanner = SacredScanner(knowledge_db)
    synthesizer = UniversalSynthesizer(knowledge_db)
    mind = MindIntegrator()
    
    yield {
        "knowledge_db": knowledge_db,
        "scanner": scanner,
        "synthesizer": synthesizer,
        "mind": mind
    }
    
    # Cleanup
    knowledge_db.client.drop_database("AdamAI-KnowledgeDB")

def test_full_workflow(test_system):
    """Test the complete question-to-response workflow"""
    # Test question about mercy
    question = "What does Islam say about forgiveness?"
    
    # 1. Scanner finds relevant knowledge
    scan_results = test_system["scanner"].scan(question)
    assert len(scan_results["verses"]) > 0
    assert any("forgiv" in v["content"].lower() for v in scan_results["verses"])
    
    # 2. Synthesizer blends the knowledge
    synthesized = test_system["synthesizer"].blend(
        scan_results["verses"],
        scan_results["wisdom"]
    )
    assert "forgiv" in synthesized["content"].lower()
    assert synthesized["primary_theme"] == "mercy"
    
    # 3. Mind integrator creates response
    response = test_system["mind"].integrate(synthesized, {
        "user_id": "test_user",
        "mood": 0.7,
        "religion": "islam"
    })
    assert "forgiv" in response.lower()
    assert "*clay*" in response  # Verify Adam's signature style