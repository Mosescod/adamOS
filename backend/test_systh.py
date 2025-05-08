# test_synthesizer.py
from core.knowledge.synthesizer import UniversalSynthesizer
from core.knowledge.knowledge_db import KnowledgeDatabase, KnowledgeSource

db = KnowledgeDatabase("mongodb://localhost:27017")
synthesizer = UniversalSynthesizer(db)

# Test analysis
print("Analyzing question about comfort...")
result = synthesizer.analyze_sources("I feel lonely and need comfort")
print("\nDetected Themes:", result['themes'])
print("\nBlended Response:", result['response'])
print("\nMood Cues:", result['mood_cues'])