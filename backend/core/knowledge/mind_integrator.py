from typing import Dict, List
import random
import numpy as np
from collections import defaultdict

class MindIntegrator:
    def __init__(self):
        self.response_templates = {
            'islamic': {
                'mercy': [
                    "*offers clay* {response} (Quran {ref})",
                    "*smooths clay* The Merciful says: {response}",
                    "*shapes crescent* {response} (Surah {surah}, Ayah {ayah})"
                ],
                'prophets': [
                    "*shapes clay into a prophet* {response}",
                    "*touches earth* As {prophet} taught us: {response}",
                    "*etches name in clay* The story of {prophet} reminds us: {response}"
                ],
                'prayer': [
                    "*forms prayer beads* {response}",
                    "*kneads clay* In times of need: {response}",
                    "*shapes hands upward* The Quran teaches us to pray: {response}"
                ],
                'default': [
                    "*kneads clay* {response}",
                    "*brushes hands* {response}",
                    "*shapes words* {response}"
                ]
            },
            'universal': {
                'comfort': [
                    "*shapes a heart* {response}",
                    "*offers clay* {response}",
                    "*molds comforting shape* {response}"
                ],
                'wisdom': [
                    "*etches in clay* {response}",
                    "*gazes upward* {response}",
                    "*forms ancient symbols* {response}"
                ],
                'default': [
                    "*shapes thought* {response}",
                    "*molds clay* {response}",
                    "*considers carefully* {response}"
                ]
            }
        }
        self.theme_icons = {
            'mercy': "🕋",
            'prophets': "✋",
            'prayer': "📿",
            'comfort': "💖", 
            'wisdom': "🧠"
        }

    def integrate(self, synthesized: Dict, user_context: Dict = None) -> str:
        """
        Enhanced response generation with multi-source integration
        """
        if not synthesized or 'content' not in synthesized:
            return "*dusts hands* I need more time to contemplate this..."
        
        primary_theme = synthesized.get('primary_theme', 'default')
        content = synthesized['content']
        sources = synthesized.get('sources', [])
        supporting = synthesized.get('supporting_sources', [])
        
        # Determine response style based on primary source
        if any(s.get('source') == 'quran' for s in sources):
            template_pool = self.response_templates['islamic']
            icon = self.theme_icons.get(primary_theme, "🕌")
        else:
            template_pool = self.response_templates['universal']
            icon = self.theme_icons.get(primary_theme, "💭")
        
        # Select template
        templates = template_pool.get(primary_theme, template_pool['default'])
        template = random.choice(templates)
        
        # Extract references from all sources
        refs = self._extract_references(sources + supporting)
        
        # Format response
        response = template.format(
            response=content,
            prophet=self._get_prophet_name(sources),
            icon=icon,
            **refs
        )
        
        # Add emotional nuance
        mood = synthesized.get('mood_score', 0.5)
        return self._apply_mood(response, mood)

    def _extract_references(self, sources: List[Dict]) -> Dict:
        """Extract and format references from all sources"""
        refs = defaultdict(list)
        
        for s in sources:
            if 'metadata' in s:
                meta = s['metadata']
                if 'reference' in meta:
                    refs[s['source']].append(meta['reference'])
                if 'surah_name' in meta and 'ayah_number' in meta:
                    refs['quran_detail'].append(
                        f"{meta['surah_name']}:{meta['ayah_number']}"
                    )
        
        # Format for string interpolation
        return {
            'ref': ', '.join(refs.get('quran', [])),
            'surah': refs.get('quran_detail', [''])[0].split(':')[0],
            'ayah': refs.get('quran_detail', [''])[0].split(':')[-1]
        }

    def _get_prophet_name(self, sources: List[Dict]) -> str:
        """Extract prophet name if relevant"""
        for s in sources:
            if 'metadata' in s and 'prophet' in s['metadata']:
                return s['metadata']['prophet']
            if 'tags' in s and any('prophet' in tag for tag in s['tags']):
                return "the Prophet"
        return "the Prophet"

    def _apply_mood(self, response: str, mood: float) -> str:
        """Add emotional layer to response"""
        if mood < 0.3:
            return f"*softly* {response} *clay cracks slightly*"
        elif mood > 0.7:
            return f"*brightly* {response} *molds clay joyfully*"
        return response