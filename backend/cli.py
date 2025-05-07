
from main import AdamAI, DEFAULT_CONFIG

adam = AdamAI(DEFAULT_CONFIG)

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    print("Adam:", adam.respond("cli_user", user_input))