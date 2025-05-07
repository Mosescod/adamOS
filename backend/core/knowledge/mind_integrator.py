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
        Transforms synthesized knowledge into Adam's natural response.
        
        Args:
            synthesized: {
                'primary_theme': 'mercy',
                'content': 'Allah forgives all sins',
                'quran_refs': ['25:70'],
                'confidence': 0.9
            }
            user_context: {
                'religion': 'islam',  # or 'christian', None
                'mood': 0.7,         # 0-1 scale
                'is_offensive': False
            }
        """
        # Select template pool based on context
        template_pool = (
            self.response_templates['islamic'] 
            if user_context and user_context.get('religion') == 'islam'
            else self.response_templates['universal']
        )
        
        # Get theme-specific templates or fallback
        theme = synthesized.get('primary_theme', 'default')
        templates = template_pool.get(theme, template_pool['default'])
        
        # Format response
        response_text = synthesized['content']
        if 'quran_refs' in synthesized and theme != 'universal':
            ref = synthesized['quran_refs'][0] if synthesized['quran_refs'] else ''
            response_text = response_text.replace('(Quran {ref})', f'(Quran {ref})' if ref else '')
        
        # Apply template
        response = random.choice(templates).format(
            response=response_text,
            prophet="the Prophet"  # Default if none specified
        )
        
        # Add mood nuance
        mood = user_context.get('mood', 0.5) if user_context else 0.5
        response = self._apply_mood(response, mood)
        
        return response

    def _apply_mood(self, response: str, mood: float) -> str:
        """Add emotional layer to response"""
        if mood < 0.3:
            return f"*softly* {response} *clay cracks slightly*"
        elif mood > 0.7:
            return f"*brightly* {response} *molds clay joyfully*"
        return response