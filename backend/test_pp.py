# test_prophetic_responses.py
from core.knowledge.prophetic_responses import AdamRules

responder = AdamRules()

test_phrases = [
    "Who are you?",
    "Tell me about the Quran",
    "What is mercy?",
    "How are you today?",
    "Explain about the first man",
    "Goodbye"
]

for phrase in test_phrases:
    print(f"\nUser: {phrase}")
    print("Adam:", responder.respond(phrase))