import time
from typing import Dict, Optional
import logging
from logging.handlers import RotatingFileHandler
from core.knowledge.knowledge_db import KnowledgeRetriever
from core.knowledge.sacred_scanner import SacredScanner
from core.knowledge.synthesizer import UniversalSynthesizer
from core.knowledge.mind_integrator import MindIntegrator
from core.personality.emotional_model import EmotionalModel
from core.personality.general_personality import GeneralPersonality
from core.learning.memory_system import MemoryDatabase
import os
from dotenv import load_dotenv

def configure_logging():
    """Configure dual logging - file and console"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Main logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler (for all logs)
    file_handler = RotatingFileHandler(
        'logs/adam_system.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler (only ERROR and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Only show errors in console
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Special ready logger for console
    ready_logger = logging.getLogger('adam_ready')
    ready_logger.propagate = False
    ready_handler = logging.StreamHandler()
    ready_handler.setLevel(logging.INFO)
    ready_handler.setFormatter(logging.Formatter('%(message)s'))
    ready_logger.addHandler(ready_handler)

    # Suppress sentence_transformers logs
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)

    # Suppress duplicate root logs
    logging.getLogger().handlers = []

# Call this at the start of your application
configure_logging()

load_dotenv()

class AdamAI:
    def __init__(self):
        """Initialize with silent logging"""
        self._silent_init()
        self._announce_ready()

    def _silent_init(self):
        """Perform initialization with logs going to file only"""
        try:
            self.db = KnowledgeRetriever()
            self.scanner = SacredScanner(self.db)
            self.synthesizer = UniversalSynthesizer(self.db)
            self.integrator = MindIntegrator()
            self.emotion = EmotionalModel()
            self.safety = GeneralPersonality()
            self.memory = MemoryDatabase()

        
        
            # Warm up components
            self._initialize_system()
            logging.getLogger('adam.system').info("AdamAI system initialized")

        except Exception as e:
            logging.getLogger('adam.system').critical(f"Initialization failed: {str(e)}")
            raise

    def _announce_ready(self):
        """Show ready message in console"""
        ready_logger = logging.getLogger('adam_ready')
        ready_logger.info("\n*shapes clay* Adam is ready to converse")
        ready_logger.info("Type your questions (or 'exit' to end)\n")

    def _initialize_system(self):
        """Initialize system components"""
        logging.getLogger("Building thematic index...")
        self.scanner._refresh_thematic_index()
    
        if os.getenv("BACKFILL_EMBEDDINGS", "false").lower() == "true":
            logging.getLogger("Backfilling embeddings...")
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
            try:
                scan_results = self.scanner.scan(message, context)
            except Exception as scan_error:
                if "text index required" in str(scan_error):
                    logging.error("Text index missing - attempting to create...")
                    self.db.create_text_index()
                    scan_results = self.scanner.scan(message, context)  # Retry
                else:
                    raise

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
            logging.getLogger(response)

            return response
            
        except Exception as e:
            logging.getLogger(f"Response generation failed: {str(e)}", exc_info=True)
            if "text index" in str(e):
                return "*reshapes clay* My knowledge needs reorganization... please ask again momentarily"
            return "*clay crumbles* My thoughts are scattered... please ask again"

    def _store_conversation(self, user_id: str, user_msg: str, adam_response: str):
        """Store conversation in memory"""
        self.memory.store_conversation(
            user_id=user_id,
            user_message=user_msg,
            adam_response=adam_response
        )
        logging.getLogger(f"Stored conversation for user {user_id}")

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
    try:
        # This will show nothing in console until ready
        adam = AdamAI()
        
        # Simple conversation loop
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n*carefully sets clay down* Until we meet again...")
                    break
                    
                response = adam.respond("console_user", user_input)
                print(f"Adam: {response}")
                
            except KeyboardInterrupt:
                print("\n*brushes clay from hands* Farewell...")
                break
            except Exception as e:
                logging.getLogger(f"Conversation error: {str(e)}")
                print("*clay cracks* Oh dear, something went wrong...")
                
    except Exception as e:
        # Critical errors still show in console
        print(f"*clay shatters* System failed to initialize: {str(e)}")