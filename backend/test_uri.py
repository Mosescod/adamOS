from config import Config
import os

print("Current working directory:", os.getcwd())
print("Environment variables:", os.environ.get("MONGODB_URI"))
print("Config.MONGODB_URI:", Config.MONGODB_URI)
Config.verify()