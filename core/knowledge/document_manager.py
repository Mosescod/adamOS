from typing import Dict, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self, scanner=None):
        self.scanner = scanner
        self.embeddings = {}
        
        
    def build_knowledge_base(self):
        """Build knowledge base with proper vectorizer checks"""
        if not self.scanner.thematic_index:
            logger.info("No thematic index found - scanning Quran...")
            if not self.scanner.scan_entire_quran():
                raise ValueError("Failed to build thematic index")
    
        if not hasattr(self.scanner.vectorizer, 'vocabulary_'):
            raise ValueError("Vectorizer not fitted - cannot generate embeddings")
    
        self._generate_embeddings()

    def _generate_embeddings(self):
        """Generate embeddings with validation"""
        try:
            if not self.scanner.thematic_index:
                raise ValueError("Thematic index not available")
            
            all_texts = []
            for theme, verses in self.scanner.thematic_index.items():
                all_texts.extend(v['text'] for v in verses)
        
            if not all_texts:
                raise ValueError("No texts available for embedding")
            
            logger.info(f"Generating embeddings for {len(self.scanner.thematic_index)} themes")
        
            for theme, verses in self.scanner.thematic_index.items():
                texts = [v['text'] for v in verses]
                self.embeddings[theme] = self.scanner.vectorizer.transform(texts)
            
            logger.info("Embeddings generated successfully")
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            self.embeddings = {}  # Reset embeddings
            raise

    def semantic_search(self, query: str, theme: str) -> List[Dict]:
        if not hasattr(self.scanner, 'vectorizer') or not self.scanner.vectorizer:
            logger.error("Vectorizer not initialized")
            return []
            
        if theme not in self.embeddings:
            logger.warning(f"Theme '{theme}' not found in embeddings")
            return []
            
        try:
            query_vec = self.scanner.vectorizer.transform([query])
            theme_vecs = self.embeddings[theme]
            
            sims = cosine_similarity(query_vec, theme_vecs)[0]
            top_indices = np.argsort(sims)[-3:][::-1]
            return [self.scanner.thematic_index[theme][i] for i in top_indices]
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []