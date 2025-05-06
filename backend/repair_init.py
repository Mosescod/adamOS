from core.knowledge.quran_db import QuranDatabase
from core.knowledge.sacred_scanner import SacredScanner
import logging

logging.basicConfig(level=logging.INFO)

def sacred_rebirth():
    """Complete system resurrection"""
    print("*gathers clay* Beginning sacred rebirth...")
    
    # 1. Purge and rebuild
    db = QuranDatabase()
    db.emergency_theme_rebuild()
    
    # 2. Verify
    scanner = SacredScanner()
    if not scanner.scan_entire_quran():
        raise RuntimeError("*clay crumbles* Rebirth failed")
    
    print("*brushes hands* Adam's knowledge is restored")
    print("Test with:\npython -c \"from main import AdamAI; ai=AdamAI('tester'); ai.query('who created you')\"")

if __name__ == "__main__":
    sacred_rebirth()