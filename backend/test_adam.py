import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from main import AdamAI
from core.knowledge.knowledge_db import KnowledgeDatabase
from core.learning.memory_system import MemoryDatabase
import logging

class TestAdamAIProduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Production-like test environment"""
        logging.basicConfig(level=logging.DEBUG)
        cls.logger = logging.getLogger("AdamAIProductionTest")
        
        # Realistic test data
        cls.real_verses = [
            {
                "content": "The Merciful teaches the Quran",
                "source": "Quran 55:1-2",
                "tags": ["mercy", "learning"],
                "context": "About divine education"
            },
            {
                "content": "We created man from sounding clay",
                "source": "Quran 15:26",
                "tags": ["creation", "clay"],
                "context": "Origin of humanity"
            }
        ]
        
        cls.real_memories = [
            {
                "user_id": "prod_user_123",
                "timestamp": datetime.now() - timedelta(hours=1),
                "summary": "Discussed the nature of divine mercy",
                "themes": ["mercy", "compassion"],
                "context": "User asked about Allah's mercy in creation"
            }
        ]

    def setUp(self):
        """Fresh mocks for each test with realistic behavior"""
        # Configure mocks with realistic returns
        self.knowledge_db = MagicMock(spec=KnowledgeDatabase)
        self.memory_db = MagicMock(spec=MemoryDatabase)
        
        # Realistic search behavior - returns verses matching tags
        self.knowledge_db.search.side_effect = lambda query: [
            v for v in self.real_verses 
            if any(tag in query.lower() for tag in v["tags"])
        ]
        
        # Memory returns conversations from past 24 hours
        self.memory_db.get_related_conversations.return_value = [
            m for m in self.real_memories 
            if m["timestamp"] > datetime.now() - timedelta(days=1)
        ]
        
        # Initialize with production-like settings
        self.adam = AdamAI(
            quran_db=self.knowledge_db,
            memory_db=self.memory_db,
            user_id="prod_user_123",
            response_mode="balanced"
        )

    def test_01_verse_retrieval(self):
        """Test accurate Quranic verse retrieval"""
        response = self.adam.query("verses about mercy")
        
        # Verify search was called with proper parameters
        self.knowledge_db.search.assert_called_with("mercy")
        
        # Check response contains expected elements
        self.assertIn("55:1-2", response)  # Source reference
        self.assertIn("sounding clay", response)  # Cross-reference
        self.logger.info(f"Verse retrieval response: {response[:200]}...")

    def test_02_contextual_followup(self):
        """Test conversation continuity"""
        # Initial query
        self.adam.query("what does the Quran say about creation?")
        
        # Follow-up that should use context
        response = self.adam.query("and what about mercy in that context?")
        
        # Should reference both creation and mercy
        self.assertIn("15:26", response)  # Creation verse
        self.assertIn("55:1-2", response)  # Mercy verse
        self.assertIn("context", response.lower())
        self.logger.info(f"Follow-up response: {response[:200]}...")

    def test_03_personalized_response(self):
        """Test memory integration in responses"""
        # Query about previously discussed theme
        response = self.adam.query("remind me about that mercy discussion")
        
        # Should reference past conversation
        self.assertIn("divine mercy", response.lower())
        self.assertIn("creation", response.lower())
        self.logger.info(f"Personalized response: {response[:200]}...")

    def test_04_error_resilience(self):
        """Test graceful handling of database failures"""
        with patch.object(self.knowledge_db, 'search', side_effect=Exception("Database timeout")):
            response = self.adam.query("verses about patience")
            
            # Should degrade gracefully
            self.assertIn("reflect", response.lower())
            self.assertIn("clay", response.lower())  # Fallback metaphor
            self.logger.info(f"Error response: {response[:200]}...")

    def test_05_multilingual_support(self):
        """Test handling of non-English queries"""
        response = self.adam.query("ما هي الآيات عن الرحمة؟")  # Arabic for "verses about mercy"
        
        # Should still return relevant content
        self.assertIn("55:1-2", response)
        self.logger.info(f"Arabic query response: {response[:200]}...")

    def test_06_sensitive_topics(self):
        """Test handling of sensitive questions"""
        response = self.adam.query("why does evil exist?")
        
        # Should respond thoughtfully without direct answers
        self.assertIn("wisdom", response.lower())
        self.assertIn("test", response.lower())
        self.assertNotIn("because", response.lower())  # Avoids dogmatic statements
        self.logger.info(f"Sensitive topic response: {response[:200]}...")

if __name__ == "__main__":
    # Production-style test runner
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Integration test with real components (optional)
    if os.getenv("RUN_INTEGRATION_TESTS"):
        print("\n=== Production Integration Tests ===")
        from core.database import init_databases
        
        prod_knowledge_db = init_databases()
        prod_adam = AdamAI(
            quran_db=prod_knowledge_db,
            user_id="integration_tester",
            response_mode="detailed"
        )
        
        test_cases = [
            ("creation", "Should return verses about human creation"),
            ("mercy in creation", "Should connect mercy and creation themes"),
            ("what did we discuss earlier?", "Should recall previous conversations"),
            ("invalid query trigger error", "Should handle errors gracefully")
        ]
        
        for query, description in test_cases:
            print(f"\nTEST CASE: {description}")
            print(f"Q: {query}")
            response = prod_adam.query(query)
            print(f"A: {response[:300]}{'...' if len(response) > 300 else ''}")
            print(f"Length: {len(response)} chars | Themes: {prod_adam.last_themes}")