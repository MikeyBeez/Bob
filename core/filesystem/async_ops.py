"""
async_ops.py - Asynchronous file operations for FileSystemCore

Handles async file I/O operations using aiofiles when available.
"""

from pathlib import Path
from typing import Union

# Optional async support
try:
    import aiofiles
    ASYNC_AVAILABLE = True
except ImportError:
    aiofiles = None
    ASYNC_AVAILABLE = False

from .validation import PathValidator
from .metrics import MetricsTracker


class AsyncFileOperations:
    """Handles asynchronous file operations."""
    
    def __init__(self, validator: PathValidator, metrics: MetricsTracker, db_core=None):
        """
        Initialize async file operations handler.
        
        Args:
            validator: Path validator instance
            metrics: Metrics tracker instance
            db_core: Optional database core for logging
        """
        self.validator = validator
        self.metrics = metrics
        self.db_core = db_core
    
    async def read_file(self, path: Union[str, Path], mode: str = 'text') -> Union[str, bytes]:
        """
        Asynchronously read file contents.
        
        Args:
            path: Path to file
            mode: 'text' or 'binary'
            
        Returns:
            File contents
            
        Raises:
            ImportError: If aiofiles is not installed
            FileNotFoundError: If file doesn't exist
        """
        if not ASYNC_AVAILABLE:
            raise ImportError("aiofiles not installed. Run: pip install aiofiles")
        
        path = self.validator.validate_path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        async with aiofiles.open(path, mode='r' if mode == 'text' else 'rb') as f:
            content = await f.read()
        
        self.metrics.record_read(len(content))
        return content
    
    async def write_file(self, path: Union[str, Path], content: Union[str, bytes],
                        mode: str = 'text') -> int:
        """
        Asynchronously write content to file.
        
        Args:
            path: Path to write to
            content: Content to write
            mode: 'text' or 'binary'
            
        Returns:
            Number of bytes written
            
        Raises:
            ImportError: If aiofiles is not installed
        """
        if not ASYNC_AVAILABLE:
            raise ImportError("aiofiles not installed. Run: pip install aiofiles")
        
        path = self.validator.validate_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, mode='w' if mode == 'text' else 'wb') as f:
            await f.write(content)
        
        size = len(content)
        self.metrics.record_write(size)
        return size
