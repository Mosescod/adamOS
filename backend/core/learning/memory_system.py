import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from transformers import pipeline
from config import Config
import random
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryDatabase:
    def __init__(self, db_uri: str = (Config.MONGODB_URI)):
        self.client = MongoClient(db_uri)
        self.db = self.client (Config.DB_NAME)
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

    def log_conversation(self, user_id: str, messages: List[Dict]) -> str:
        """Store a conversation with timestamp"""
        conv_id = str(uuid.uuid4())
        self.conversations.insert_one({
            "_id": conv_id,
            "user_id": user_id,
            "messages": messages,
            "timestamp": datetime.utcnow(),
            "analyzed": False
        })
        logger.info(f"Logged conversation {conv_id} for user {user_id}")
        return conv_id

    def get_user_conversations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversations for a user"""
        return list(self.conversations.find(
            {"user_id": user_id},
            sort=[("timestamp", -1)],
            limit=limit
        ))

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
        logger.info(f"Stored summary for conversation {summary_data['conv_id']}")

    def find_related_summaries(self, user_id: str, topics: List[str], limit: int = 3) -> List[Dict]:
        """Find past summaries matching topics"""
        return list(self.summaries.find({
            "user_id": user_id,
            "topics": {"$in": topics}
        }).sort("timestamp", -1).limit(limit))