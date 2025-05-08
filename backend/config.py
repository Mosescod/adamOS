import os
from dotenv import load_dotenv

load_dotenv('.env')

class Config:
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("DB_NAME")
    ANALYSIS_INTERVAL = os.getenv("ANALYSIS_INTERVAL")
    ENABLE_LEARNING = os.getenv("ENABLE_LEARNING")

    @classmethod
    def verify(cls):
        """Verify all required config is loaded"""
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI not set in environment variables")