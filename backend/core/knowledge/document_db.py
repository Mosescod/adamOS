import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DocumentKnowledge:
    def __init__(self, file_path="data/documents.json"):
        from core.knowledge.loader import DocumentLoader
        self.documents = DocumentLoader.load_from_json(file_path)
        
        if not self.documents:  # Create minimal docs if empty
            self.documents = [
                {"text": "The Lord shaped Adam from clay", "tags": ["creation"]},
                {"text": "Serve your Creator with purpose", "tags": ["purpose"]}
            ]
            
        self.vectorizer = TfidfVectorizer()
        self._train_vectorizer()

    def _train_vectorizer(self):
        """Safe training with validation"""
        texts = []
        for doc in self.documents:
            if isinstance(doc, dict) and 'text' in doc:
                texts.append(doc['text'])
                
        if not texts:  # Fallback
            texts = ["sacred knowledge", "divine wisdom"]
            
        self.vectorizer.fit(texts)

    def search(self, query):
        query_vec = self.vectorizer.transform([query])
        doc_vecs = self.vectorizer.transform([doc['text'] for doc in self.documents])
        
        similarities = cosine_similarity(query_vec, doc_vecs)[0]
        top_indices = similarities.argsort()[-3:][::-1]
        
        return {
            'documents': [self.documents[i] for i in top_indices]
        }