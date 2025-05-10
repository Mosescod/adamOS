from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from .knowledge_db import KnowledgeSource
from collections import Counter

class UniversalSynthesizer:
    def __init__(self, knowledge_db):
        self.db = knowledge_db
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.theme_hierarchy = {
            'comfort': ['lonely', 'sad', 'ease', 'peace', 'solace', 'heal'],
            'mercy': ['forgive', 'compassion', 'kind', 'merciful', 'pardon', 'grace'],
            'wisdom': ['knowledge', 'understanding', 'insight', 'learn', 'teach'],
            'prayer': ['supplication', 'dua', 'worship', 'invocation', 'pray'],
            'prophets': ['muhammad', 'isa', 'musa', 'abraham', 'david', 'solomon']
        }
        self.theme_weights = {
            'quran': 1.5,
            'bible': 1.2,
            'book': 1.0
        }

    def blend(self, verses: List[Dict], wisdom: List[Dict], context: Dict = None) -> Dict:
        """Enhanced knowledge blending with multi-source synthesis"""
        if not verses and not wisdom:
            return self._empty_response()
        
        # Combine and weight sources
        all_sources = self._combine_sources(verses, wisdom)
        
        # Extract unified content
        unified_content = self._create_unified_content(all_sources)
        
        # Analyze themes across all sources
        themes = self._analyze_themes(all_sources)
        primary_theme = self._determine_primary_theme(themes)
        
        # Calculate confidence
        confidence = self._calculate_confidence(all_sources)
        
        # Detect emotional tone
        mood_score = self._analyze_mood(all_sources)
        
        return {
            'content': unified_content,
            'primary_theme': primary_theme,
            'sources': all_sources[:1],  # Primary source
            'supporting_sources': all_sources[1:4],  # Top 3 supporting
            'confidence': confidence,
            'mood_score': mood_score,
            'detected_themes': themes
        }

    def _combine_sources(self, verses: List[Dict], wisdom: List[Dict]) -> List[Dict]:
        """Combine and weight sources by importance"""
        combined = []
        
        # Add Quran verses first with highest weight
        for verse in verses:
            verse['weight'] = self.theme_weights.get('quran', 1.5)
            combined.append(verse)
        
        # Add other religious texts
        for wisdom_text in wisdom:
            source_type = wisdom_text.get('source', '').lower()
            weight = self.theme_weights.get(source_type, 1.0)
            wisdom_text['weight'] = weight
            combined.append(wisdom_text)
        
        # Sort by weight then score
        return sorted(combined, 
                     key=lambda x: (x['weight'], x.get('score', 0)), 
                     reverse=True)

    def _create_unified_content(self, sources: List[Dict]) -> str:
        """Create coherent response from multiple sources"""
        if not sources:
            return "I need more time to contemplate this question"
        
        # Start with primary source
        primary = sources[0]
        content = primary['content']
        
        # Add supporting points if available
        if len(sources) > 1:
            supporting = sources[1]
            content += f"\n\nAs mentioned in {supporting.get('source', 'another source')}:"
            content += f"\n{supporting['content'][:200]}..."
        
        return content

    def _analyze_themes(self, sources: List[Dict]) -> List[str]:
        """Identify themes across all sources"""
        texts = [s['content'] for s in sources]
        tags = []
        
        # Get tags from all sources
        for s in sources:
            tags.extend(s.get('tags', []))
        
        # Analyze text content
        if texts:
            self.vectorizer.fit(texts)
            terms = self.vectorizer.get_feature_names_out()
            scores = np.sum(self.vectorizer.transform(texts).toarray(), axis=0)
            top_terms = [terms[i] for i in np.argsort(scores)[-5:][::-1]]
            
            # Match terms to themes
            detected = []
            for term in top_terms + tags:
                for theme, keywords in self.theme_hierarchy.items():
                    if term in keywords and theme not in detected:
                        detected.append(theme)
            
            return detected
        
        return []

    def _determine_primary_theme(self, themes: List[str]) -> str:
        """Select most relevant theme"""
        if not themes:
            return 'default'
        
        # Count theme occurrences
        counts = Counter(themes)
        return counts.most_common(1)[0][0]

    def _calculate_confidence(self, sources: List[Dict]) -> float:
        """Calculate confidence based on source quality and quantity"""
        if not sources:
            return 0.0
            
        base_conf = min(0.7 + (len(sources) * 0.05), 0.95)
        weighted_conf = base_conf * sources[0]['weight']
        return min(weighted_conf, 1.0)

    def _analyze_mood(self, sources: List[Dict]) -> float:
        """Analyze emotional tone across sources (0=sad, 1=joyful)"""
        positive = ['hope', 'love', 'peace', 'joy', 'mercy']
        negative = ['lonely', 'suffering', 'pain', 'fear', 'anger']
        
        score = 0.5
        for s in sources:
            text = s['content'].lower()
            score += sum(0.02 for word in positive if word in text)
            score -= sum(0.02 for word in negative if word in text)
        
        return np.clip(score, 0.1, 0.9)

    def _empty_response(self) -> Dict:
        """Return empty response structure"""
        return {
            'content': "I need more time to contemplate this question",
            'primary_theme': 'default',
            'sources': [],
            'supporting_sources': [],
            'confidence': 0.0,
            'mood_score': 0.5
        }