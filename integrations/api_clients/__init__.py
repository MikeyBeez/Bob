"""
API Clients package for Bob v5.0
Contains all API client implementations.
"""

from .base_client import BaseAPIClient
from .ollama_client import OllamaClient, create_ollama_client

__all__ = [
    'BaseAPIClient',
    'OllamaClient', 
    'create_ollama_client',
]
