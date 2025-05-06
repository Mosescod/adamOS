from abc import ABC, abstractmethod

class AdamAICore:
    def __init__(self, config):
        self.config = config
        self.modules = {
            'knowledge': {},
            'personality': {},
            'response': []
        }
        self._load_modules()

    def _load_modules(self):
        # Knowledge modules
        for name, module_config in self.config['knowledge'].items():
            module_class = globals()[module_config['class']]
            self.modules['knowledge'][name] = module_class(**module_config.get('params', {}))
        
        # Personality modules
        for name, module_config in self.config['personality'].items():
            module_class = globals()[module_config['class']]
            self.modules['personality'][name] = module_class(**module_config.get('params', {}))
        
        # Response modules
        for module_config in self.config['response']:
            module_class = globals()[module_config['class']]
            self.modules['response'].append(module_class(**module_config.get('params', {})))

    def process(self, query, context=None):
        context = context or {}
        
        # Knowledge retrieval
        knowledge = {}
        for name, module in self.modules['knowledge'].items():
            knowledge[name] = module.search(query)
        
        # Personality processing
        processed = knowledge
        for name, module in self.modules['personality'].items():
            processed = module.transform(query, processed, context)
        
        # Response generation
        for module in self.modules['response']:
            try:
                return module.generate(processed, context)
            except Exception as e:
                continue
        
        return "I couldn't formulate a proper response."