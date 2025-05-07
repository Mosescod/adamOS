from .quran_db import QuranDatabase 
import logging
from typing import Optional, Dict, List
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class DivineKnowledge:
    """Enhanced knowledge processing system with multi-stage reasoning."""
    
    def __init__(self, quran_db: QuranDatabase):
        self.db = quran_db
        self.vectorizer = TfidfVectorizer(
            min_df=2,
            max_df=0.8,
            stop_words='english'
        )
        
        # Knowledge mapping systems
        self._initialize_term_mappings()
        self._initialize_priority_systems()
        self._initialize_response_templates()
        
        # Initialize vectorizer with sample texts
        self._train_vectorizer()
    
    def _initialize_term_mappings(self):
        """Initialize term mappings for natural language conversion."""
        self.term_map = {
            "Allah": "the Lord",
            "Paradise": "the Garden",
            "Messenger": "Prophet",
            "We": "I",
            "verily": "truly",
            "disbelieve": "turn away",
            "polytheists": "those who associate others with God",
            "worship": "serve"
        }
    
    def _initialize_priority_systems(self):
        """Initialize priority verses and themes."""
        self.priority_verses = {
            "creation": "15:26-29",
            "afterlife": "2:25",
            "forgiveness": "39:53",
            "adam": "2:30-33",
            "eve": "4:1",
            "lonely": "94:5-6",
            "patience": "2:153",
            "hell": "3:131",
            "depression": "94:5",
            "comfort": "2:286",
            "relationships": "30:21"
        }
        
        self.theme_hierarchies = {
            "creation": ["origin", "human", "clay", "shape"],
            "mercy": ["forgive", "compassion", "repent", "mercy"],
            "prophets": ["messenger", "warner", "scripture"]
        }
    
    def _initialize_response_templates(self):
        """Initialize response templates for various contexts."""
        self.natural_responses = {
            'creation': [
                "*shaping clay into human form* The same Lord who molded me from this earth shaped you too",
                "*kneading clay* We're fashioned from the same divine clay, you and I"
            ],
            'hell': [
                "*clay darkens* Fire awaits those who turn away - not as punishment, but as hardened hearts' natural end",
                "*presses clay firmly* The unrepentant heart creates its own fire"
            ],
            'love': [
                "*clay forms two interlocked hands* Love is the moisture that makes souls pliable",
                "*softens clay* The Lord placed affection between hearts like water in clay"
            ],
            'mercy': [
                "*offers clay piece* No soul is so broken it can't be reshaped",
                "*smoothing cracks* The Lord's mercy is softer than fresh clay"
            ],
            'default': [
                "*reshapes clay* The answer eludes me today",
                "*brushes hands* This truth hasn't been revealed to me yet"
            ]
        }
        
        self.certainty_templates = {
            'high': [
                "*firm shaping* The truth is clear: {text}",
                "*steady hands* {text} - this I know with certainty"
            ],
            'medium': [
                "*tilts head* This may answer: {text}",
                "*soft shaping* Perhaps consider: {text}"
            ],
            'low': [
                "*experimental shaping* Might this resonate? {text}",
                "*testing clay* One perspective: {text}"
            ]
        }
    
    def _train_vectorizer(self):
        """Train the TF-IDF vectorizer with sample texts."""
        sample_texts = [
            " ".join(self.term_map.keys()),
            " ".join(self.priority_verses.keys()),
            " ".join([" ".join(words) for words in self.theme_hierarchies.values()])
        ]
        self.vectorizer.fit(sample_texts)
    
    def retrieve_knowledge(self, question: str, context: Dict) -> Dict:
        """
        Stage 1: Retrieve relevant knowledge from all sources.
        
        Returns:
            Dictionary containing:
            - verses: List of relevant verses
            - themes: Identified themes
            - sources: Knowledge sources used
            - confidence: Initial confidence scores
        """
              
        knowledge = {
            'verses': [],
            'themes': [],
            'sources': [],
            'confidence': 0.0
        }
        
        # Check for priority verses first
        priority_results = self._check_priority_verses(question, context)
        if priority_results:
            knowledge.update(priority_results)
            knowledge['confidence'] = 0.9
            return knowledge
        
        # Perform thematic search
        theme_results = self._thematic_search(question)
        if theme_results['verses']:
            knowledge.update(theme_results)
            knowledge['confidence'] = 0.7
            return knowledge
        
        # Fallback to general search
        search_results = self._general_search(question)
        knowledge.update(search_results)
        knowledge['confidence'] = 0.5
        
        return knowledge
    
    def analyze_context(self, question: str, knowledge: Dict, context: Dict) -> Dict:
        """
        Stage 2: Analyze knowledge in context.
        
        Returns:
            Analysis dictionary containing:
            - primary_theme: Main identified theme
            - secondary_themes: Additional relevant themes
            - emotional_context: Emotional analysis
            - certainty: Confidence score (0-1)
            - response_strategy: Chosen response approach
        """
        analysis = {
            'primary_theme': None,
            'secondary_themes': [],
            'emotional_context': context['emotional'],
            'certainty': knowledge.get('confidence', 0.5),
            'response_strategy': 'direct'
        }
        
        # Determine themes
        if knowledge.get('themes'):
            analysis['primary_theme'] = knowledge['themes'][0]
            analysis['secondary_themes'] = knowledge['themes'][1:]
        
        # Adjust certainty based on context
        analysis = self._adjust_certainty(analysis, context['conversation'])
        
        # Determine response strategy
        analysis['response_strategy'] = self._determine_response_strategy(analysis)
        
        return analysis
    
    def synthesize_response(self, question: str, knowledge: Dict, analysis: Dict) -> str:
        """
        Stage 3: Synthesize final response.
        
        Args:
            question: Original user question
            knowledge: Retrieved knowledge
            analysis: Context analysis
            
        Returns:
            Formatted response string
        """
        # Select base content
        if knowledge.get('verses'):
            content = self._select_verse_content(knowledge['verses'], analysis)
        else:
            content = self.get_natural_response(analysis.get('primary_theme', 'default'))
        
        # Apply formatting based on analysis
        return self._format_response(content, analysis)
    
    def _check_priority_verses(self, question: str, context: Dict) -> Dict:
        """Check for priority verse matches."""
        question_lower = question.lower()
        results = {}
        
        # Check context first
        if context and context.get('last_theme'):
            last_theme = context['last_theme']
            if last_theme in self.priority_verses:
                if verse := self._get_verse_by_ref(self.priority_verses[last_theme]):
                    results = {
                        'verses': [verse],
                        'themes': [last_theme],
                        'sources': ['context_priority']
                    }
                    return results
        
        # Check question directly
        for theme, ref in self.priority_verses.items():
            if theme in question_lower:
                if verse := self._get_verse_by_ref(ref):
                    results = {
                        'verses': [verse],
                        'themes': [theme],
                        'sources': ['direct_priority']
                    }
                    return results
        
        return {}
    
    def _thematic_search(self, question: str) -> Dict:
        """Search verses by identified themes."""
        themes = self._identify_themes(question)
        results = {
            'verses': [],
            'themes': themes,
            'sources': ['thematic']
        }
        
        for theme in themes:
            verses = self.db.get_verses_by_theme(theme, limit=2)
            results['verses'].extend(verses)
        
        return results
    
    def _general_search(self, question: str) -> Dict:
        """Perform general verse search."""
        verses = self.db.search_verses(question, limit=3)
        return {
            'verses': verses,
            'themes': [],
            'sources': ['general_search']
        }
    
    def _identify_themes(self, text: str) -> List[str]:
        """Identify relevant themes using semantic similarity."""
        themes = list(self.theme_hierarchies.keys())
        if not themes:
            return []
        
        # Vectorize input and themes
        text_vec = self.vectorizer.transform([text])
        theme_texts = [" ".join([theme] + keywords) for theme, keywords in self.theme_hierarchies.items()]
        theme_vecs = self.vectorizer.transform(theme_texts)
        
        # Calculate similarities
        sims = cosine_similarity(text_vec, theme_vecs)[0]
        sorted_indices = np.argsort(sims)[::-1]
        
        # Return themes above threshold
        threshold = 0.3
        return [themes[i] for i in sorted_indices if sims[i] > threshold]
    
    def _adjust_certainty(self, analysis: Dict, conversation_context: Dict) -> Dict:
        """Adjust certainty based on conversation context."""
        certainty = analysis['certainty']
        
        # Boost if continuing same theme
        if (analysis['primary_theme'] and 
            conversation_context.get('last_theme') == analysis['primary_theme']):
            certainty = min(1.0, certainty + 0.15)
        
        # Reduce if conflicting with recent themes
        if (analysis['primary_theme'] and 
            conversation_context.get('recent_themes') and
            analysis['primary_theme'] not in conversation_context.get('recent_themes', {})):
            certainty = max(0.3, certainty - 0.1)
        
        analysis['certainty'] = certainty
        return analysis
    
    def _determine_response_strategy(self, analysis: Dict) -> str:
        """Determine appropriate response strategy."""
        certainty = analysis['certainty']
        
        if certainty > 0.8:
            return 'direct'
        elif certainty > 0.6:
            return 'suggestive'
        elif analysis['primary_theme']:
            return 'exploratory'
        return 'fallback'
    
    def _select_verse_content(self, verses: List[Dict], analysis: Dict) -> Dict:
        """Select appropriate verse content based on analysis."""
        if analysis['response_strategy'] == 'direct':
            return verses[0]
        
        # For lower certainty, sometimes return multiple verses
        if len(verses) > 1 and random.random() < 0.4:
            return {
                'text': "\n".join(v['text'] for v in verses[:2]),
                'surah_number': 'multiple',
                'ayah_number': ''
            }
        return random.choice(verses)
    
    def _format_response(self, content: Dict, analysis: Dict) -> str:
        """Format response based on analysis."""
        certainty = analysis['certainty']
        
        if isinstance(content, str):
            return content
        
        # Determine template set
        if certainty > 0.8:
            templates = self.certainty_templates['high']
        elif certainty > 0.6:
            templates = self.certainty_templates['medium']
        else:
            templates = self.certainty_templates['low']
        
        # Format with template
        template = random.choice(templates)
        return template.format(
            text=content['text'],
            surah=content.get('surah_number', ''),
            ayah=content.get('ayah_number', '')
        )
    
    def get_natural_response(self, theme: str) -> str:
        """Get natural language response for common themes."""
        return random.choice(self.natural_responses.get(theme, self.natural_responses['default']))
    
    def _get_verse_by_ref(self, ref: str) -> Optional[Dict]:
        """Get verse by reference with error handling."""
        try:
            return self.db.get_verse_by_reference(ref)
        except Exception as e:
            logger.error(f"Failed to get verse {ref}: {str(e)}")
            return None