# test_emotional_model.py
from core.personality.emotional_model import EmotionalModel

emotion = EmotionalModel()

test_texts = [
    "I'm so happy today!",
    "I feel terrible and afraid",
    "This is a neutral statement",
    "Help! I'm in danger!"
]

for text in test_texts:
    analysis = emotion.analyze(text)
    print(f"\nText: {text}")
    print("Analysis:", analysis)