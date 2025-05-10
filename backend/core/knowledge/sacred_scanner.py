from logging.handlers import RotatingFileHandler
import os
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .knowledge_db import KnowledgeRetriever, KnowledgeSource
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from collections import defaultdict

def configure_logging():
    """Configure dual logging - file and console"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Main logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler (for all logs)
    file_handler = RotatingFileHandler(
        'logs/adam_system.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler (only ERROR and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Only show errors in console
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Special ready logger for console
    ready_logger = logging.getLogger('adam_ready')
    ready_logger.propagate = False
    ready_handler = logging.StreamHandler()
    ready_handler.setLevel(logging.INFO)
    ready_handler.setFormatter(logging.Formatter('%(message)s'))
    ready_logger.addHandler(ready_handler)

    # Suppress sentence_transformers logs
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)

# Call this at the start of your application
configure_logging()


class SacredScanner:
    def __init__(self, knowledge_db: KnowledgeRetriever):
        self.db = knowledge_db
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.theme_hierarchy = {
            'mercy': ['forgive', 'compassion', 'kindness', 'pardon', 'merciful'],
            'comfort': ['lonely', 'sad', 'ease', 'distress', 'anxiety', 'peace'],
            'prophets': ['muhammad', 'isa', 'musa', 'abraham', 'david', 'solomon'],
            'prayer': ['supplication', 'dua', 'worship', 'invocation'],
            'patience': ['perseverance', 'steadfast', 'endurance', 'trials']
        }
        self.thematic_index = defaultdict(list)
        self._refresh_thematic_index()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def scan(self, question: str, context: Optional[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Enhanced knowledge retrieval with comprehensive context search.
        
        Args:
            question: The question or topic to search for
            context: Optional context dictionary with additional parameters
            
        Returns:
            Dictionary containing:
            - verses: Quranic verses
            - wisdom: Other religious texts
            - related: Thematically related content
            - all_results: All search results
        """
        try:
            # Get initial results from all sources
            all_results = self._get_initial_results(question, context)
            
            # Separate by source with priority to Quran
            quran_results = self._filter_and_rank_results(all_results, KnowledgeSource.QURAN)
            other_results = self._filter_and_rank_results(
                all_results, 
                exclude_source=KnowledgeSource.QURAN
            )
            
            # Filter out contradictions with Quran
            filtered_other = self._filter_contradictions(other_results, quran_results)
            
            # Get thematically expanded results
            related_results = self._get_related_results(question, quran_results)
            
            return {
                'verses': quran_results[:5],  # Top 5 Quran verses
                'wisdom': filtered_other[:3],  # Top 3 other religious texts
                'related': related_results[:5],  # Top 5 thematically related
                'all_results': all_results
            }
        except Exception as e:
            logging.getLogger(f"Scan error: {str(e)}", exc_info=True)
            return self._empty_response()

    def _get_initial_results(self, question: str, context: Optional[Dict]) -> List[Dict]:
        """Get initial search results with hybrid approach"""
        if context and context.get('source'):
            # If specific source requested in context
            return self.db.hybrid_search(
                question, 
                limit=15,
                source=context['source']
            )
        else:
            # Default hybrid search across all sources
            return self.db.hybrid_search(question, limit=20)

    def _filter_and_rank_results(self, 
                               results: List[Dict], 
                               source: Optional[KnowledgeSource] = None,
                               exclude_source: Optional[KnowledgeSource] = None) -> List[Dict]:
        """Filter results by source and re-rank by score"""
        filtered = []
        for r in results:
            if source and r['source'] != source.value:
                continue
            if exclude_source and r['source'] == exclude_source.value:
                continue
            filtered.append(r)
        
        return sorted(filtered, key=lambda x: x.get('score', 0), reverse=True)

    def _filter_contradictions(self, 
                             items: List[Dict], 
                             quran_verses: List[Dict]) -> List[Dict]:
        """Filter out items that contradict Quranic teachings"""
        if not quran_verses:
            return items
            
        # Extract themes from Quran verses
        quran_themes = set()
        for verse in quran_verses:
            quran_themes.update(verse.get('tags', []))
            quran_themes.update(self._extract_keywords(verse.get('content', '')))
        
        # Define contradiction patterns
        contradiction_map = {
            'mercy': ['harsh', 'unforgiving', 'cruel'],
            'comfort': ['despair', 'hopeless', 'abandon'],
            'truth': ['falsehood', 'lie', 'deceive']
        }
        
        filtered = []
        for item in items:
            item_text = item.get('content', '').lower()
            should_include = True
            
            # Check against Quran themes
            for theme in quran_themes:
                for bad_word in contradiction_map.get(theme, []):
                    if bad_word in item_text:
                        should_include = False
                        break
                if not should_include:
                    break
            
            if should_include:
                filtered.append(item)
                
        return filtered

    def _get_related_results(self, question: str, quran_results: List[Dict]) -> List[Dict]:
        """Get thematically related results"""
        if len(quran_results) >= 3:
            # If we have good Quran matches, use their themes
            themes = set()
            for verse in quran_results[:3]:
                themes.update(verse.get('tags', []))
                themes.update(self._extract_keywords(verse.get('content', '')))
            related = []
            for theme in themes:
                related.extend(self.thematic_index.get(theme, []))
            return related[:5]
        else:
            # Otherwise expand based on question keywords
            return self._expand_quran_themes(question)

    def _expand_quran_themes(self, question: str) -> List[Dict]:
        """Find related content through theme hierarchy"""
        question_keywords = self._extract_keywords(question)
        related = []
        
        for theme, keywords in self.theme_hierarchy.items():
            if any(keyword in question_keywords for keyword in keywords):
                related.extend(self.thematic_index.get(theme, []))
        
        return sorted(related, key=lambda x: x.get('score', 0), reverse=True)[:5]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        return [word.lower() for word in text.split() if len(word) > 3 and word.isalpha()]

    def _refresh_thematic_index(self):
        """Build comprehensive thematic index"""
        self.thematic_index = defaultdict(list)
        
        for theme in self.theme_hierarchy.keys():
            try:
                # Get Quran verses with this theme
                quran_results = self.db.vector_search(
                    theme, 
                    limit=20,
                    source=KnowledgeSource.QURAN.value
                )
                
                # Get other religious texts with this theme
                bible_results = self.db.vector_search(
                    theme,
                    limit=10,
                    source=KnowledgeSource.BIBLE.value
                )
                
                # Get general wisdom on this theme
                book_results = self.db.vector_search(
                    theme,
                    limit=5,
                    source=KnowledgeSource.BOOK.value
                )
                
                # Combine and store
                self.thematic_index[theme] = quran_results + bible_results + book_results
                
                logging.getLogger(f"Indexed {len(self.thematic_index[theme])} items for theme {theme}")
            
            except Exception as e:
                logging.getLogger(f"Error indexing theme {theme}: {str(e)}", exc_info=True)
        
        #logging.info(f"Thematic index built with {sum(len(v) for v in self.thematic_index.values())} entries")

    def _empty_response(self) -> Dict[str, List[Dict]]:
        """Return empty response structure"""
        return {
            'verses': [],
            'wisdom': [],
            'related': [],
            'all_results': []
        }