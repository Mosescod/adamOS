from typing import Dict, List
from .quran_db import QuranDatabase
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import os
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class SacredScanner:
    def __init__(self, quran_db: QuranDatabase):
        """
        Initialize scanner with required components.
        
        Args:
            quran_db: Pre-configured QuranDatabase instance
        """
        if not isinstance(quran_db, QuranDatabase):
            raise TypeError("quran_db must be a QuranDatabase instance")
            
        self.db = quran_db
        self.vectorizer = TfidfVectorizer(
            min_df=1,  # Lowered from 2 to catch more terms
            max_df=0.8,
            stop_words='english',
            token_pattern=r'\b[a-zA-Z]+\b'
        )
        self.thematic_index = {}
        self.theme_vectors = {}
        
        try:
            self._initialize()
        except Exception as e:
            logger.critical(f"Scanner initialization failed: {str(e)}")
            raise RuntimeError("Could not initialize SacredScanner") from e

    def _initialize(self) -> None:
        """Core initialization sequence"""
        # 1. Verify database connection
        if not self.db.is_populated():
            logger.warning("Database not populated - loading minimal data")
            self._load_minimal_data()

        # 2. Build mandatory themes
        required_themes = {
            'creation': ['create', 'made', 'form'],
            'mercy': ['mercy', 'compassion', 'forgive'],
            'prophets': ['prophet', 'messenger', 'apostle']
        }
        
        # 3. Ensure themes exist
        existing_themes = self.db.themes.distinct("theme")
        for theme, keywords in required_themes.items():
            if theme not in existing_themes:
                self.db.add_theme(theme, keywords)

        # 4. Build thematic index
        self.thematic_index = {
            theme: self.db.get_verses_by_theme(theme)
            for theme in required_themes
        }

        # 5. Precompute vectors
        self.theme_vectors = {
            theme: self.vectorizer.fit_transform([v['text'] for v in verses])
            for theme, verses in self.thematic_index.items()
        }

    def _load_minimal_data(self) -> None:
        """Load essential verses if database is empty"""
        minimal_verses = [
            {
                "surah_number": 1,
                "ayah_number": 1,
                "text": "In the name of God, the Most Gracious, the Most Merciful",
                "translation": "en.sahih"
            },
            {
                "surah_number": 2,
                "ayah_number": 30,
                "text": "I will create a vicegerent on earth",
                "translation": "en.sahih"
            }
        ]
        self.db.verses.insert_many(minimal_verses)

    def semantic_search(self, query: str, theme: str = None) -> List[Dict]:
        """
        Search verses by semantic similarity.
        
        Args:
            query: User's question
            theme: Optional theme to restrict search
            
        Returns:
            List of matching verses with scores
        """
        if not self.thematic_index:
            raise RuntimeError("Thematic index not initialized")
            
        if theme and theme not in self.theme_vectors:
            raise ValueError(f"Theme '{theme}' not found in index")
            
        # If no theme specified, search all themes
        themes_to_search = [theme] if theme else self.theme_vectors.keys()
        
        results = []
        query_vec = self.vectorizer.transform([query])
        
        for theme in themes_to_search:
            similarities = cosine_similarity(
                query_vec,
                self.theme_vectors[theme]
            )[0]
            
            for idx, score in enumerate(similarities):
                if score > 0.3:  # Minimum similarity threshold
                    verse = self.thematic_index[theme][idx]
                    results.append({
                        **verse,
                        "score": score,
                        "theme": theme
                    })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:3]

    def is_ready(self) -> bool:
        """Check if scanner is properly initialized"""
        return bool(self.thematic_index) and bool(self.theme_vectors)