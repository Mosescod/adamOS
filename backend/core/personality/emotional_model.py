from transformers import pipeline  # pip install transformers
import numpy as np
from typing import Dict

class EmotionalModel:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=3
        )
        
    def analyze(self, text: str) -> Dict:
        """
        Detects emotion from user's question.
        Returns: {
            'dominant_emotion': 'sadness',
            'mood_score': 0.2,  # 0-1 (0=negative)
            'is_urgent': bool
        }
        """
        results = self.classifier(text)[0]
        emotion_scores = {r['label']: r['score'] for r in results}
        
        # Mood mapping (negative -> 0, positive -> 1)
        mood_map = {
            'sadness': 0.1, 'fear': 0.3, 
            'joy': 0.9, 'admiration': 0.8
        }
        
        # Calculate weighted mood
        mood = sum(
            mood_map.get(emotion, 0.5) * score 
            for emotion, score in emotion_scores.items()
        )
        
        return {
            'dominant_emotion': max(emotion_scores, key=emotion_scores.get),
            'mood_score': np.clip(mood, 0, 1),
            'is_urgent': any(e in emotion_scores for e in ['fear', 'desperation'])
        }