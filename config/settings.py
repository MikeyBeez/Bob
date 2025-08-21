"""
Configuration management for Bob
"""

import os
from pathlib import Path
from typing import Dict, Any
import json

def load_config() -> Dict[str, Any]:
    """Load Bob's configuration"""
    config_dir = Path(__file__).parent
    
    # Default configuration
    config = {
        "ollama_host": "http://localhost:11434",
        "thinking_model": "llama3.2",
        "knowledge_db_path": str(Path.home() / "Bob" / "data" / "knowledge.db"),
        "vector_store_path": str(Path.home() / "Bob" / "data" / "vectors"),
        "max_context_length": 4096,
        "temperature": 0.7,
        "debug": False,
        "log_level": "INFO"
    }
    
    # Try to load user config
    user_config_path = config_dir / "config.json"
    if user_config_path.exists():
        try:
            with open(user_config_path, 'r') as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load user config: {e}")
    
    # Override with environment variables
    env_overrides = {
        "OLLAMA_HOST": "ollama_host",
        "BOB_MODEL": "thinking_model",
        "BOB_DEBUG": "debug",
        "BOB_LOG_LEVEL": "log_level"
    }
    
    for env_var, config_key in env_overrides.items():
        if os.getenv(env_var):
            if config_key == "debug":
                config[config_key] = os.getenv(env_var).lower() == "true"
            else:
                config[config_key] = os.getenv(env_var)
    
    return config

def save_config(config: Dict[str, Any]):
    """Save configuration to file"""
    config_dir = Path(__file__).parent
    config_path = config_dir / "config.json"
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
