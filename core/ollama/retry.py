"""
retry.py - Retry logic and error handling for Ollama API calls
"""

import asyncio
import aiohttp
from typing import Any, Callable, Optional, TypeVar, Coroutine
from functools import wraps

T = TypeVar('T')


class RetryManager:
    """Manages retry logic for API calls."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize retry manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries (exponential backoff)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retry_errors = (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            ConnectionError,
        )
    
    async def execute(self,
                     func: Callable[..., Coroutine[Any, Any, T]],
                     *args,
                     **kwargs) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
                
            except self.retry_errors as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate exponential backoff delay
                    delay = self.base_delay * (2 ** attempt)
                    
                    print(f"Retry {attempt + 1}/{self.max_retries} after {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    print(f"All {self.max_retries + 1} attempts failed")
                    
            except Exception as e:
                # Non-retryable error
                print(f"Non-retryable error: {e}")
                raise
        
        # Raise the last exception if all retries failed
        if last_exception:
            raise last_exception
    
    def with_retry(self, func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        """
        Decorator to add retry logic to an async function.
        
        Args:
            func: Async function to wrap
            
        Returns:
            Wrapped function with retry logic
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await self.execute(func, *args, **kwargs)
        return wrapper
    
    def is_retryable_error(self, error: Exception) -> bool:
        """
        Check if an error is retryable.
        
        Args:
            error: Exception to check
            
        Returns:
            True if error should trigger retry
        """
        return isinstance(error, self.retry_errors)
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a retry attempt.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        return self.base_delay * (2 ** attempt)


class OllamaError(Exception):
    """Base exception for Ollama-specific errors."""
    pass


class ModelNotFoundError(OllamaError):
    """Raised when a requested model is not available."""
    pass


class ContextTooLongError(OllamaError):
    """Raised when the context exceeds model limits."""
    pass


class ServiceUnavailableError(OllamaError):
    """Raised when Ollama service is not available."""
    pass
