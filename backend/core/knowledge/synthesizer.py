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
            'mercy': ['forgive', 'compassion', 'kind']
        }

    def analyze_sources(self, question: str) -> Dict:
        """Retrieve & blend knowledge from all sources."""
        # Step 1: Fetch relevant content from all sources
        results = {
            'quran': self.db.search(source=KnowledgeSource.QURAN, query=question),
            'bible': self.db.search(source=KnowledgeSource.BIBLE, query=question),
            'books': self.db.search(source=KnowledgeSource.BOOK, query=question)
        }

        # Step 2: Extract universal themes (ignoring source origins)
        all_texts = [item['content'] for sublist in results.values() for item in sublist]
        themes = self._extract_universal_themes(all_texts)

        # Step 3: Merge into cohesive wisdom
        blended = self._blend_wisdom(all_texts, themes)
        return {
            'themes': themes,
            'response': blended,
            'mood_cues': self._detect_emotional_tone(all_texts)
        }

    def _extract_universal_themes(self, texts: List[str]) -> List[str]:
        """Identify cross-source themes using TF-IDF."""
        if not texts:
            return []
        
        self.vectorizer.fit(texts)
        terms = self.vectorizer.get_feature_names_out()
        scores = np.sum(self.vectorizer.transform(texts).toarray(), axis=0)
        top_terms = [terms[i] for i in np.argsort(scores)[-3:][::-1]]
        
        # Map terms to higher-level themes
        themes = []
        for term in top_terms:
            for theme, keywords in self.theme_hierarchy.items():
                if term in keywords:
                    themes.append(theme)
        return list(set(themes))

    def blend(self, quran: List[Dict], other: List[Dict], context: Dict = None) -> Dict:
        """Combine knowledge sources"""
        if quran:
            return {
                'content': quran[0]['content'],
                'source': 'quran',
                'reference': quran[0].get('metadata', {}).get('reference', '')
            }
        elif other:
            return {
                'content': other[0]['content'],
                'source': 'other'
            }
        return None
    pass

    def _detect_emotional_tone(self, texts: List[str]) -> float:
        """Analyze sentiment across sources (0=sad, 1=joyful)."""
        positive_words = ['hope', 'love', 'peace']
        negative_words = ['lonely', 'suffering', 'pain']
        
        score = 0.5  # Neutral baseline
        for text in texts:
            if any(word in text for word in positive_words):
                score += 0.1
            if any(word in text for word in negative_words):
                score -= 0.1
        return np.clip(score, 0, 1)