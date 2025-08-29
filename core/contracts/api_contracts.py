"""
API Client Contract Definitions for Bob v5.0
Contract-driven architecture for external API integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class APIErrorType(Enum):
    """Types of API errors for categorization"""
    TIMEOUT = "timeout"
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID_REQUEST = "invalid_request"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN = "unknown"


@dataclass
class APIRequest:
    """Standardized API request structure"""
    prompt: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    system_context: Optional[str] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate request parameters"""
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if not self.model.strip():
            raise ValueError("Model cannot be empty")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")


@dataclass
class APIResponse:
    """Standardized API response structure"""
    content: str
    tokens_used: int
    cost: float
    duration: float
    model_used: str
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate response data"""
        if self.tokens_used < 0:
            raise ValueError("tokens_used cannot be negative")
        if self.cost < 0:
            raise ValueError("cost cannot be negative")
        if self.duration < 0:
            raise ValueError("duration cannot be negative")


@dataclass
class APIError:
    """Standardized API error structure"""
    error_type: APIErrorType
    message: str
    retryable: bool
    suggested_action: Optional[str] = None
    original_exception: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInfo:
    """Information about available models"""
    name: str
    description: str
    max_tokens: int
    cost_per_token: float = 0.0
    supports_streaming: bool = True
    context_window: int = 4096
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIClientContract(ABC):
    """Abstract base contract for all API clients"""
    
    @abstractmethod
    async def generate_response(self, request: APIRequest) -> APIResponse:
        """
        Generate response from API
        
        Args:
            request: Standardized API request
            
        Returns:
            APIResponse: Standardized response with content and metadata
            
        Raises:
            APIError: On any API-related error
        """
        pass
    
    @abstractmethod
    async def estimate_cost(self, prompt: str, model: str) -> float:
        """
        Estimate cost for request
        
        Args:
            prompt: The prompt text
            model: Model identifier
            
        Returns:
            float: Estimated cost in USD
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check API availability
        
        Returns:
            bool: True if API is healthy and accessible
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """
        Get list of available models
        
        Returns:
            List[ModelInfo]: List of available models with metadata
        """
        pass
    
    @abstractmethod
    async def stream_response(self, request: APIRequest) -> AsyncGenerator[str, None]:
        """
        Stream response chunks from API
        
        Args:
            request: API request with stream=True
            
        Yields:
            str: Response chunks as they arrive
            
        Raises:
            APIError: On streaming errors
        """
        pass
    
    @property
    @abstractmethod
    def client_name(self) -> str:
        """Unique identifier for this API client"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL for API endpoints"""
        pass
    
    @property
    @abstractmethod
    def supported_features(self) -> List[str]:
        """List of supported features (streaming, embeddings, etc.)"""
        pass


# Export all contract types
__all__ = [
    'APIClientContract',
    'APIRequest', 
    'APIResponse',
    'APIError',
    'APIErrorType',
    'ModelInfo',
]
