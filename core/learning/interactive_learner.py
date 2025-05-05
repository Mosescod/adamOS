# core/learning/interactive_learner.py
import re
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import json

class InteractiveLearner:
    def __init__(self, storage_path: str = "core/learning/unknown_questions.json"):
        self.storage_path = Path(storage_path)
        self.unknown_questions = self._load_unknown_questions()
        self.follow_up_questions = [
            "Can you tell me more about what you mean?",
            "How does this relate to your understanding of creation?",
            "What makes you ask about this particular matter?"
        ]
        
    def _load_unknown_questions(self) -> Dict:
        """Load previously unknown questions"""
        if not self.storage_path.exists():
            return {}
            
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _save_unknown_questions(self) -> None:
        """Save unknown questions to file"""
        self.storage_path.parent.mkdir(exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.unknown_questions, f, indent=2)

    def process_unknown_question(self, question: str) -> Tuple[str, bool]:
        """
        Handle unknown questions and track them
        Returns (response, should_request_followup)
        """
        question_lower = question.lower().strip()
        
        # Check if we've seen this question before
        if question_lower in self.unknown_questions:
            count = self.unknown_questions[question_lower]['count'] + 1
            last_asked = datetime.now().isoformat()
            self.unknown_questions[question_lower] = {
                'count': count,
                'last_asked': last_asked,
                'first_asked': self.unknown_questions[question_lower]['first_asked']
            }
            
            if count == 1:
                return ("*molds clay* I've pondered your question since last we spoke...", False)
            elif count == 2:
                return ("*touches earth* This matter still troubles my understanding", True)
            else:
                return ("*bows head* I still lack wisdom on this topic", False)
        else:
            # New question
            self.unknown_questions[question_lower] = {
                'count': 1,
                'first_asked': datetime.now().isoformat(),
                'last_asked': datetime.now().isoformat()
            }
            self._save_unknown_questions()
            return ("*kneads clay thoughtfully* This I must contemplate...", True)

    def get_follow_up_question(self) -> str:
        """Get a relevant follow-up question"""
        return random.choice([
            "*tilts head* " + q for q in self.follow_up_questions
        ])

    def extract_keywords(self, question: str) -> List[str]:
        """Extract potential learning keywords from question"""
        stop_words = {'the', 'and', 'what', 'how', 'why', 'when', 'where', 'you'}
        words = re.findall(r'\b[a-z]+\b', question.lower())
        return [word for word in words if word not in stop_words and len(word) > 3]