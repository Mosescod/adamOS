import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from transformers import pipeline
from .memory_system import MemoryDatabase
import random
import numpy as np
import logging 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveLearner:
    def __init__(self, memory_db: MemoryDatabase):
        self.memory = memory_db
        self.summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn",
            device="cpu"  # Change to "cuda" if using GPU
        )
        self.sentiment = pipeline(
            "text-classification",
            model="finiteautomata/bertweet-base-sentiment-analysis",
            device="cpu"
        )
        self.theme_keywords = {
            'mercy': ['forgive', 'mercy', 'compassion', 'pardon'],
            'prophets': ['muhammad', 'isa', 'musa', 'prophet'],
            'prayer': ['salah', 'pray', 'worship', 'dua'],
            'afterlife': ['hereafter', 'judgment', 'paradise', 'hell']
        }

    def analyze_conversation(self, conv_id: str) -> Optional[Dict]:
        """Generate and store conversation insights"""
        conv = self.memory.conversations.find_one({"_id": conv_id})
        if not conv:
            return None

        # Prepare conversation text
        dialog_text = self._prepare_conversation_text(conv['messages'])
        
        try:
            # Generate summary
            summary = self._generate_summary(dialog_text)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(summary)
            
            # Extract topics
            topics = self._extract_topics(dialog_text)
            
            # Prepare analysis data
            analysis = {
                "conv_id": conv_id,
                "user_id": conv["user_id"],
                "summary": summary,
                "sentiment": sentiment["label"],
                "sentiment_score": float(sentiment["score"]),
                "topics": topics,
                "timestamp": datetime.utcnow()
            }
            
            # Store results
            self.memory.store_summary(analysis)
            self.memory.mark_as_analyzed(conv_id)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed for {conv_id}: {str(e)}")
            return None

    def _prepare_conversation_text(self, messages: List[Dict]) -> str:
        """Convert message history to text"""
        return "\n".join(
            f"{m['role'].capitalize()}: {m['content']}" 
            for m in messages
        )

    def _generate_summary(self, text: str) -> str:
        """Generate conversation summary"""
        if len(text.split()) < 50:  # Skip very short conversations
            return "Brief discussion"
        
        result = self.summarizer(
            text,
            max_length=130,
            min_length=30,
            do_sample=False
        )
        return result[0]['summary_text']

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze emotional tone"""
        result = self.sentiment(text)
        return {
            "label": result[0]['label'],
            "score": result[0]['score']
        }

    def _extract_topics(self, text: str) -> List[str]:
        """Identify key discussion topics"""
        text_lower = text.lower()
        topics = []
        
        for theme, keywords in self.theme_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(theme)
                
        return topics if topics else ["general"]