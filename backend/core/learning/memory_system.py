import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from transformers import pipeline
from config import Config
import random
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryDatabase:
    def __init__(self, db_uri: str = (os.getenv("MONGODB_URI"))):
        self.client = MongoClient(db_uri)
        self.db = self.client[os.getenv("DB_NAME", "AdamAI-MemoryDB")]
        self.conversations = self.db.conversations
        self.summaries = self.db.summaries
        self._create_indexes()

    def _create_indexes(self):
        """Create necessary database indexes"""
        self.conversations.create_index([("user_id", ASCENDING)])
        self.conversations.create_index([("timestamp", ASCENDING)])
        self.summaries.create_index([("user_id", ASCENDING)])
        self.summaries.create_index([("topics", ASCENDING)])
        self.summaries.create_index([("timestamp", ASCENDING)])

    def log_conversation(self, user_id: str, user_message: str, adam_response: str) -> str:
        """Store a conversation with timestamp"""
        conv_id = str(uuid.uuid4())
        self.conversations.insert_one({
            "_id": conv_id,
            "user_id": user_id,
            "user_message": user_message,
            "adam_response": adam_response,
            "timestamp": datetime.utcnow(),
            "analyzed": False
        })
        logger.info(f"Logged conversation {conv_id} for user {user_id}")
        return conv_id

    def store_conversation(self, user_id: str, user_message: str, adam_response: str) -> str:
        """Alias for log_conversation"""
        return self.log_conversation(user_id, user_message, adam_response)

    def get_user_conversations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversations for a user"""
        return list(self.conversations.find(
            {"user_id": user_id},
            sort=[("timestamp", -1)],
            limit=limit
        ))

    def get_recent_conversations(self, user_id: str, limit: int = 3) -> List[Dict]:
        """Get recent conversations (alias for get_user_conversations)"""
        return self.get_user_conversations(user_id, limit)

    def get_unanalyzed_conversations(self, limit: int = 10) -> List[Dict]:
        """Get conversations needing analysis"""
        return list(self.conversations.find(
            {"analyzed": False},
            sort=[("timestamp", -1)],
            limit=limit
        ))

    def mark_as_analyzed(self, conv_id: str):
        """Flag conversation as analyzed"""
        self.conversations.update_one(
            {"_id": conv_id},
            {"$set": {"analyzed": True}}
        )

    def store_summary(self, summary_data: Dict):
        """Store conversation analysis"""
        self.summaries.insert_one(summary_data)
        logger.info(f"Stored summary for conversation {summary_data.get('conv_id', 'unknown')}")

    def find_related_summaries(self, user_id: str, message: str = None, limit: int = 3) -> List[Dict]:
        """Find related summaries - handles message or direct topics"""
        topics = self._extract_topics(message) if message else []
    
        query = {"user_id": user_id}
        if topics:
            query["topics"] = {"$in": topics}
        
        return list(self.summaries.find(query).sort("timestamp", -1).limit(limit))

    def _extract_topics(self, text: str) -> List[str]:
        """Improved topic extraction logic"""
        text_lower = text.lower()
        topics = []
        
        # Common Islamic topics
        islamic_topics = {
            'mercy': ['mercy', 'compassion', 'rahma'],
            'forgiveness': ['forgive', 'pardon', 'maghfira'],
            'prayer': ['pray', 'salah', 'dua'],
            'prophets': ['prophet', 'muhammad', 'isa', 'musa']
        }
        
        for theme, keywords in islamic_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(theme)
        
        return topics