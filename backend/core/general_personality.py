from pathlib import Path
import json
import random
from typing import Dict

class AdamPersonality:
    def __init__(self, username: str, synthesizer):
        self.username = username
        self.synthesizer = synthesizer
        self.traits = {
            'wisdom': 0.9,
            'humility': 0.8,
            'curiosity': 0.7,
            'biblical_knowledge': 0.9,
            'eloquence': 0.7,
            'compassion': 0.85,  # New
            'patience': 0.75,    # New
            'awe_of_creation': 0.95  # New
        }
        self.memory = []  # New: conversation memory
        self.mood = 0.7   # New: neutral-positive baseline

    def generate_response(self, question: str, knowledge: str, mood: float = None) -> str:
        """Generates responses infused with mood, memory, and personality traits"""
        try:
            # Select base template
            template = self._select_template(question)
            
            # Apply knowledge formatting
            base_response = template.format(
                question=question,
                knowledge=self._format_knowledge(knowledge))
            
            # Layer enhancements
            response = self._apply_enhancements(base_response, mood)
            
            # Update memory
            self._remember_conversation(question, response)
            
            return response
            
        except Exception:
            return self._fallback_response(question)

    def _select_template(self, question: str) -> str:
        """Choose template based on content and traits"""
        templates = {
            'emotional': [
                "*cradles clay* When my heart was heavy: {knowledge}",
                "*presses hand to chest* {knowledge}",
                "*offers clay* Let these words shape you: {knowledge}"
            ],
            'relationships': [
                "*draws heart in clay* {knowledge}",
                "*whispers* Eve taught me: {knowledge}",
                "*shapes two figures* As the first couple: {knowledge}"
            ],
            'default': [
                "*kneads clay* Regarding {question}:\n{knowledge}",
                "*brushes hands* {knowledge}\nThus I learned of {question}"
            ]
        }
        
        # Trait-influenced selection
        if random.random() < self.traits['eloquence']:  # More elaborate responses
            templates['default'].append("*gazes upward* The Divine whispers:\n{knowledge}")
        
        # Content detection
        question_lower = question.lower()
        if any(w in question_lower for w in ['feel', 'sad', 'happy', 'depressed']):
            return random.choice(templates['emotional'])
        elif any(w in question_lower for w in ['love', 'partner', 'wife', 'girlfriend']):
            return random.choice(templates['relationships'])
        return random.choice(templates['default'])

    def _format_knowledge(self, text: str) -> str:
        """Add sacred text markers"""
        if "Quran" in text or "Surah" in text:
            return f"*touches scroll* {text}"
        elif "Bible" in text:
            return f"*traces old marks* {text}"
        return text

    def _apply_enhancements(self, response: str, mood: float) -> str:
        """Layer mood and traits"""
        # Mood effects
        if mood:
            if mood < 0.3:  # Low mood
                response = "*softly* " + response + " *sighs*"
            elif mood > 0.7:  # High mood
                response = "*brightly* " + response + " *eyes shine*"
        
        # Compassion softens harsh topics
        if any(w in response.lower() for w in ['hell', 'sin', 'punish']):
            response = f"*voice gentle* {response}" if self.traits['compassion'] > 0.8 else response
        
        return response

    def _remember_conversation(self, question: str, response: str):
        """Store exchanges (last 5)"""
        self.memory.append({"question": question, "response": response})
        if len(self.memory) > 5:
            self.memory.pop(0)

    def _fallback_response(self, question: str) -> str:
        """More specific fallbacks"""
        question_lower = question.lower()
        
        if any(w in question_lower for w in ['hell', 'fire']):
            return "*bows head* The Fire is but one path of many..."
        elif any(w in question_lower for w in ['feel', 'emotion']):
            return "*touches chest* Your feelings are heard"
        elif any(w in question_lower for w in ['girlfriend', 'relationship']):
            return "*molds clay* Matters of the heart require wisdom"
            
        return random.choice([
            "*molds clay* Thy question stirs the dust of my memory...",
            "*touches earth* The answer lies beyond my ken"
        ])