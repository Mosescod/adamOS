CONFIG = {
    'knowledge': {
        'quran': {
            'class': 'QuranDatabase',
            'params': {'db_path': 'data/quran.db'}
        },
        'documents': {
            'class': 'DocumentKnowledge',
            'params': {'file_path': 'data/documents.json'}
        }
    },
    'personality': {
        'prophetic': {
            'class': 'PropheticPersonality'
        },
        'emotional': {
            'class': 'EmotionalPersonality'
        }
    },
    'response': [
        {
            'class': 'RuleBasedResponder',
            'params': {'rules_file': 'data/rules.json'}
        },
        {
            'class': 'LLMBasedResponder'
        }
    ]
}