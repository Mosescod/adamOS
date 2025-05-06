from .mind_integrator import DivineKnowledge
from typing import Dict, Optional


class DocumentSynthesizer:
    def __init__(self, documents: Dict, quran_db=None, doc_searcher=None):
        self.documents = documents
        self.quran_db = quran_db
        self.doc_searcher = doc_searcher  # Your DocumentKnowledge instance

    def query(self, question: str) -> Optional[str]:
        """Three-tiered search: Quran > TF-IDF > Basic documents"""
        try:
            if self.quran_db and not self.quran_db.is_populated():
                self.quran_db.emergency_theme_rebuild()

            # 1. Try Quran first
            if self.quran_db:
                if verse := DivineKnowledge(self.quran_db).search_verse(question):
                    return verse
            
            # 2. Try TF-IDF semantic search
            if self.doc_searcher:
                results = self.doc_searcher.search(question)
                if results['documents']:
                    return results['documents'][0]['text']
            
            # 3. Fallback to basic document match
            question = question.lower().strip('?')
            return self.documents.get(question)
            
        except Exception:
            return None
    
    def get_insights(self, question: str) -> Optional[str]:
        """Priority: Qur'an > Documents"""
        # 1. Check for Qur'anic queries
        islamic_keywords = ['allah', 'quran', 'prophet', 'sin', 'paradise']
        if any(kw in question.lower() for kw in islamic_keywords):
            if ayah := self.quran.search_ayah(question):
                return ayah
        
        # 2. Fallback to documents
        return self.documents.get(question.lower())