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
        self.db = knowledge_db
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.theme_hierarchy = {
            'mercy': ['forgive', 'compassion', 'kindness'],
            'comfort': ['lonely', 'sad', 'ease'],
            'prophets': ['muhammad', 'isa', 'musa']
        }
        self._refresh_thematic_index()

    def scan(self, question: str, context: Dict = None) -> Dict[str, List[Dict]]:
        """Enhanced Quran-first knowledge retrieval with context awareness"""
        try:
            # Get most relevant results regardless of source
            all_results = self.db.get_relevant_context(question, limit=10)
            
            # Separate by source
            quran_results = [r for r in all_results if r['source'] == KnowledgeSource.QURAN.value]
            other_results = [r for r in all_results if r['source'] != KnowledgeSource.QURAN.value]
            
            # Filter out contradictions
            filtered_other = [
                r for r in other_results 
                if not self._contradicts_quran(r, quran_results)
            ]
            
            # Add thematic expansion if Quran results are sparse
            if len(quran_results) < 3:
                quran_results.extend(self._expand_quran_themes(question))
                quran_results = quran_results[:3]
                
            return {
                'verses': quran_results,
                'wisdom': filtered_other,
                'all_results': all_results
            }
        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            return {'verses': [], 'wisdom': [], 'all_results': []}

    def _expand_quran_themes(self, question: str) -> List[Dict]:
        """Find related Quranic verses through theme hierarchy"""
        related_verses = []
        for theme, keywords in self.theme_hierarchy.items():
            if any(keyword in question.lower() for keyword in keywords):
                related_verses.extend(self.thematic_index.get(theme, []))
        return related_verses

    def _contradicts_quran(self, item: Dict, quran_verses: List[Dict]) -> bool:
        """Check if non-Quran content contradicts Quranic verses"""
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
            try:
                # Search using tags instead of source
                quran_results = self.db.search(
                    tags=[theme],
                    source=KnowledgeSource.QURAN,
                    limit=20
                ) or []  # Ensure we get an empty list if None is returned
            
                bible_results = self.db.search(
                    tags=[theme],
                    source=KnowledgeSource.BIBLE, 
                    limit=5
                ) or []
            
                book_results = self.db.search(
                    tags=[theme],
                    source=KnowledgeSource.BOOK,
                    limit=3
                ) or []
        
                self.thematic_index[theme] = quran_results + bible_results + book_results
        
            except Exception as e:
                logger.error(f"Error building index for theme {theme}: {str(e)}")
                self.thematic_index[theme] = []
    
        logger.info(f"Thematic index built with {sum(len(v) for v in self.thematic_index.values())} entries")