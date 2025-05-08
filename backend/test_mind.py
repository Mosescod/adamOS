# test_mind_integrator.py
from core.knowledge.mind_integrator import MindIntegrator

integrator = MindIntegrator()

test_cases = [
    {
        'primary_theme': 'mercy',
        'content': 'Allah forgives all sins',
        'quran_refs': ['25:70']
    },
    {
        'primary_theme': 'comfort',
        'content': 'You are not alone in this'
    }
]

for case in test_cases:
    print("\nTest Case:", case['primary_theme'])
    print("Islamic Context:", integrator.integrate(case, {'religion': 'islam'}))
    print("Universal Context:", integrator.integrate(case, {}))