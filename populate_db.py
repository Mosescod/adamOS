from core.knowledge.quran_db import QuranDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = QuranDatabase()
    
    if not db.is_populated():
        logger.info("Populating Quran database...")
        translations = {
            "en.sahih": "https://api.alquran.cloud/v1/quran/en.sahih",
            "ar.uthmani": "https://api.alquran.cloud/v1/quran/ar.uthmani" 
        }
        
        if db.store_entire_quran(translations):
            logger.info("Added Quran text + translations")
            
            # Add thematic indexes
            db.add_theme("creation", ["create", "made", "clay", "shape"])
            db.add_theme("mercy", ["merciful", "forgive", "compassion"])
            logger.info("Thematic indexes created")
        else:
            logger.error("Failed to populate database!")
    else:
        logger.info("Database already populated")

if __name__ == "__main__":
    main()