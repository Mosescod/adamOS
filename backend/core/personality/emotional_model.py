import random
from typing import Dict, List, Tuple
from datetime import datetime
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


logger = logging.getLogger(__name__)

class EmotionalModel:
    """Advanced emotional modeling system with mood tracking and response adaptation."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.base_mood = 0.7  # Neutral-positive baseline (0-1 scale)
        self.mood = self.base_mood
        self.mood_history = []  # List of (timestamp, mood) tuples
        self.last_update = datetime.now()
        self.interaction_history = []  # Track all interactions
        
        # Emotional triggers and weights
        self.emotion_weights = {
            'positive': {
                'joy': 0.15,
                'love': 0.12,
                'peace': 0.10,
                'hope': 0.08
            },
            'negative': {
                'anger': -0.18,
                'sadness': -0.15,
                'fear': -0.12,
                'shame': -0.10
            }
        }
        
        # Initialize vectorizer for emotional text analysis
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english'
        )
        self._initialize_vectorizer()
    
    def _initialize_vectorizer(self):
        """Initialize the emotional text vectorizer."""
        sample_texts = [
            " ".join(self.emotion_weights['positive'].keys()),
            " ".join(self.emotion_weights['negative'].keys())
        ]
        self.vectorizer.fit(sample_texts)
    
    def analyze_emotional_context(self, text: str) -> Dict:
        """
        Perform comprehensive emotional analysis of input text.
        
        Returns:
            Dictionary containing:
            - primary_emotion: Dominant detected emotion
            - secondary_emotions: Other detected emotions
            - intensity: Emotional intensity (0-1)
            - suggested_response_style: Recommended response approach
        """
        analysis = {
            'primary_emotion': None,
            'secondary_emotions': [],
            'intensity': 0.5,
            'suggested_response_style': 'neutral'
        }
        
        if not text or not isinstance(text, str):
            return analysis
            
        text_lower = text.lower()
        
        # Detect emotions and calculate scores
        emotion_scores = {}
        for category, emotions in self.emotion_weights.items():
            for emotion, weight in emotions.items():
                if emotion in text_lower:
                    emotion_scores[emotion] = weight
        
        # Semantic analysis for more subtle detection
        semantic_emotions = self._detect_semantic_emotions(text)
        for emotion, score in semantic_emotions.items():
            if emotion in emotion_scores:
                emotion_scores[emotion] += score * 0.5
            else:
                emotion_scores[emotion] = score * 0.5
        
        if emotion_scores:
            # Sort emotions by absolute score
            sorted_emotions = sorted(
                emotion_scores.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            analysis['primary_emotion'] = sorted_emotions[0][0]
            analysis['secondary_emotions'] = [e[0] for e in sorted_emotions[1:3] if abs(e[1]) > 0.05]
            
            # Calculate intensity (absolute value of strongest emotion)
            analysis['intensity'] = min(1.0, abs(sorted_emotions[0][1]) * 2)
            
            # Determine response style
            analysis['suggested_response_style'] = self._determine_response_style(
                analysis['primary_emotion'],
                analysis['intensity']
            )
        
        return analysis
    
    def _detect_semantic_emotions(self, text: str) -> Dict:
        """Detect emotions through semantic similarity."""
        emotion_scores = {}
        
        # Vectorize input text
        try:
            text_vec = self.vectorizer.transform([text])
            
            # Compare with positive emotions
            pos_text = " ".join(self.emotion_weights['positive'].keys())
            pos_vec = self.vectorizer.transform([pos_text])
            pos_sim = cosine_similarity(text_vec, pos_vec)[0][0]
            
            # Compare with negative emotions
            neg_text = " ".join(self.emotion_weights['negative'].keys())
            neg_vec = self.vectorizer.transform([neg_text])
            neg_sim = cosine_similarity(text_vec, neg_vec)[0][0]
            
            # Calculate relative scores
            if pos_sim > neg_sim:
                for emotion in self.emotion_weights['positive'].keys():
                    emotion_scores[emotion] = pos_sim * 0.5
            else:
                for emotion in self.emotion_weights['negative'].keys():
                    emotion_scores[emotion] = neg_sim * -0.5
            
        except Exception as e:
            logger.error(f"Semantic emotion detection failed: {str(e)}")
        
        return emotion_scores
    
    def _determine_response_style(self, primary_emotion: str, intensity: float) -> str:
        """Determine appropriate response style based on emotion."""
        if primary_emotion in self.emotion_weights['positive']:
            if intensity > 0.7:
                return 'celebratory'
            elif intensity > 0.4:
                return 'supportive'
            return 'neutral_positive'
        
        elif primary_emotion in self.emotion_weights['negative']:
            if intensity > 0.7:
                return 'comforting'
            elif intensity > 0.4:
                return 'gentle'
            return 'neutral_reassuring'
        
        return 'neutral'
    
    def update_mood(self, user_input: str) -> None:
        """Update mood state based on user input."""
        analysis = self.analyze_emotional_context(user_input)
        
        if analysis['primary_emotion']:
            # Get weight for detected emotion
            emotion = analysis['primary_emotion']
            weight = 0.0
            
            for category in self.emotion_weights.values():
                if emotion in category:
                    weight = category[emotion]
                    break
            
            # Apply mood change with intensity modulation
            mood_change = weight * analysis['intensity']
            
            # Apply time decay since last update
            time_passed = datetime.now() - self.last_update
            decay_factor = max(0.3, 1 - (time_passed.total_seconds() / 7200))  # Decays over 2 hours
            
            # Calculate new mood
            self.mood = max(0.1, min(0.9, (self.mood * decay_factor) + mood_change))
            
            # Record mood history
            self.mood_history.append((datetime.now(), self.mood))
            self.last_update = datetime.now()
    
    def record_interaction(self, user_input: str, ai_response: str) -> None:
        """Record complete interaction for longitudinal analysis."""
        self.interaction_history.append({
            'timestamp': datetime.now(),
            'input': user_input,
            'response': ai_response,
            'mood_at_time': self.mood
        })
    
    def get_mood_modifiers(self) -> Tuple[float, float]:
        """
        Get current mood modifiers for response generation.
        
        Returns:
            tuple: (elaboration_modifier, positivity_modifier)
        """
        if self.mood > 0.8:
            return (1.2, 1.3)  # More elaborate and positive
        elif self.mood > 0.6:
            return (1.1, 1.1)
        elif self.mood > 0.4:
            return (1.0, 1.0)
        elif self.mood > 0.2:
            return (0.9, 0.9)
        return (0.8, 0.7)  # Less elaborate and more reserved
    
    def format_response(self, response: str) -> str:
        """
        Format response with emotional markers based on current state.
        
        Args:
            response: Raw response text
            
        Returns:
            Formatted response with emotional markers
        """
        mood_level = self._get_mood_level()
        elaboration_mod, positivity_mod = self.get_mood_modifiers()
        
        # Apply mood-based formatting
        formatted = self._apply_mood_formatting(response, mood_level)
        
        # Add gestures based on mood
        if random.random() < (0.3 * elaboration_mod):
            formatted += self._get_gesture(mood_level)
            
        return formatted
    
    def _get_mood_level(self) -> str:
        """Get current mood level category."""
        if self.mood > 0.8:
            return 'high'
        elif self.mood > 0.6:
            return 'moderate_high'
        elif self.mood > 0.4:
            return 'moderate'
        elif self.mood > 0.2:
            return 'moderate_low'
        return 'low'
    
    def _apply_mood_formatting(self, response: str, mood_level: str) -> str:
        """Apply mood-specific formatting to response."""
        formats = {
            'high': [
                ("*bright eyes* ", ""),
                ("*joyful shaping* ", " *smiles*")
            ],
            'moderate_high': [
                ("*pleased tone* ", ""),
                ("", " *nods*")
            ],
            'moderate': [
                ("", ""),
                ("*calmly* ", "")
            ],
            'moderate_low': [
                ("*softly* ", " *sighs*"),
                ("*quiet tone* ", "")
            ],
            'low': [
                ("*heavy hands* ", " *bows*"),
                ("*weary voice* ", " *slowly shapes clay*")
            ]
        }
        
        prefix, suffix = random.choice(formats[mood_level])
        return prefix + response + suffix
    
    def _get_gesture(self, mood_level: str) -> str:
        """Get appropriate gesture for mood level."""
        gestures = {
            'high': [
                "\n*offers clay flower*",
                "\n*shapes joyful figure*"
            ],
            'moderate_high': [
                "\n*gestures warmly*",
                "\n*shapes small gift*"
            ],
            'moderate': [
                "\n*adjusts clay*",
                "\n*tilts head*"
            ],
            'moderate_low': [
                "\n*smooths clay slowly*",
                "\n*offers simple shape*"
            ],
            'low': [
                "\n*clay cracks slightly*",
                "\n*hands move heavily*"
            ]
        }
        return random.choice(gestures[mood_level])
    
    def get_mood_description(self) -> str:
        """Get textual description of current mood."""
        descriptions = {
            'high': "*eyes bright* My heart is light with remembrance of the Creator",
            'moderate_high': "*calm demeanor* I am at peace",
            'moderate': "*neutral tone* I am contemplative",
            'moderate_low': "*slight sigh* The weight of memory sits with me",
            'low': "*bowed head* The sorrows of the world weigh heavy"
        }
        return descriptions[self._get_mood_level()]