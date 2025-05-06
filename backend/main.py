from core.knowledge.quran_db import QuranDatabase
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.mind_integrator import DivineKnowledge
from core.general_personality import AdamPersonality
from core.personality.emotional_model import EmotionalModel
from core.prophetic_responses import AdamRules
from core.knowledge.loader import DocumentLoader
from core.knowledge.document_db import DocumentKnowledge
from core.knowledge.synthesizer import DocumentSynthesizer
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class AdamAI:
    def __init__(self, quran_db: Optional[QuranDatabase] = None, user_id: str = "default"):
        try:
            self.user_id = user_id
            self.quran_db = self._initialize_database(quran_db)
            self._initialize_knowledge_components()
            
        except Exception as e:
            logger.critical(f"Creation failed: {str(e)}")
            raise RuntimeError("Failed to create AdamAI instance") from e

    def _initialize_database(self, quran_db: Optional[QuranDatabase]) -> QuranDatabase:
        """Initialize database with fallback"""
        try:
            return quran_db if quran_db is not None else QuranDatabase()
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise RuntimeError("Could not connect to knowledge base") from e

    def _initialize_knowledge_components(self):
        """Initialize all knowledge components"""
        try:
            # Initialize scanner
            self.scanner = SacredScanner(self.quran_db)
            
            # Initialize other components
            self.mind = DivineKnowledge(self.quran_db)
            documents = DocumentLoader.load_from_json("core/knowledge/data/documents.json")
            self.doc_knowledge = DocumentKnowledge()
            self.synthesizer = DocumentSynthesizer(
                documents=documents,
                quran_db=self.quran_db,
                doc_searcher=self.doc_knowledge
            )
            
            self.personality = AdamPersonality(
                username=self.user_id,
                synthesizer=self.synthesizer
            )
            self.emotional_model = EmotionalModel(self.user_id)
            self.prophetic_responses = AdamRules()
            
        except Exception as e:
            logger.error(f"Knowledge initialization failed: {str(e)}")
            raise RuntimeError("Could not form Adam's knowledge") from e

    def query(self, question: str) -> str:
        """Handle user query with error handling"""
        try:
            return self._process_query(question)
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return "My knowledge fails me momentarily"

    def _process_query(self, question: str) -> str:
        """Process query with proper error handling"""
        # Your query processing logic here
        pass