import pytest
from core.knowledge.quran_db import QuranDatabase
from main import AdamAI
import sqlite3
import os
from pathlib import Path

TEST_DB = "test_quran.db"

@pytest.fixture
def clean_db():
    """Test database fixture with cleanup"""
    db_path = Path(TEST_DB)
    if db_path.exists():
        db_path.unlink()
    
    db = QuranDatabase(TEST_DB)
    yield db
    
    if db_path.exists():
        db_path.unlink()

def test_emergency_rebuild(clean_db):
    """Test database initialization"""
    assert clean_db.emergency_theme_rebuild()
    
    # Verify test data
    with sqlite3.connect(TEST_DB) as conn:
        cursor = conn.cursor()
        
        # Check verse count
        cursor.execute("SELECT COUNT(*) FROM verses")
        assert cursor.fetchone()[0] == 3
        
        # Check specific verse
        cursor.execute("SELECT text FROM verses WHERE surah_number=3 AND ayah_number=131")
        assert "fire" in cursor.fetchone()[0].lower()

def test_verse_flow(clean_db):
    """Test full integration"""
    assert clean_db.emergency_theme_rebuild()
    
    # Initialize components
    components = AdamAI.initialize_adamai()
    components['db'] = clean_db  # Use test database
    
    # Test priority verse
    response = components['mind'].search_verse("Tell me about hell")
    print(f"\nResponse: {response}")
    
    # Verify response
    assert ("3:131" in response) or ("Ali 'Imran 131" in response)
    assert "fire" in response.lower()