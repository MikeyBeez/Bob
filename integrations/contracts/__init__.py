"""
Integration contracts package for Bob v5.0
Contains all interface contracts for external integrations.
"""

from .api_client_contracts import (
    APIClientContract,
    APIRequest,
    APIResponse,
    APIError,
    APIErrorType,
    ModelInfo,
    ConfigurableAPIClient,
    ClientConfiguration,
    StreamingChunk,
)

__all__ = [
    'APIClientContract',
    'APIRequest',
    'APIResponse',
    'APIError',
    'APIErrorType', 
    'ModelInfo',
    'ConfigurableAPIClient',
    'ClientConfiguration',
    'StreamingChunk',
]
