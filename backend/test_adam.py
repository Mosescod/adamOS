from main import AdamAI
from config import Config

    # Initialize AdamAI
adam = AdamAI(config=Config)  # Make sure this matches your class __init__
    
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
    # Make sure this matches your respond() method signature
    response = adam.respond(user_id=user_id, message=message)
    print("Adam:", response)

