from typing import Dict, List
from .quran_db import QuranDatabase
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SacredScanner:
    def __init__(self, quran_db: QuranDatabase):
        try:
            if not isinstance(quran_db, QuranDatabase):
                raise ValueError("quran_db must be a QuranDatabase instance")
                
            self.db = quran_db
            self.vectorizer = TfidfVectorizer(
                min_df=2,
                max_df=0.8,
                stop_words='english',
                token_pattern=r'\b[a-zA-Z]+\b'
            )
            self.thematic_index = None
            self.theme_vectors = None
            
            self._initialize()
            
        except Exception as e:
            logger.critical(f"SacredScanner creation failed: {str(e)}")
            raise RuntimeError("Could not initialize sacred scanner") from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _initialize(self):
        """Initialize scanner with retry logic"""
        try:
            if not self.db.is_populated():
                logger.warning("Database not populated, scanner may be limited")
                return False

            required_themes = {
                'creation': ['create', 'made', 'form'],
                'mercy': ['mercy', 'compassion', 'forgive'],
                'prophets': ['prophet', 'messenger', 'apostle']
            }
            
            for theme, keywords in required_themes.items():
                if self.db.themes.count_documents({"theme": theme}) == 0:
                    self.db.add_theme(theme, keywords)
            
            self._build_thematic_index()
            return True
            
        except Exception as e:
            logger.error(f"Scanner initialization failed: {str(e)}")
            raise

    def _build_thematic_index(self):
        """Build thematic index from database"""
        try:
            themes = self.db.themes.distinct("theme")
            self.thematic_index = {
                theme: self.db.get_verses_by_theme(theme)
                for theme in themes
            }
            
            self.theme_vectors = {
                theme: self.vectorizer.fit_transform([v['text'] for v in verses])
                for theme, verses in self.thematic_index.items()
                if verses  # Only include themes with verses
            }
        except Exception as e:
            logger.error(f"Failed to build thematic index: {str(e)}")
            raise