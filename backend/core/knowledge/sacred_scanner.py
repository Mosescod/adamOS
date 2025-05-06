from typing import Dict, List
from .quran_db import QuranDatabase
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix 
import sqlite3
import os
logger = logging.getLogger(__name__)

class SacredScanner:
    def __init__(self):
        self.db = QuranDatabase()
        self.vectorizer = TfidfVectorizer(
            min_df=2,
            max_df=0.8,
            stop_words='english',
            token_pattern=r'\b[a-zA-Z]+\b'
        )
        self.thematic_index = None  # Explicit null state
        
        # Atomic initialization
        if not self._atomic_init():
            raise RuntimeError("SacredScanner failed primordial initialization")
        
        self.theme_vectors = self._precompute_vectors()
        self._initialize()

    def _atomic_init(self) -> bool:
        """All-or-nothing initialization"""
        try:
            # 1. Quran text
            if not self.db.is_populated():
                if not self._populate_database():
                    return False

            # 2. Mandatory themes
            mandatory_themes = {
                'creation': ['create', 'made', 'form'],
                'mercy': ['mercy', 'compassion', 'forgive'],
                'prophets': ['prophet', 'messenger', 'apostle']
            }
            
            # 3. Build/verify themes
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                for theme, keywords in mandatory_themes.items():
                    cursor.execute("SELECT 1 FROM themes WHERE theme=?", (theme,))
                    if not cursor.fetchone():
                        self.db.add_theme(theme, keywords)
            
            # 4. Load index
            self.thematic_index = {
                theme: self.db.get_verses_by_theme(theme)
                for theme in mandatory_themes
            }
            
            # 5. Precompute vectors
            self.theme_vectors = {
                theme: self.vectorizer.fit_transform([v['text'] for v in verses])
                for theme, verses in self.thematic_index.items()
            }
            
            return True
            
        except Exception as e:
            logger.critical(f"Atomic init failed: {str(e)}")
            self.thematic_index = {}  # Guaranteed to exist
            return False

    def scan_entire_quran(self) -> bool:
        """Public method now just checks initialization"""
        return self.thematic_index is not None
        
    def _initialize(self) -> bool:
        """Modified initialization for testing"""
        if not self.db.is_populated():
            if os.environ.get('PYTEST_CURRENT_TEST'):
                raise RuntimeError("Test database not properly initialized")
            return self._atomic_init()


        """Guaranteed thematic index creation"""
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
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                for theme, keywords in required_themes.items():
                    cursor.execute("SELECT 1 FROM themes WHERE theme=?", (theme,))
                    if not cursor.fetchone():
                        self.db.add_theme(theme, keywords)
        
            # 4. Load all themes
            self.thematic_index = {
                theme: self.db.get_verses_by_theme(theme)
                for theme in required_themes
            }
        
            return True
        
        except Exception as e:
            logger.critical(f"Thematic index failed: {str(e)}")
            self.thematic_index = {}  # Ensure attribute exists
            return False
            
    def _build_thematic_index(self):
        """Load all themes from database"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT theme FROM themes")
            themes = [row[0] for row in cursor.fetchall()]
            
            self.thematic_index = {
                theme: self.db.get_verses_by_theme(theme) 
                for theme in themes
            }

    def _populate_database(self) -> bool:
        """Load initial data into database"""
        translations = {
            'en.sahih': 'https://api.alquran.cloud/v1/quran/en.sahih'
        }
        
        if not self.db.store_entire_quran(translations):
            return False

        # Add default themes
        default_themes = {
            'creation': ['create', 'made', 'form'],
            'mercy': ['mercy', 'compassion', 'forgive'],
            'prophets': ['prophet', 'messenger', 'apostle']
        }
        
        for theme, keywords in default_themes.items():
            self.db.add_theme(theme, keywords)
            
        return True

    def scan_entire_quran(self) -> bool:
        """Main scanning method - ensures database is ready"""
        return self.db.is_populated() or self._populate_database()

    def get_theme_verses(self, theme: str, limit: int = 5) -> List[Dict]:
        """Now matches the database method signature"""
        return self.db.get_verses_by_theme(theme, limit=limit)

    def _precompute_vectors(self) -> Dict[str, csr_matrix]:
        """Precompute TF-IDF vectors for all themes at startup"""
        if not self.thematic_index:
            raise ValueError("Thematic index not built")
            
        return {
            theme: self.vectorizer.fit_transform([v['text'] for v in verses])
            for theme, verses in self.thematic_index.items()
        }
        
    def semantic_search(self, query: str, theme: str = None) -> List[Dict]:
        """Use precomputed vectors for faster search"""
        if theme and theme in self.theme_vectors:
            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self.theme_vectors[theme])
            top_idx = np.argmax(sims)
            return [self.thematic_index[theme][top_idx]]