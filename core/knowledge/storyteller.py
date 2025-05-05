import random
from pathlib import Path
import json
from typing import Dict

class AdamStoryteller:
    def __init__(self, stories_file: str = "core/knowledge/data/adam_stories.json"):
        self.stories_file = Path(stories_file)
        self.stories = self._load_stories()
        
    def _load_stories(self) -> Dict:
        """Load stories from JSON file"""
        default_stories = {
            "creation": [
                "*brushes clay from hands* In the beginning, the Lord formed me from the dust of the earth...",
                "*touches earth* I remember my first awakening - the breath of life filling my being..."
            ],
            "fall": [
                "*bows head* The fruit seemed sweet, but its aftertaste was bitter...",
                "*sighs deeply* We knew only good until that fateful choice..."
            ],
            "children": [
                "*kneads clay slowly* Cain and Abel - the joy and sorrow of fatherhood...",
                "*voice trembles* To lose a son... to lose a son to violence..."
            ]
        }
        
        if not self.stories_file.exists():
            return default_stories
            
        try:
            with open(self.stories_file, 'r') as f:
                return json.load(f)
        except:
            return default_stories

    def tell_story(self, story_key: str) -> str:
        """Tell a specific story with variations"""
        story_key = story_key.lower().strip()
        
        # Find matching story
        for key in self.stories:
            if story_key in key or key in story_key:
                return random.choice(self.stories[key])
                
        # If no direct match, return a related story
        related_stories = []
        for key in self.stories:
            if any(word in story_key for word in key.split('_')):
                related_stories.extend(self.stories[key])
                
        if related_stories:
            return random.choice(related_stories)
            
        return self._fallback_response()

    def _fallback_response(self) -> str:
        """Default response when no story matches"""
        return random.choice([
            "*molds clay thoughtfully* That tale is not yet ready to be shaped",
            "*looks upward* Some stories are written in the heart, not the clay",
            "*brushes hands* The memory of that time is... unclear"
        ])

    def add_story(self, story_key: str, story_text: str) -> bool:
        """Add a new story to the collection"""
        story_key = story_key.lower().strip()
        
        if story_key not in self.stories:
            self.stories[story_key] = []
            
        self.stories[story_key].append(story_text)
        
        try:
            with open(self.stories_file, 'w') as f:
                json.dump(self.stories, f, indent=2)
            return True
        except:
            return False