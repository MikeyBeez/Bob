"""
Ollama submodules for Bob's modular architecture.

This package contains the implementation details for OllamaClient,
following the modular pattern established in FileSystemCore.
"""

from .connection import ConnectionManager
from .streaming import StreamHandler
from .retry import RetryManager, OllamaError, ModelNotFoundError, ContextTooLongError, ServiceUnavailableError
from .models import ModelManager
from .metrics import OllamaMetrics

__all__ = [
    'ConnectionManager',
    'StreamHandler', 
    'RetryManager',
    'ModelManager',
    'OllamaMetrics',
    'OllamaError',
    'ModelNotFoundError',
    'ContextTooLongError',
    'ServiceUnavailableError'
]
