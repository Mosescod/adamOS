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
        """
        Quran-first knowledge retrieval.
        Returns: {'verses': [], 'wisdom': []} (sources anonymized)
        """
        try:
            # 1. Hybrid Search
            query_embedding = self.embedder.encode(question)
            semantic_results = {
                'quran': self.db.search(
                    source=KnowledgeSource.QURAN,
                    vector=query_embedding,
                    similarity_threshold=0.7
                ),
                'other': self.db.search(
                    query=question,
                    exclude_sources=[KnowledgeSource.QURAN],
                    limit=5
                )
            }

            # 2. Expand with Quranic themes
            expanded = {
                'quran': semantic_results['quran'] + self._expand_quran_themes(question),
                'other': semantic_results['other']
            }

            # 3. Filter conflicts (non-Quran matches must not contradict Quran)
            filtered = {
                'quran': expanded['quran'],
                'other': [
                    item for item in expanded['other']
                    if not self._contradicts_quran(item, expanded['quran'])
                ]
            }

            return {
                'verses': filtered['quran'][:3],  # Always prioritize Quran
                'wisdom': filtered['other'][:2]   # Secondary sources
            }

        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            return {'verses': [], 'wisdom': []}

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