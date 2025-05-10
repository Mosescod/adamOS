import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .knowledge_db import KnowledgeDatabase, KnowledgeSource
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SacredScanner:
    def __init__(self, knowledge_db: KnowledgeDatabase):
        """
        Quran-prioritized knowledge scanner for AdamAI.
        """
        self.db = knowledge_db
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.theme_hierarchy = {
            'mercy': ['forgive', 'compassion', 'kindness'],
            'comfort': ['lonely', 'sad', 'ease'],
            'prophets': ['muhammad', 'isa', 'musa']
        }
        self._refresh_thematic_index()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _refresh_thematic_index(self):
        """Auto-build theme index from DB with Quran focus"""
        self.thematic_index = {}
        for theme in self.theme_hierarchy:
            # Prioritize Quranic verses in thematic index
            self.thematic_index[theme] = (
                self.db.search(source=KnowledgeSource.QURAN, tags=[theme], limit=20) +
                self.db.search(source=KnowledgeSource.BIBLE, tags=[theme], limit=5) +
                self.db.search(source=KnowledgeSource.BOOK, tags=[theme], limit=3)
            )
        logger.info(f"Thematic index built with {sum(len(v) for v in self.thematic_index.values())} entries")

    def scan(self, question: str, context: Dict = None) -> Dict[str, List[Dict]]:
        """Quran-first knowledge retrieval with proper return format"""
        try:
            # Get Quran results
            quran_results = self.db.hybrid_search(
                query=question,
                source=KnowledgeSource.QURAN.value,  # Use .value for enum
                limit=3
            )
        
            # Get other results
            other_results = []
            for source in [KnowledgeSource.BIBLE, KnowledgeSource.BOOK]:
                results = self.db.hybrid_search(
                    query=question,
                    source=source.value,  # Use .value for enum
                    limit=2
                )
                other_results.extend(results)
        
            # Return with correct keys
            return {
                'quran': quran_results,
                'other': other_results,
                'verses': quran_results,  # Duplicate for compatibility
                'wisdom': other_results   # Duplicate for compatibility
            }
        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            return {'quran': [], 'other': [], 'verses': [], 'wisdom': []}

    def _expand_quran_themes(self, question: str) -> List[Dict]:
        """Find related Quranic verses through theme hierarchy"""
        related_verses = []
        for theme, keywords in self.theme_hierarchy.items():
            if any(keyword in question.lower() for keyword in keywords):
                related_verses.extend(self.thematic_index.get(theme, []))
        return related_verses

    def _contradicts_quran(self, item: Dict, quran_verses: List[Dict]) -> bool:
        """
        Check if non-Quran content contradicts Quranic verses.
        Simple keyword-based contradiction detection.
        """
        if not quran_verses:
            return False
            
        quran_keywords = set()
        for verse in quran_verses:
            quran_keywords.update(verse.get('tags', []))
        
        anti_keywords = {
            'mercy': ['harsh', 'unforgiving'],
            'comfort': ['despair', 'hopeless']
        }
        
        for theme in quran_keywords:
            if any(bad in item['content'].lower() 
                   for bad in anti_keywords.get(theme, [])):
                return True
        return False
    
    def _refresh_thematic_index(self):
        """Improved thematic index builder"""
        self.thematic_index = {}
        for theme, keywords in self.theme_hierarchy.items():
            # Search using tags instead of source
            quran_results = self.db.search(
                tags=[theme],
                source=KnowledgeSource.QURAN,
                limit=20
            )
            bible_results = self.db.search(
                tags=[theme],
                source=KnowledgeSource.BIBLE, 
                limit=5
            )
            book_results = self.db.search(
                tags=[theme],
                source=KnowledgeSource.BOOK,
                limit=3
            )
        
            self.thematic_index[theme] = quran_results + bible_results + book_results
    
        logger.info(f"Thematic index built with {sum(len(v) for v in self.thematic_index.values())} entries")