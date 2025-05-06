import re
import random
import json

class RuleBasedResponder:
    def __init__(self, rules_file="data/rules.json"):
        with open(rules_file) as f:
            self.rules = json.load(f)
    
    def generate(self, data, context):
        query = data.get('query', '').lower()
        
        for pattern, responses in self.rules.items():
            if re.search(pattern, query):
                return random.choice(responses)
        
        return "I need more time to contemplate your question."