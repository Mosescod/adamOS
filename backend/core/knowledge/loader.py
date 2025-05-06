from pathlib import Path
import json

class DocumentLoader:
    @staticmethod
    def load_from_json(path: str) -> list:
        """Returns list of document dicts"""
        file_path = Path(path)
        if not file_path.exists():
            return []  # Return empty list instead of raising
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                if isinstance(data, dict):  # Convert old format
                    return [{"text": v, "tags": []} for v in data.values()]
                elif isinstance(data, list):
                    return data
                else:
                    return []
                    
        except json.JSONDecodeError:
            return []  # Fail gracefully