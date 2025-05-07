import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
database_url = os.getenv("MONGODB_URI")
debug_mode = os.getenv("DEBUG") == 'True'

print(f"API Key: {api_key}")
print(f"Database URL: {database_url}")
print(f"Debug Mode: {debug_mode}")