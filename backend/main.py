from typing import Dict, List, Optional
from config import Config
from core.knowledge.knowledge_db import KnowledgeDatabase
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.synthesizer import UniversalSynthesizer
from core.personality.emotional_model import EmotionalModel
from core.personality.general_personality import GeneralPersonality
from core.learning.memory_system import MemoryDatabase
from core.learning.interactive_learner import InteractiveLearner
from core.knowledge.mind_integrator import MindIntegrator
from core.knowledge.loader import ThemeGenerator
import logging
import uuid
from datetime import datetime
import sys 
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdamAI:
    def __init__(self, config: Dict):
        """
        Initialize Adam's complete AI system.
        
        Args:
            config: {
                "mongodb_uri": "mongodb://localhost:27017",
                "analysis_interval": 5,  # Analyze every Nth conversation
                "enable_learning": True
            }
        """
        # Initialize core components
        self.knowledge_db = KnowledgeDatabase(config.MONGODB_URI)
        self.memory_db = MemoryDatabase(config.MONGODB_URI)
        
        # Functional modules
        self.scanner = SacredScanner(self.knowledge_db)
        self.synthesizer = UniversalSynthesizer(self.knowledge_db)
        self.emotion_detector = EmotionalModel()
        self.personality = GeneralPersonality()
        self.learner = InteractiveLearner(self.memory_db)
        self.mind = MindIntegrator()
        
        # Configuration
        self.analysis_interval = config.get("analysis_interval", 5)
        self.enable_learning = config.get("enable_learning", True)
        
        self.theme_generator = ThemeGenerator(self.knowledge_db)
        self._initialize_autonomous_learning()

        logger.info("AdamAI system initialized")
    
    def _initialize_autonomous_learning(self):
        """Start background learning processes"""
        from threading import Thread
        import time
        
        def learning_loop():
            while True:
                self.run_learning_cycle()
                time.sleep(3600)

        Thread(target=learning_loop, daemon=True).start()

    def run_learning_cycle(self):
        """Execute full learning cycle"""
        # Auto-generate themes
        self.themes = self.theme_generator.generate_themes()
        
        # Analyze recent conversations
        unanalyzed = self.memory_db.get_unanalyzed_conversations()
        for conv in unanalyzed:
            self.learner.analyze_conversation(conv["_id"])
        
        # Update knowledge embeddings
        self.scanner.update_embeddings()

    def respond(self, user_id: str, message: str) -> str:
        """
        Main entry point for generating responses.
        
        Args:
            user_id: Unique user identifier
            message: User's input message
            
        Returns:
            Adam's response with clay metaphors
        """
        try:
            # 1. Safety and Emotion Analysis
            safety = self.personality.assess(message)
            if safety["is_offensive"]:
                return "*sets clay aside* I cannot respond to harmful words."
                
            emotion = self.emotion_detector.analyze(message)
            
            # 2. Knowledge Retrieval
            scan_results = self.scanner.scan(
                message,
                context={
                    "user_id": user_id,
                    "mood": emotion["mood_score"]
                }
            )
            
            # 3. Memory Context
            memory_context = self._get_memory_context(user_id, message)
            
            # 4. Knowledge Synthesis
            synthesized = self.synthesizer.blend(
                verses=scan_results["verses"],
                wisdom=scan_results["wisdom"],
                context={
                    "memory": memory_context,
                    "emotion": emotion
                }
            )
            
            # 5. Response Generation
            response = self.mind.integrate(
                synthesized,
                user_context={
                    "user_id": user_id,
                    "mood": emotion["mood_score"],
                    "is_offensive": safety["is_offensive"]
                }
            )
            
            # 6. Log Interaction
            self._log_interaction(user_id, message, response)
            
            # 7. Periodic Learning
            if self.enable_learning:
                self._run_learning_cycle(user_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return "*clay crumbles* My knowledge fails me momentarily."

    def _get_memory_context(self, user_id: str, message: str) -> Dict:
        """
        Retrieve relevant conversation memories.
        Returns: {
            "related_topics": List[str],
            "past_responses": List[Dict]
        }
        """
        # Get summaries of past conversations
        summaries = self.memory_db.find_related_summaries(
            user_id=user_id,
            message=message,
            limit=3
        )
        
        return {
            "related_topics": list(set(
                topic 
                for summary in summaries 
                for topic in summary["topics"]
            )),
            "past_responses": [
                {
                    "content": s["summary"],
                    "timestamp": s["timestamp"]
                } 
                for s in summaries
            ]
        }

    def _log_interaction(self, user_id: str, user_msg: str, adam_response: str):
        """Store conversation in memory"""
        conversation_id = self.memory_db.log_conversation(
            user_id=user_id,
            messages=[
                {"role": "user", "content": user_msg},
                {"role": "adam", "content": adam_response}
            ]
        )
        logger.info(f"Logged conversation {conversation_id}")

    def _run_learning_cycle(self, user_id: str):
        """Periodically analyze conversations"""
        if random.random() < (1 / self.analysis_interval):
            logger.info("Running learning cycle...")
            unanalyzed = self.memory_db.get_unanalyzed_conversations(
                user_id=user_id,
                limit=3
            )
            for conv in unanalyzed:
                self.learner.analyze_conversation(conv["_id"])

    def add_knowledge(self, content: str, source: str, metadata: Dict = None):
        """Manually add knowledge to Adam's database"""
        self.knowledge_db.store_knowledge(
            content=content,
            source=source,
            metadata=metadata or {}
        )
        logger.info(f"Added new {source} knowledge: {content[:50]}...")

# Example Configuration
DEFAULT_CONFIG = {
    "mongodb_uri": "mongodb://localhost:27017",
    "analysis_interval": 5,
    "enable_learning": True
}

if __name__ == "__main__":
    # Initialize Adam
    adam = AdamAI(DEFAULT_CONFIG)
    
    # Example conversation
    user_id = f"user_{uuid.uuid4()}"
    
    print("User: What does Islam say about forgiveness?")
    response = adam.respond(user_id, "What does Islam say about forgiveness?")
    print("Adam:", response)
    
    print("\nUser: Can you remind me about mercy?")
    response = adam.respond(user_id, "Can you remind me about mercy?")
    print("Adam:", response)