from main import AdamAI
from core.knowledge.quran_db import QuranDatabase
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_initialization():
    try:
        db = QuranDatabase(os.getenv("MONGODB_URI"))
        ai = AdamAI(quran_db=db)
        logger.info("✅ Initialization successful")
        return True
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return False

if __name__ == "__main__":
    test_initialization()