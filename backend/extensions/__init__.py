from typing import Dict, Callable

class ExtensionManager:
    def __init__(self):
        self.extensions: Dict[str, Callable] = {}
    
    def register(self, name: str):
        def decorator(func):
            self.extensions[name] = func
            return func
        return decorator
    
    def execute(self, name: str, *args, **kwargs):
        if name not in self.extensions:
            raise ValueError(f"Extension '{name}' not found")
        return self.extensions[name](*args, **kwargs)

manager = ExtensionManager()

# Example extension
@manager.register("prophecy")
def make_prophecy(text: str):
    return f"*visions swirl* {text.upper()}"