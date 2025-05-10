from typing import Dict, Optional
from core.knowledge.knowledge_db import KnowledgeRetriever
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.synthesizer import UniversalSynthesizer
from core.knowledge.mind_integrator import MindIntegrator
from core.personality.emotional_model import EmotionalModel
from core.personality.general_personality import GeneralPersonality
from core.learning.memory_system import MemoryDatabase
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

class AdamAI:
    def __init__(self):
        """Initialize Adam's core response system"""
        self.db = KnowledgeRetriever()
        self.scanner = SacredScanner(self.db)
        self.synthesizer = UniversalSynthesizer(self.db)
        self.integrator = MindIntegrator()
        self.emotion = EmotionalModel()
        self.safety = GeneralPersonality()
        self.memory = MemoryDatabase()
        
        # Warm up components
        self._initialize_system()
        logger.info("AdamAI system ready")

    def _initialize_system(self):
        """Initialize system components"""
        logger.info("Building thematic index...")
        self.scanner._refresh_thematic_index()
        
        if os.getenv("BACKFILL_EMBEDDINGS", "false").lower() == "true":
            logger.info("Backfilling embeddings...")
            self.db.backfill_embeddings()

    def respond(self, user_id: str, message: str) -> str:
        """
        Generate a thoughtful response to user's message
        with Islamic knowledge foundation and clay metaphors.
        
        Args:
            user_id: Unique user identifier
            message: User's input question/message
            
        Returns:
            Adam's crafted response with clay metaphors
        """
        try:
            # Step 1: Safety and Emotion Analysis
            safety_check = self.safety.assess(message)
            if isinstance(safety_check, dict) and safety_check.get('is_unsafe', False):
                return "*sets clay aside* I cannot respond to that which may cause harm."
                
            emotion = self.emotion.analyze(message)
            if isinstance(emotion, dict):
                mood_score = emotion.get('mood_score', 0.5)
            else:
                mood_score = 0.5
            
            # Step 2: Contextual Memory Retrieval
            context = self._prepare_context(user_id, message, mood_score)
            
            # Step 3: Knowledge Retrieval
            scan_results = self.scanner.scan(message, context)
            
            # Step 4: Knowledge Synthesis
            synthesized = self.synthesizer.blend(
                verses=scan_results.get('verses', []),
                wisdom=scan_results.get('wisdom', []),
                context=context
            )
            
            # Step 5: Response Generation
            response = self.integrator.integrate(
                synthesized,
                user_context={
                    "user_id": user_id,
                    "mood": mood_score,
                    "is_offensive": safety_check.get('is_unsafe', False) if isinstance(safety_check, dict) else False
                }
            )
            
            # Step 6: Store Interaction
            self._store_conversation(user_id, message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}", exc_info=True)
            return "*clay crumbles* My thoughts are scattered... please ask again"

    def _store_conversation(self, user_id: str, user_msg: str, adam_response: str):
        """Store conversation in memory"""
        self.memory.store_conversation(
            user_id=user_id,
            user_message=user_msg,
            adam_response=adam_response
        )
        logger.info(f"Stored conversation for user {user_id}")

    def _prepare_context(self, user_id: str, message: str, mood_score: float) -> Dict:
        """Prepare context for knowledge retrieval"""
        # Get relevant conversation history
        history = self.memory.get_recent_conversations(user_id, limit=3)
        
        # Get related themes from past discussions
        related_themes = set()
        conversation_history = []
        
        for conv in history:
            if isinstance(conv, dict):
                # Extract themes from message content
                themes = self.memory._extract_topics(conv.get('user_message', ''))
                themes.extend(self.memory._extract_topics(conv.get('adam_response', '')))
                related_themes.update(themes)
                
                conversation_history.append({
                    "role": "user",
                    "content": conv.get('user_message', '')
                })
                conversation_history.append({
                    "role": "adam",
                    "content": conv.get('adam_response', '')
                })
        
        return {
            "user_id": user_id,
            "mood": mood_score,
            "related_themes": list(related_themes),
            "conversation_history": conversation_history
        }

if __name__ == "__main__":
    # Initialize Adam
    adam = AdamAI()
    
    print("AdamAI is ready. Type 'exit' to end our conversation.")
    print("*molds clay* Ask me anything...")
    
    # Simple conversation loop
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("*carefully sets clay down* Until we meet again...")
                break
                
            response = adam.respond("console_user", user_input)
            print(f"\nAdam: {response}")
            
        except KeyboardInterrupt:
            print("\n*brushes clay from hands* Farewell...")
            break
        except Exception as e:
            print("*clay cracks* Oh dear, something went wrong...")
            logger.error(f"Conversation error: {str(e)}")
            break