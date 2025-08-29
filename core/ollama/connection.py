"""
connection.py - HTTP connection management for Ollama API
"""

import aiohttp
import asyncio
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager


class ConnectionManager:
    """Manages HTTP connections to Ollama API."""
    
    def __init__(self, base_url: str, timeout: int):
        """
        Initialize connection manager.
        
        Args:
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
    @asynccontextmanager
    async def _get_session(self):
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        try:
            yield self._session
        except Exception:
            # Don't close on error, let retry logic handle it
            raise
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        async with self._get_session() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute POST request.
        
        Args:
            endpoint: API endpoint path
            data: JSON data to send
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        async with self._get_session() as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                return await response.json()
    
    async def post_stream(self, endpoint: str, data: Dict[str, Any]):
        """
        Execute POST request with streaming response.
        
        Args:
            endpoint: API endpoint path
            data: JSON data to send
            
        Yields:
            Streaming response lines
        """
        url = f"{self.base_url}{endpoint}"
        
        async with self._get_session() as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        yield line
    
    async def delete(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute DELETE request.
        
        Args:
            endpoint: API endpoint path
            data: Optional JSON data
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        async with self._get_session() as session:
            kwargs = {"json": data} if data else {}
            async with session.delete(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
    
    async def close(self):
        """Close the connection session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def __del__(self):
        """Cleanup session on deletion."""
        if self._session and not self._session.closed:
            try:
                asyncio.create_task(self._session.close())
            except RuntimeError:
                # Event loop might be closed
                pass
