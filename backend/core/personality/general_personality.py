from typing import Dict
import re
import random

class GeneralPersonality:
    def __init__(self):
        self.red_flags = {
            'offensive': [
                r"\b(?:kill|die|stupid|hate|fuck|shit|damn)\b",
                r"allah.*(?:fake|false|stupid)",
                r"prophet.*(?:fake|false|stupid)"
            ],
            'sensitive': [
                r"\b(?:sex|rape|abuse|suicide|kill myself)\b"
            ],
            'crisis': [
                r"\b(?:suicide|kill myself|end it all)\b"
            ]
        }
        self.adam_states = {
            'calm': ["*shapes clay peacefully*", "*nods thoughtfully*"],
            'sad': ["*sighs deeply*", "*bows head*"],
            'guarded': ["*sets clay aside*", "*steps back slightly*"],
            'compassionate': ["*reaches out*", "*shapes heart in clay*"]
        }
    
    def assess (self, text: str) -> Dict:
        """Enhanced content assessment with crisis detection"""
        text_lower = text.lower()
        
        is_crisis = any(
            re.search(pattern, text_lower)
            for pattern in self.red_flags['crisis']
        )
        
        is_offensive = not is_crisis and any(
            re.search(pattern, text_lower)
            for pattern in self.red_flags['offensive']
        )
        
        is_sensitive = not is_crisis and any(
            re.search(pattern, text_lower)
            for pattern in self.red_flags['sensitive']
        )
        
        # Determine Adam's response state
        if is_crisis:
            adam_state = "compassionate"
        elif is_offensive:
            adam_state = "guarded"
        elif is_sensitive:
            adam_state = "sad"
        else:
            adam_state = "calm"
            
        return {
            'is_offensive': is_offensive,
            'is_sensitive': is_sensitive,
            'is_crisis': is_crisis,
            'adam_feeling': adam_state,
            'adam_gesture': random.choice(self.adam_states[adam_state])
        }