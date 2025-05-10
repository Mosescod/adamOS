# emotional_personality.py
from transformers import pipeline
import numpy as np
from typing import Dict
import re

class EmotionalModel:
    def __init__(self):
        # Emotion detection model
        self.emotion_classifier = pipeline(
            "text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=5
        )
        
        # Personality configuration
        self.personality_traits = {
            'humility': 0.9,
            'compassion': 0.8,
            'wisdom': 0.95,
            'patience': 0.85
        }
        
        # Emotion weight mapping
        self.emotion_weights = {
            'joy': 0.9, 'admiration': 0.8, 'gratitude': 0.85,
            'neutral': 0.5, 'curiosity': 0.6,
            'anger': 0.2, 'fear': 0.3, 'sadness': 0.1
        }
        
        # Content safety filters
        self.safety_filters = {
            'offensive': [
                r"\b(?:kill|die|stupid|hate)\b",
                r"allah.*(?:fake|false)"
            ],
            'sensitive': [
                r"\b(?:suicide|abuse|rape)\b"
            ]
        }

    def analyze(self, text: str) -> Dict:
        """Analyze emotional content of text"""
        results = self.emotion_classifier(text)[0]
        emotion_scores = {r['label']: r['score'] for r in results}
        
        # Calculate weighted mood score
        mood = sum(
            self.emotion_weights.get(emotion, 0.5) * score
            for emotion, score in emotion_scores.items()
        )
        
        return {
            'dominant_emotion': max(emotion_scores, key=emotion_scores.get),
            'mood_score': np.clip(mood, 0, 1),
            'is_urgent': any(e in emotion_scores for e in ['fear', 'grief', 'desperation']),
            'emotion_profile': emotion_scores
        }

    def assess_safety(self, text: str) -> Dict:
        """Check content safety and appropriateness"""
        text_lower = text.lower()
        is_offensive = any(
            re.search(pattern, text_lower)
            for pattern in self.safety_filters['offensive']
        )
        is_sensitive = any(
            re.search(pattern, text_lower)
            for pattern in self.safety_filters['sensitive']
        )
        
        return {
            'is_offensive': is_offensive,
            'is_sensitive': is_sensitive,
            'requires_care': is_sensitive or is_offensive
        }

    def get_personality_response(self, emotion_state: Dict) -> str:
        """Generate personality-appropriate response markers"""
        mood = emotion_state['mood_score']
        
        if emotion_state['is_urgent']:
            return "*quickly reaches out* This seems important... "
        elif mood < 0.3:
            return "*speaks softly* I sense some heaviness... "
        elif mood > 0.7:
            return "*molds clay joyfully* What a wonderful question! "
        elif 0.4 < mood < 0.6:
            return "*tilts head* Let me think about that... "
        else:
            return "*carefully shapes clay* "