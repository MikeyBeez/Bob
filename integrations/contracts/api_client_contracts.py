"""
Integration Layer Contract Definitions for Bob v5.0
Contracts for external system integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

# Import from core contracts - fix relative import
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.contracts import (
    APIClientContract,
    APIRequest,
    APIResponse,
    APIError,
    APIErrorType,
    ModelInfo,
)


@dataclass
class ClientConfiguration:
    """Configuration for API clients"""
    base_url: str
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    api_key: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    model_overrides: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class StreamingChunk:
    """Individual chunk from streaming response"""
    content: str
    is_final: bool = False
    tokens_so_far: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigurableAPIClient(APIClientContract):
    """Extended API client contract with configuration support"""
    
    @abstractmethod
    async def configure(self, config: ClientConfiguration) -> bool:
        """
        Configure the client with new settings
        
        Args:
            config: Client configuration
            
        Returns:
            bool: True if configuration was applied successfully
        """
        pass
    
    @abstractmethod
    def get_configuration(self) -> ClientConfiguration:
        """
        Get current client configuration
        
        Returns:
            ClientConfiguration: Current configuration
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection and return diagnostic information
        
        Returns:
            Dict[str, Any]: Connection test results and diagnostics
        """
        pass


# Export all integration contracts
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
