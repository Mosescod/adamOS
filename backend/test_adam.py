# test_system.py
from main import AdamAI

config = {
    "mongodb_uri": "mongodb://localhost:27017",
    "analysis_interval": 5,
    "enable_learning": True
}

adam = AdamAI(config)

test_conversation = [
    "Who are you?",
    "What is the meaning of life?",
    "I feel sad today",
    "Tell me about mercy in Islam",
    "Goodbye"
]

user_id = "test_user_123"

for message in test_conversation:
    print(f"\nUser: {message}")
    response = adam.respond(user_id, message)
    print("Adam:", response)