from typing import Callable, Dict
import inspect

class AdamExtender:
    def __init__(self):
        self._extensions: Dict[str, Callable] = {}
    
    def register(self, name: str):
        """Decorator to register new capabilities"""
        def decorator(fn):
            self._extensions[name] = fn
            return fn
        return decorator
    
    def extend(self, adam_instance, extension_name: str, *args):
        """Execute an extension"""
        if extension_name not in self._extensions:
            raise ValueError(f"Unknown extension: {extension_name}")
        
        # Inject Adam instance if needed
        params = inspect.signature(self._extensions[extension_name]).parameters
        if 'adam' in params:
            return self._extensions[extension_name](adam=adam_instance, *args)
        return self._extensions[extension_name](*args)

# Example extension
extender = AdamExtender()

@extender.register("prophetic_vision")
def generate_vision(adam, query: str):
    base = adam.query(query)
    return f"*eyes glow* PROPHECY: {base.upper()}"