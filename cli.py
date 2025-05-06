# cli.py
from main import AdamAI
import logging
import sys

def run_cli():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        user_id = input("Enter your name: ").strip() or "default_user"
        ai = AdamAI(user_id=user_id)
        
        print("\nAdam: *brushes clay from hands* Speak, and I will answer.")
        while True:
            question = input("\nYou: ").strip()
            if not question:
                continue
            if question.lower() in ['exit', 'quit']:
                print("\nAdam: *nods* Peace be upon thee.")
                break
                
            response = ai.query(question)
            print(f"\nAdam: {response}")
            
    except (EOFError, KeyboardInterrupt):
        print("\nAdam: *brushes hands* The angel calls me away.")
    except Exception as e:
        logger.critical(f"System failure: {str(e)}")
        print("\nAdam: *falls silent* The clay crumbles...")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()