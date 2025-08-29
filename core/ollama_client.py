"""
ollama_client.py - Clean API for Ollama LLM communication

This is the main API module for Bob's Ollama integration.
Implementation details are hidden in submodules for clarity.
Following the modular pattern established in FileSystemCore.
"""

from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from pathlib import Path

# Import implementation modules
from .ollama.connection import ConnectionManager
from .ollama.streaming import StreamHandler
from .ollama.retry import RetryManager
from .ollama.models import ModelManager
from .ollama.metrics import OllamaMetrics


class OllamaClient:
    """
    Clean API for Ollama LLM communication.
    
    This is the clean API surface for interacting with Ollama.
    All implementation details are delegated to specialized submodules.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 timeout: int = 60,
                 max_retries: int = 3):
        """
        Initialize OllamaClient with configuration.
        
        Args:
            base_url: Ollama API endpoint
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        # Initialize submodules
        self.connection = ConnectionManager(base_url, timeout)
        self.stream_handler = StreamHandler()
        self.retry_manager = RetryManager(max_retries)
        self.model_manager = ModelManager(self.connection)
        self.metrics = OllamaMetrics()
        
        # Store configuration
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
    
    # === CORE GENERATION METHODS ===
    
    async def generate(self, 
                      prompt: str,
                      model: str = "llama2",
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      stream: bool = False,
                      **kwargs) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate response from Ollama model.
        
        Args:
            prompt: Input text prompt
            model: Model name to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional model parameters
            
        Returns:
            Generated text or async generator for streaming
        """
        # Track metrics
        self.metrics.track_request(model, prompt)
        
        # Build request
        request = self._build_request(prompt, model, temperature, max_tokens, **kwargs)
        
        # Execute with retry logic
        if stream:
            return self._generate_stream(request)
        else:
            return await self._generate_complete(request)
    
    async def chat(self,
                   messages: List[Dict[str, str]],
                   model: str = "llama2",
                   temperature: float = 0.7,
                   **kwargs) -> str:
        """
        Chat completion with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name to use
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        self.metrics.track_chat(model, len(messages))
        
        request = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = await self.retry_manager.execute(
            self.connection.post,
            "/api/chat",
            request
        )
        
        return response.get("message", {}).get("content", "")
    
    # === MODEL MANAGEMENT ===
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        return await self.model_manager.list_models()
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from the Ollama library."""
        return await self.model_manager.pull_model(model_name)
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model from local storage."""
        return await self.model_manager.delete_model(model_name)
    
    async def show_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model."""
        return await self.model_manager.show_info(model_name)
    
    # === HEALTH & STATUS ===
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            response = await self.connection.get("/api/tags")
            return response is not None
        except Exception:
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics and statistics."""
        return self.metrics.get_stats()
    
    # === EMBEDDINGS ===
    
    async def generate_embeddings(self, 
                                 text: str,
                                 model: str = "llama2") -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Input text to embed
            model: Model to use for embeddings
            
        Returns:
            List of embedding values
        """
        request = {
            "model": model,
            "prompt": text
        }
        
        response = await self.retry_manager.execute(
            self.connection.post,
            "/api/embeddings",
            request
        )
        
        return response.get("embedding", [])
    
    # === PRIVATE HELPER METHODS ===
    
    def _build_request(self, prompt: str, model: str, 
                      temperature: float, max_tokens: Optional[int],
                      **kwargs) -> Dict[str, Any]:
        """Build request dictionary for Ollama API."""
        request = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            request["num_predict"] = max_tokens
            
        return request
    
    async def _generate_complete(self, request: Dict[str, Any]) -> str:
        """Generate complete response without streaming."""
        response = await self.retry_manager.execute(
            self.connection.post,
            "/api/generate",
            {**request, "stream": False}
        )
        
        self.metrics.track_response(
            request["model"],
            response.get("total_duration", 0),
            response.get("eval_count", 0)
        )
        
        return response.get("response", "")
    
    async def _generate_stream(self, request: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        async for chunk in self.stream_handler.handle_stream(
            self.connection,
            "/api/generate",
            {**request, "stream": True}
        ):
            yield chunk
    
    # === CONTEXT MANAGEMENT ===
    
    async def create_context(self, model: str, context: str) -> str:
        """Create a reusable context for a model."""
        request = {
            "model": model,
            "prompt": context,
            "keep_alive": "5m"
        }
        
        response = await self.connection.post("/api/generate", request)
        return response.get("context", "")
    
    async def clear_context(self, model: str) -> bool:
        """Clear the context for a model."""
        request = {
            "model": model,
            "keep_alive": "0s"
        }
        
        try:
            await self.connection.post("/api/generate", request)
            return True
        except Exception:
            return False
