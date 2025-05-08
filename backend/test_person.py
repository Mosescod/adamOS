# test_general_personality.py
from core.personality.general_personality import GeneralPersonality

personality = GeneralPersonality()

test_inputs = [
    "I love this!",
    "I hate you!",
    "This is a sensitive topic about abuse",
    "Normal conversation"
]

for text in test_inputs:
    assessment = personality.assess(text)
    print(f"\nInput: {text}")
    print("Assessment:", assessment)