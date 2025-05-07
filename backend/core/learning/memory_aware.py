import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from transformers import pipeline
from memory_system import MemoryDatabase
from interactive_learner import InteractiveLearner
import random
import numpy as np
import logging


class AdamAI:
    def __init__(self, memory_db: MemoryDatabase):
        self.memory = memory_db
        self.learner = InteractiveLearner(memory_db)
        self.analysis_interval = 5  # Analyze every Nth conversation
        
    def respond(self, user_id: str, message: str) -> str:
        """Generate response using memory context"""
        # 1. Check for related past discussions
        related = self._find_related_discussions(user_id, message)
        
        # 2. Generate base response
        if related:
            memory_context = self._create_memory_context(related)
            response = f"{memory_context} {self._generate_response(message)}"
        else:
            response = self._generate_response(message)
            
        # 3. Log interaction
        self._log_interaction(user_id, message, response)
        
        # 4. Periodically analyze conversations
        if random.randint(1, self.analysis_interval) == 1:
            self._analyze_recent_conversations(user_id)
            
        return response

    def _find_related_discussions(self, user_id: str, message: str) -> List[Dict]:
        """Find relevant past conversations"""
        # First extract topics from current message
        message_topics = self.learner._extract_topics(message)
        
        if not message_topics:
            return []
            
        # Find related summaries
        return self.memory.find_related_summaries(user_id, message_topics)

    def _create_memory_context(self, related_summaries: List[Dict]) -> str:
        """Create recall phrase based on past discussions"""
        topics = set()
        for summary in related_summaries:
            topics.update(summary['topics'])
            
        topics_str = ", ".join(list(topics)[:2])  # Max 2 topics
        return random.choice([
            f"*recalls clay* We discussed {topics_str} before...",
            f"*shapes familiar clay* Regarding {topics_str}...",
            f"*brushes old clay* As we spoke of {topics_str}..."
        ])

    def _generate_response(self, message: str) -> str:
        """Generate standard response (simplified for example)"""
        return random.choice([
            "*kneads clay* The Divine wisdom teaches us...",
            "*shapes clay* The truth is...",
            "*offers clay* Let me share..."
        ])

    def _log_interaction(self, user_id: str, user_msg: str, adam_response: str):
        """Store conversation turn"""
        self.memory.log_conversation(user_id, [
            {"role": "user", "content": user_msg},
            {"role": "adam", "content": adam_response}
        ])

    def _analyze_recent_conversations(self, user_id: str):
        """Analyze recent unanalyzed conversations"""
        unanalyzed = self.memory.get_unanalyzed_conversations()
        for conv in unanalyzed:
            self.learner.analyze_conversation(conv["_id"])