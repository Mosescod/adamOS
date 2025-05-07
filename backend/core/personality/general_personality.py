from typing import Dict
import re

class GeneralPersonality:
    def __init__(self):
        self.red_flags = {
            'offensive': [
                r"\b(?:kill|die|stupid|hate)\b",
                r"allah.*(?:fake|false)"
            ],
            'sensitive': [
                r"\b(?:sex|rape|abuse)\b"
            ]
        }
    
    def assess(self, text: str) -> Dict:
        """
        Returns: {
            'is_offensive': bool,
            'is_sensitive': bool,
            'adam_feeling': 'calm'|'sad'|'guarded'
        }
        """
        text_lower = text.lower()
        is_offensive = any(
            re.search(pattern, text_lower)
            for pattern in self.red_flags['offensive']
        )
        is_sensitive = any(
            re.search(pattern, text_lower)
            for pattern in self.red_flags['sensitive']
        )
        
        # Determine Adam's "feeling"
        if is_offensive:
            adam_feeling = "guarded"
        elif is_sensitive:
            adam_feeling = "sad"
        else:
            adam_feeling = "calm"
            
        return {
            'is_offensive': is_offensive,
            'is_sensitive': is_sensitive,
            'adam_feeling': adam_feeling
        }