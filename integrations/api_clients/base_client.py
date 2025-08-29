"""
Base API Client Implementation for Bob v5.0
Provides common functionality for all API clients.
"""

import asyncio
import time
from abc import ABC
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime

# Fix imports for contracts
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from integrations.contracts import (
    ConfigurableAPIClient,
    APIRequest,
    APIResponse,
    APIError,
    APIErrorType,
    ModelInfo,
    ClientConfiguration,
    StreamingChunk,
)


class BaseAPIClient(ConfigurableAPIClient):
    """Base implementation providing common API client functionality"""
    
    def __init__(self, config: Optional[ClientConfiguration] = None):
        """Initialize base client with optional configuration"""
        self._config = config or ClientConfiguration(base_url="")
        self._last_request_time: Optional[datetime] = None
        self._request_count: int = 0
    
    async def configure(self, config: ClientConfiguration) -> bool:
        """Configure the client with new settings"""
        try:
            self._config = config
            return True
        except Exception as e:
            return False
    
    def get_configuration(self) -> ClientConfiguration:
        """Get current client configuration"""
        return self._config
    
    async def estimate_cost(self, prompt: str, model: str) -> float:
        """
        Base cost estimation - override in specific implementations
        Default assumes free local API
        """
        return 0.0
    
    async def health_check(self) -> bool:
        """
        Base health check - override in specific implementations
        """
        try:
            test_result = await self.test_connection()
            return test_result.get('healthy', False)
        except Exception:
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Base connection test - override in specific implementations
        """
        return {
            'healthy': False,
            'message': 'Connection test not implemented',
            'timestamp': datetime.now().isoformat(),
        }
    
    def _create_api_error(
        self, 
        error_type: APIErrorType, 
        message: str, 
        retryable: bool = False,
        suggested_action: Optional[str] = None,
        original_exception: Optional[Exception] = None
    ) -> APIError:
        """Helper to create standardized API errors"""
        return APIError(
            error_type=error_type,
            message=message,
            retryable=retryable,
            suggested_action=suggested_action,
            original_exception=original_exception,
        )
    
    def _track_request(self):
        """Track request for rate limiting and analytics"""
        self._last_request_time = datetime.now()
        self._request_count += 1
    
    def _validate_request(self, request: APIRequest) -> None:
        """Validate request before processing"""
        if not request.prompt.strip():
            raise ValueError("Request prompt cannot be empty")
        if not request.model.strip():
            raise ValueError("Request model cannot be empty")
    
    @property
    def request_count(self) -> int:
        """Number of requests made by this client"""
        return self._request_count
    
    @property
    def last_request_time(self) -> Optional[datetime]:
        """Timestamp of last request"""
        return self._last_request_time
