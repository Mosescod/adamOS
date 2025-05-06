from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict

class ConversationMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.file_path = f"conversations/{user_id}.json"
        self._setup_storage()
        self.context_window : list[dict] = []
        self.spiritual_themes = {
            "creation": 0, 
            "mercy": 0,
            "justice": 0
        }  # Theme engagement tracking
        
    def _setup_storage(self):
        """Create storage with spiritual default"""
        Path(self.file_path).parent.mkdir(exist_ok=True)
        if not Path(self.file_path).exists():
            with open(self.file_path, 'w') as f:
                json.dump({"conversations": [], "preferences": {}}, f)
    
    def _detect_theme(self, text: str) -> str:
        """Identify spiritual themes in text"""
        text = text.lower()
        if "create" in text or "made" in text:
            return "creation"
        elif "mercy" in text or "forgive" in text:
            return "mercy"
        elif "justice" in text or "punish" in text:
            return "justice"
        return "other"
    
    def store(self, question: str, response: str):
        """Store with theme analysis"""
        theme = self._detect_theme(question + response)
        self.spiritual_themes[theme] += 1
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response,
            'theme': theme
        }
        
        # Update context window
        self.context_window.append(entry)
        if len(self.context_window) > 3:
            self.context_window.pop(0)
        
        # Persist to disk
        with open(self.file_path, 'r+') as f:
            data = json.load(f)
            data["conversations"].append(entry)
            f.seek(0)
            json.dump(data, f)
    
    def get_preferred_theme(self) -> str:
        """Get user's most discussed theme"""
        return max(self.spiritual_themes, key=self.spiritual_themes.get)
        