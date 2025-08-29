"""
Core package for Bob v5.0
Contains business logic contracts and implementations.
"""

from .contracts import (
    APIClientContract,
    APIRequest,
    APIResponse,
    APIError,
    APIErrorType,
    ModelInfo,
)

__all__ = [
    'APIClientContract',
    'APIRequest', 
    'APIResponse',
    'APIError',
    'APIErrorType',
    'ModelInfo',
]
