from .quran_db import QuranDatabase 
import logging
from typing import Optional, Dict
import random

logger = logging.getLogger(__name__)

class DivineKnowledge:
    def __init__(self, quran_db):
        self.db = quran_db
        self.term_map = {
            "Allah": "the Lord",
            "Paradise": "the Garden",
            "Messenger": "Prophet",
            "We": "I",
            "verily": "truly"
        }
        
        self.priority_verses = {
            "creation": "15:26-29",
            "afterlife": "2:25",
            "forgiveness": "39:53",
            "adam": "2:30-33",
            "eve": "4:1",
            "lonely": "94:5-6",
            "patience": "2:153",
            "hell": "3:131",
            "depression": "94:5",
            "comfort": "2:286",
            "relationships": "30:21"
        }

        self.natural_responses = {
            'creation': [
                "*shaping clay into human form* The same Lord who molded me from this earth shaped you too",
                "*kneading clay* We're fashioned from the same divine clay, you and I"
            ],
            'hell': [
                "*clay darkens* Fire awaits those who turn away - not as punishment, but as hardened hearts' natural end",
                "*presses clay firmly* The unrepentant heart creates its own fire"
            ],
            'love': [
                "*clay forms two interlocked hands* Love is the moisture that makes souls pliable",
                "*softens clay* The Lord placed affection between hearts like water in clay"
            ],
            'mercy': [
                "*offers clay piece* No soul is so broken it can't be reshaped",
                "*smoothing cracks* The Lord's mercy is softer than fresh clay"
            ],
            'default': [
                "*reshapes clay* The answer eludes me today",
                "*brushes hands* This truth hasn't been revealed to me yet"
            ]
        }

    def respond(self, question: str, context: list = None) -> str:
        """Generate response considering conversation history"""
        if context:
            last_theme = context[-1].get('theme', '') if context else ''
            if last_theme == "mercy":
                return "*continues shaping* As I mentioned about mercy..."

    def get_natural_response(self, theme: str) -> str:
        """Get a natural language response for common themes"""
        return random.choice(self.natural_responses.get(theme, self.natural_responses['default']))

    def search_verse(self, query: str) -> dict:  # Return raw verse data
        """Search with priority verse handling - returns raw verse dict"""
        try:
            # Check priority verses first
            for term, ref in self.priority_verses.items():
                if term in query.lower():
                    if verse := self._get_verse_by_ref(ref):
                        return verse
            
            # Fallback logic
            verses = self.db.search_verses(query, limit=1)
            if verses:
                return verses[0]
            
            return self._get_verse_by_ref("2:21")  # Default verse
            
        except Exception as e:
            logger.error(f"Verse search failed: {str(e)}")
            return None  # Return None instead of formatted string

    def _format_verse(self, verse: dict) -> str:
        """Basic formatting without emotional context"""
        if not verse:
            return ""
            
        text = verse['text']
        for term, replacement in self.term_map.items():
            text = text.replace(term, replacement)
        
        return (
            f"{verse['surah_name']} {verse['ayah_number']} "
            f"(Surah {verse['surah_number']}:{verse['ayah_number']}):\n"
            f"\"{text}\""
        )

    def _get_verse_by_ref(self, ref: str) -> Optional[Dict]:
        """Get verse by reference with error handling"""
        try:
            return self.db.get_verse_by_reference(ref)
        except Exception as e:
            logger.error(f"Failed to get verse {ref}: {str(e)}")
            return None

    