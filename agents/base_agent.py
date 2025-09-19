from typing import Dict, Any

class BaseAgent:
    """Base class for all agents in the system."""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
