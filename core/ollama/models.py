"""
models.py - Model management for Ollama
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class ModelManager:
    """Manages Ollama models."""
    
    def __init__(self, connection):
        """
        Initialize model manager.
        
        Args:
            connection: ConnectionManager instance
        """
        self.connection = connection
        self._model_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 300  # 5 minutes
    
    async def list_models(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of available models.
        
        Args:
            force_refresh: Force refresh of cached model list
            
        Returns:
            List of model information dictionaries
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid():
            return list(self._model_cache.values())
        
        # Fetch fresh model list
        response = await self.connection.get("/api/tags")
        models = response.get("models", [])
        
        # Update cache
        self._model_cache = {m["name"]: m for m in models}
        self._cache_timestamp = datetime.now()
        
        return models
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from the Ollama library.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
        """
        try:
            # Note: This is a long-running operation
            # In production, this should be handled with proper progress tracking
            response = await self.connection.post(
                "/api/pull",
                {"name": model_name}
            )
            
            # Invalidate cache after pulling
            self._invalidate_cache()
            
            return response.get("status") == "success"
            
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """
        Delete a model from local storage.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            True if successful
        """
        try:
            await self.connection.delete(
                "/api/delete",
                {"name": model_name}
            )
            
            # Remove from cache
            if model_name in self._model_cache:
                del self._model_cache[model_name]
            
            return True
            
        except Exception as e:
            print(f"Error deleting model {model_name}: {e}")
            return False
    
    async def show_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary
        """
        response = await self.connection.post(
            "/api/show",
            {"name": model_name}
        )
        
        return response
    
    async def copy_model(self, source: str, destination: str) -> bool:
        """
        Copy a model to a new name.
        
        Args:
            source: Source model name
            destination: Destination model name
            
        Returns:
            True if successful
        """
        try:
            await self.connection.post(
                "/api/copy",
                {"source": source, "destination": destination}
            )
            
            self._invalidate_cache()
            return True
            
        except Exception as e:
            print(f"Error copying model {source} to {destination}: {e}")
            return False
    
    async def create_model(self, name: str, modelfile: str) -> bool:
        """
        Create a custom model from a Modelfile.
        
        Args:
            name: Name for the new model
            modelfile: Modelfile content
            
        Returns:
            True if successful
        """
        try:
            response = await self.connection.post(
                "/api/create",
                {"name": name, "modelfile": modelfile}
            )
            
            self._invalidate_cache()
            return response.get("status") == "success"
            
        except Exception as e:
            print(f"Error creating model {name}: {e}")
            return False
    
    def get_cached_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model info from cache if available.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model info or None if not cached
        """
        if self._is_cache_valid():
            return self._model_cache.get(model_name)
        return None
    
    def _is_cache_valid(self) -> bool:
        """Check if the model cache is still valid."""
        if not self._cache_timestamp:
            return False
        
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl
    
    def _invalidate_cache(self):
        """Invalidate the model cache."""
        self._model_cache = {}
        self._cache_timestamp = None
