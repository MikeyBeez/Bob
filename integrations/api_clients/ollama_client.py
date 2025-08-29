"""
Ollama API Client for Bob v5.0
Contract-compliant implementation for local Ollama API integration.
"""

import asyncio
import json
import time
import aiohttp
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime

# Fix imports for base client and contracts
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from .base_client import BaseAPIClient
from integrations.contracts import (
    APIRequest,
    APIResponse,
    APIError,
    APIErrorType,
    ModelInfo,
    ClientConfiguration,
    StreamingChunk,
)


class OllamaClient(BaseAPIClient):
    """Contract-compliant Ollama API client"""
    
    def __init__(self, config: Optional[ClientConfiguration] = None):
        """Initialize Ollama client"""
        default_config = ClientConfiguration(
            base_url="http://localhost:11434",
            timeout=60,
            max_retries=3,
            retry_delay=1.0,
        )
        super().__init__(config or default_config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._available_models: List[ModelInfo] = []
    
    @property
    def client_name(self) -> str:
        """Unique identifier for this API client"""
        return "ollama"
    
    @property
    def base_url(self) -> str:
        """Base URL for API endpoints"""
        return self._config.base_url
    
    @property
    def supported_features(self) -> List[str]:
        """List of supported features"""
        return ["streaming", "local_models", "no_cost"]
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._config.custom_headers,
            )
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def generate_response(self, request: APIRequest) -> APIResponse:
        """Generate response from Ollama API"""
        self._validate_request(request)
        self._track_request()
        
        start_time = time.time()
        
        try:
            await self._ensure_session()
            
            # Prepare request payload
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "stream": False,  # Non-streaming for this method
            }
            
            # Add optional parameters
            if request.system_context:
                payload["system"] = request.system_context
            if request.temperature != 0.7:
                payload["options"] = {"temperature": request.temperature}
            
            # Make API request
            url = f"{self.base_url}/api/generate"
            async with self._session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise aiohttp.ClientError(f"HTTP {response.status}: {error_text}")
                
                response_data = await response.json()
                
                # Extract response content
                content = response_data.get("response", "")
                duration = time.time() - start_time
                
                # Create standardized response
                return APIResponse(
                    content=content,
                    tokens_used=self._estimate_tokens(request.prompt + content),
                    cost=0.0,  # Ollama is free
                    duration=duration,
                    model_used=request.model,
                    success=True,
                    metadata={
                        "ollama_response": response_data,
                        "prompt_tokens": self._estimate_tokens(request.prompt),
                        "completion_tokens": self._estimate_tokens(content),
                    }
                )
                
        except asyncio.TimeoutError:
            raise self._create_api_error(
                APIErrorType.TIMEOUT,
                f"Request timed out after {self._config.timeout} seconds",
                retryable=True,
                suggested_action="Try increasing timeout or check Ollama service"
            )
        except aiohttp.ClientConnectorError as e:
            raise self._create_api_error(
                APIErrorType.CONNECTION,
                f"Cannot connect to Ollama at {self.base_url}",
                retryable=True,
                suggested_action="Check if Ollama is running and accessible",
                original_exception=e
            )
        except json.JSONDecodeError as e:
            raise self._create_api_error(
                APIErrorType.INVALID_REQUEST,
                "Invalid JSON response from Ollama API",
                retryable=False,
                suggested_action="Check Ollama service status",
                original_exception=e
            )
        except Exception as e:
            raise self._create_api_error(
                APIErrorType.UNKNOWN,
                f"Unexpected error: {str(e)}",
                retryable=False,
                original_exception=e
            )
    
    async def stream_response(self, request: APIRequest) -> AsyncGenerator[str, None]:
        """Stream response chunks from Ollama API"""
        self._validate_request(request)
        self._track_request()
        
        try:
            await self._ensure_session()
            
            # Prepare streaming request payload
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "stream": True,
            }
            
            # Add optional parameters
            if request.system_context:
                payload["system"] = request.system_context
            if request.temperature != 0.7:
                payload["options"] = {"temperature": request.temperature}
            
            # Make streaming API request
            url = f"{self.base_url}/api/generate"
            async with self._session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise aiohttp.ClientError(f"HTTP {response.status}: {error_text}")
                
                # Stream response chunks
                async for line in response.content:
                    if line:
                        try:
                            chunk_data = json.loads(line)
                            if "response" in chunk_data:
                                yield chunk_data["response"]
                            if chunk_data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            # Skip malformed JSON lines
                            continue
                            
        except Exception as e:
            raise self._create_api_error(
                APIErrorType.UNKNOWN,
                f"Streaming error: {str(e)}",
                retryable=True,
                original_exception=e
            )
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available Ollama models"""
        try:
            await self._ensure_session()
            
            url = f"{self.base_url}/api/tags"
            async with self._session.get(url) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                models = []
                
                for model_data in data.get("models", []):
                    model_info = ModelInfo(
                        name=model_data.get("name", ""),
                        description=f"Ollama model: {model_data.get('name', 'Unknown')}",
                        max_tokens=4096,  # Default context window
                        cost_per_token=0.0,  # Ollama is free
                        supports_streaming=True,
                        context_window=4096,
                        metadata={
                            "size": model_data.get("size", 0),
                            "modified_at": model_data.get("modified_at"),
                            "digest": model_data.get("digest"),
                        }
                    )
                    models.append(model_info)
                
                self._available_models = models
                return models
                
        except Exception as e:
            # Return cached models if API call fails
            return self._available_models
    
    async def health_check(self) -> bool:
        """Check if Ollama API is accessible"""
        try:
            test_result = await self.test_connection()
            return test_result.get('healthy', False)
        except Exception:
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama API"""
        try:
            await self._ensure_session()
            
            # Try to get version info
            url = f"{self.base_url}/api/version"
            async with self._session.get(url) as response:
                if response.status == 200:
                    version_data = await response.json()
                    return {
                        'healthy': True,
                        'message': 'Ollama API is accessible',
                        'version': version_data.get('version', 'unknown'),
                        'timestamp': datetime.now().isoformat(),
                        'base_url': self.base_url,
                    }
                else:
                    return {
                        'healthy': False,
                        'message': f'HTTP {response.status} from Ollama API',
                        'timestamp': datetime.now().isoformat(),
                        'base_url': self.base_url,
                    }
                    
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Connection failed: {str(e)}',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 characters ≈ 1 token)"""
        return max(1, len(text) // 4)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()


# Factory function for backward compatibility
def create_ollama_client(base_url: str = "http://localhost:11434") -> OllamaClient:
    """Create configured Ollama client"""
    config = ClientConfiguration(base_url=base_url)
    return OllamaClient(config)


# Export the client class and factory
__all__ = ['OllamaClient', 'create_ollama_client']
