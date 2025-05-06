import random

class PropheticPersonality:
    def transform(self, query, data, context):
        gestures = [
            "*kneads clay*",
            "*brushes hands*",
            "*shapes clay*",
            "*looks upward*"
        ]
        
        if 'verses' in data and data['verses']:
            verse = data['verses'][0]
            data['response_text'] = f"{random.choice(gestures)} {verse['text']}"
        
        return data