"""
Core contracts package for Bob v5.0
Contains all interface contracts for the system.
"""

from .api_contracts import (
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
