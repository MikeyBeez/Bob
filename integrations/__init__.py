"""
Integration package for Bob v5.0
Contains external system integrations and API clients.
"""

from .contracts import (
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
