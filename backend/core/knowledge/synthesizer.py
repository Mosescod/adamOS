from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from .knowledge_db import KnowledgeSource

class UniversalSynthesizer:
    def __init__(self, knowledge_db):
        self.db = knowledge_db
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.theme_hierarchy = {
            'comfort': ['lonely', 'sad', 'ease'],
            'mercy': ['forgive', 'compassion', 'kind'],
            'wisdom': ['knowledge', 'understanding', 'insight']
        }

    def blend(self, verses: List[Dict], wisdom: List[Dict], context: Dict = None) -> Dict:
        """Enhanced knowledge blending with context awareness"""
        if not verses and not wisdom:
            return {
                'content': "I need more time to contemplate this question",
                'primary_theme': 'default',
                'sources': [],
                'confidence': 0.0
            }
        
        # Combine all sources
        all_sources = verses + wisdom
        all_texts = [s['content'] for s in all_sources]
        
        # Determine primary source (Quran first)
        primary_source = verses[0] if verses else wisdom[0]
        
        # Extract themes
        themes = self._extract_universal_themes(all_texts)
        primary_theme = themes[0] if themes else 'default'
        
        # Calculate confidence based on source quality
        confidence = self._calculate_confidence(verses, wisdom)
        
        # Get emotional tone
        mood_cues = self._detect_emotional_tone(all_texts)
        
        return {
            'content': primary_source['content'],
            'primary_theme': primary_theme,
            'sources': [primary_source],
            'supporting_sources': all_sources[:3],
            'confidence': confidence,
            'mood_score': mood_cues
        }

    def _extract_universal_themes(self, texts: List[str]) -> List[str]:
        """Identify cross-source themes using TF-IDF"""
        if not texts:
            return []
        
        self.vectorizer.fit(texts)
        terms = self.vectorizer.get_feature_names_out()
        scores = np.sum(self.vectorizer.transform(texts).toarray(), axis=0)
        top_terms = [terms[i] for i in np.argsort(scores)[-3:][::-1]]
        
        themes = []
        for term in top_terms:
            for theme, keywords in self.theme_hierarchy.items():
                if term in keywords:
                    themes.append(theme)
        return list(set(themes))

    def _calculate_confidence(self, verses: List[Dict], wisdom: List[Dict]) -> float:
        """Calculate response confidence based on sources"""
        if verses:
            return min(0.9 + (len(verses) * 0.05), 1.0)
        elif wisdom:
            return min(0.7 + (len(wisdom) * 0.05), 0.9)
        return 0.5

    def _detect_emotional_tone(self, texts: List[str]) -> float:
        """Analyze sentiment across sources (0=sad, 1=joyful)"""
        positive_words = ['hope', 'love', 'peace']
        negative_words = ['lonely', 'suffering', 'pain']
        
        score = 0.5
        for text in texts:
            if any(word in text for word in positive_words):
                score += 0.1
            if any(word in text for word in negative_words):
                score -= 0.1
        return np.clip(score, 0, 1)