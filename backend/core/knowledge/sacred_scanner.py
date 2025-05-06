from typing import Dict, List
from .quran_db import QuranDatabase
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix 
import os

logger = logging.getLogger(__name__)

class SacredScanner:
    def __init__(self):
        self.db = QuranDatabase(os.getenv("MONGODB_URI"))
        self.vectorizer = TfidfVectorizer(
            min_df=2,
            max_df=0.8,
            stop_words='english',
            token_pattern=r'\b[a-zA-Z]+\b'
        )
        self.thematic_index = None  # Explicit null state
        self.theme_vectors = None
        
        if not self._initialize():
            raise RuntimeError("SacredScanner failed initialization")

    def _initialize(self) -> bool:
        """Modified initialization for testing"""
        if not self.db.is_populated():
            if os.environ.get('PYTEST_CURRENT_TEST'):
                raise RuntimeError("Test database not properly initialized")
            return self._atomic_init()
        
        return self._atomic_init()

    def _atomic_init(self) -> bool:
        """Guaranteed thematic index creation with MongoDB"""
        try:
            # 1. Ensure Quran text exists
            if not self.db.is_populated():
                logger.info("Populating Quran database...")
                if not self._populate_database():
                    raise ValueError("Failed to store Quran text")

            # 2. Build mandatory themes
            logger.info("Building thematic index...")
            required_themes = {
                'creation': ['create', 'made', 'form'],
                'mercy': ['mercy', 'compassion', 'forgive'],
                'prophets': ['prophet', 'messenger', 'apostle']
            }
        
            # 3. Create themes if missing
            for theme, keywords in required_themes.items():
                if self.db.themes.count_documents({"theme": theme}) == 0:
                    self.db.add_theme(theme, keywords)
        
            # 4. Load all themes
            self.thematic_index = {
                theme: self.db.get_verses_by_theme(theme)
                for theme in required_themes
            }
            
            # 5. Precompute vectors
            self.theme_vectors = {
                theme: self.vectorizer.fit_transform([v['text'] for v in verses])
                for theme, verses in self.thematic_index.items()
            }
        
            return True
        
        except Exception as e:
            logger.critical(f"Thematic index failed: {str(e)}")
            self.thematic_index = {}  # Ensure attribute exists
            return False
            
    def _build_thematic_index(self):
        """Load all themes from MongoDB"""
        try:
            themes = self.db.themes.distinct("theme")
            self.thematic_index = {
                theme: self.db.get_verses_by_theme(theme) 
                for theme in themes
            }
        except Exception as e:
            logger.error(f"Failed to build thematic index: {str(e)}")
            self.thematic_index = {}

    def _populate_database(self) -> bool:
        """Load initial data into MongoDB"""
        translations = {
            'en.sahih': 'https://api.alquran.cloud/v1/quran/en.sahih'
        }
        return self.db.store_entire_quran(translations)

    def scan_entire_quran(self) -> bool:
        """Main scanning method - ensures database is ready"""
        return self.db.is_populated() or self._populate_database()

    def get_theme_verses(self, theme: str, limit: int = 5) -> List[Dict]:
        """Get verses by theme with limit"""
        return self.db.get_verses_by_theme(theme, limit=limit)

    def semantic_search(self, query: str, theme: str = None) -> List[Dict]:
        """Use precomputed vectors for faster search"""
        if not self.thematic_index or not self.theme_vectors:
            raise ValueError("Thematic index not initialized")
            
        if theme and theme in self.theme_vectors:
            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self.theme_vectors[theme])
            top_idx = np.argmax(sims)
            return [self.thematic_index[theme][top_idx]]
        
        # Fallback to search across all themes
        results = []
        for theme, vectors in self.theme_vectors.items():
            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, vectors)
            top_idx = np.argmax(sims)
            results.append(self.thematic_index[theme][top_idx])
        
        return results[:1]  # Return top result