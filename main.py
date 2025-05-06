from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.quran_db import QuranDatabase
from core.knowledge.mind_integrator import DivineKnowledge
from core.general_personality import AdamPersonality
from core.personality.emotional_model import EmotionalModel
from core.prophetic_responses import AdamRules
from core.memory import ConversationMemory
from core.knowledge.loader import DocumentLoader
from core.knowledge.document_db import DocumentKnowledge
from core.knowledge.synthesizer import DocumentSynthesizer
from extensions.__init__ import ExtensionManager
import logging
import sys
import random
from typing import Dict, Text

logger = logging.getLogger(__name__)

class AdamAI:
    def __init__(self, quran_db, user_id: str = "default"):
        try:
            self.user_id = user_id
            self.knowledge = DivineKnowledge(quran_db)
            self.emotions = EmotionalModel(user_id)
            self.memory = ConversationMemory(user_id)
            
            self.scanner = SacredScanner()
            self.mind = DivineKnowledge(self.scanner.db)
            self.quran_db = quran_db
            
            documents = DocumentLoader.load_from_json("core/knowledge/data/documents.json")
            self.doc_knowledge = DocumentKnowledge()
            self.synthesizer = DocumentSynthesizer(
                documents=documents,
                quran_db=self.scanner.db,
                doc_searcher=self.doc_knowledge
            )
            
            if not self.scanner.db.is_populated():
                logger.warning("Performing emergency Quran storage...")
                if not self.scanner.db.emergency_theme_rebuild():
                    raise RuntimeError("Failed to store sacred verses")
            
            self.personality = AdamPersonality(
                username=user_id,
                synthesizer=self.synthesizer
            )
            self.emotional_model = EmotionalModel(user_id)
            self.prophetic_responses = AdamRules()
            
        except Exception as e:
            logger.critical(f"Creation failed: {str(e)}")
            raise RuntimeError("Adam's clay crumbled during shaping") from e
        
    def initialize_adamai():
        """Initialize AdamAI with proper error handling"""
        try:
            # Initialize database
            db = QuranDatabase()
            if not db.emergency_theme_rebuild():
                raise RuntimeError("Failed to initialize Quran database")
        
            # Initialize knowledge components
            scanner = SacredScanner()
            scanner.db = db
            mind = DivineKnowledge(db)
        
            return {
                'scanner': scanner,
                'mind': mind,
                'db': db
            }
        
        except Exception as e:
            logging.critical(f"Initialization failed: {str(e)}")
            raise

    def query(self, question: str) -> str:
        # Get platform-specific formatting
       # adapter = self.platform_adapters.get(platform, DefaultAdapter())
        try:
            # Check for common themes first
            question_lower = question.lower()
        
            if any(word in question_lower for word in ['create', 'made', 'shape']):
                response = self.mind.get_natural_response('creation')
            elif any(word in question_lower for word in ['hell', 'fire', 'punish']):
                response = self.mind.get_natural_response('hell')
            elif any(word in question_lower for word in ['love', 'spouse', 'wife']):
                response = self.mind.get_natural_response('love')
            elif any(word in question_lower for word in ['mercy', 'forgive', 'compassion']):
                response = self.mind.get_natural_response('mercy')
            else:
                # Fallback to original system if no theme matches
                verse_data = self.mind.search_verse(question)
                if verse_data:
                    response = self._simplify_verse(verse_data)
                else:
                    response = "*reshapes clay* The answer eludes me today"
        
            return self._apply_emotional_formatting(response)
        
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return self._apply_emotional_formatting("*clay cracks* My knowledge fails me momentarily")
            
    def get_user_insights(self) -> dict:
        """Get spiritual profile"""
        return {
            "preferred_theme": self.memory.get_preferred_theme(),
            "conversation_count": len(self.memory.context_window)
            }
    
    def _simplify_verse(self, verse: dict) -> str:
        """Convert verse to natural speech without references"""
        if not verse:
            return self.mind.get_natural_response('default')
    
        text = verse['text']
        for term, replacement in self.mind.term_map.items():
            text = text.replace(term, replacement)
    
        # Remove Quranic specifics and clean text
        text = text.replace("Surah", "").replace("Ayah", "").strip()
        return f"*shaping clay* {text}"
        
    def check_sacred_memory(self) -> str:
        """Diagnostic tool for verse memory"""
        if not self.scanner.db.is_populated():
            return "*clay cracks* My sacred memory lies empty... run emergency_theme_rebuild()"
    
        verse_count = len(self.scanner.db.get_verses_by_theme('creation'))
        return f"*runs fingers over clay tablets* I hold {verse_count} inscribed verses"
    
    def _apply_emotional_formatting(self, response: str) -> str:
        """More nuanced emotional integration"""
        mood = self.emotional_model.mood
        
        # Mood-based prefixes
        if mood > 0.8:
            prefixes = ["*bright eyes* ", "*joyful shaping* "]
        elif mood < 0.3:
            prefixes = ["*heavy hands* ", "*weary voice* "]
        else:
            prefixes = ["*smoothing clay* ", "*thoughtful tone* "]
            
        # Add physical gestures
        gestures = [
            "\n*offers clay piece*",
            "\n*traces finger in clay*",
            "\n*shapes new form while speaking*"
        ]
        
        formatted = random.choice(prefixes) + response
        if random.random() < 0.4:  # 40% chance for gesture
            formatted += random.choice(gestures)
            
        return formatted

    def web_query(self, question: str) -> str:
        """Web-friendly version that doesn't use input()"""
        try:
            return self.query(question)
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return "*clay cracks* My knowledge fails me momentarily"

