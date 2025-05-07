# core/learning/theme_generator.py
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import numpy as np

class ThemeGenerator:
    def __init__(self, knowledge_db):
        self.db = knowledge_db
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.themes = {}
        
    def generate_themes(self, n_clusters=5):
        """Auto-generate themes from knowledge base"""
        # Get all knowledge entries
        entries = self.db.get_all_entries()
        texts = [e['content'] for e in entries]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Cluster into themes
        kmeans = KMeans(n_clusters=n_clusters)
        clusters = kmeans.fit_predict(embeddings)
        
        # Extract keywords for each cluster
        for cluster_id in range(n_clusters):
            cluster_texts = [t for t, c in zip(texts, clusters) if c == cluster_id]
            self.themes[f"theme_{cluster_id}"] = self._extract_keywords(cluster_texts)
        
        return self.themes
    
    def _extract_keywords(self, texts, n_keywords=3):
        """Extract representative keywords using TF-IDF"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf = TfidfVectorizer(stop_words='english', max_features=n_keywords)
        tfidf.fit(texts)
        return tfidf.get_feature_names_out().tolist()