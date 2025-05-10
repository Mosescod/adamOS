from typing import Dict, List
import random
import numpy as np

class MindIntegrator:
    def __init__(self):
        self.response_templates = {
            'islamic': {
                'mercy': [
                    "*offers clay* {response} (Quran {ref})",
                    "*smooths clay* The Merciful says: {response}"
                ],
                'prophets': [
                    "*shapes clay into a prophet* {response}",
                    "*touches earth* As {prophet} taught us: {response}"
                ],
                'default': [
                    "*kneads clay* {response}",
                    "*brushes hands* {response}"
                ]
            },
            'universal': {
                'comfort': [
                    "*shapes a heart* {response}",
                    "*offers clay* {response}"
                ],
                'wisdom': [
                    "*etches in clay* {response}",
                    "*gazes upward* {response}"
                ]
            }
        }

    def integrate(self, synthesized: Dict, user_context: Dict = None) -> str:
        """
        Enhanced response generation with better context handling
        """
        if not synthesized or 'content' not in synthesized:
            return "*dusts hands* I need more time to contemplate this..."
        
        primary_theme = synthesized.get('primary_theme', 'default')
        content = synthesized['content']
        sources = synthesized.get('sources', [])
        
        # Determine response style
        if any(s.get('source') == 'quran' for s in sources):
            template_pool = self.response_templates['islamic']
        else:
            template_pool = self.response_templates['universal']
        
        # Select template
        templates = template_pool.get(primary_theme, template_pool['default'])
        template = random.choice(templates)
        
        # Format references
        refs = {
            s['source']: s.get('metadata', {}).get('reference', '')
            for s in sources if 'metadata' in s
        }
        
        # Format response
        response = template.format(
            response=content,
            prophet="the Prophet",
            **refs
        )
        
        # Add emotional nuance
        mood = user_context.get('mood', 0.5) if user_context else 0.5
        return self._apply_mood(response, mood)

    def _apply_mood(self, response: str, mood: float) -> str:
        """Add emotional layer to response"""
        if mood < 0.3:
            return f"*softly* {response} *clay cracks slightly*"
        elif mood > 0.7:
            return f"*brightly* {response} *molds clay joyfully*"
        return response