"""
filesystem_core.py - Clean API for safe file operations

This is the main API module for Bob's file system operations.
Implementation details are hidden in submodules for clarity.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import implementation modules
from .filesystem.operations import FileOperations
from .filesystem.validation import PathValidator
from .filesystem.metrics import MetricsTracker
from .filesystem.async_ops import AsyncFileOperations


class FileSystemCore:
    """
    Safe file system operations with validation and monitoring.
    
    This is the clean API surface. All implementation details are
    delegated to specialized submodules.
    """
    
    def __init__(self, db_core=None, base_path: str = None):
        """Initialize FileSystemCore with optional database connection."""
        base_path = Path(base_path or "~/Bob/data").expanduser()
        
        # Initialize submodules
        self.validator = PathValidator(base_path)
        self.metrics = MetricsTracker()
        self.operations = FileOperations(self.validator, self.metrics, db_core)
        self.async_ops = AsyncFileOperations(self.validator, self.metrics, db_core)
        
        # Expose key properties
        self.base_path = base_path
        self.db_core = db_core
    
    # === READ OPERATIONS ===
    
    def read_file(self, path: Union[str, Path], mode: str = 'text') -> Union[str, bytes]:
        """Read file contents with validation."""
        return self.operations.read_file(path, mode)
    
    def read_json(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Read and parse JSON file."""
        return self.operations.read_json(path)
    
    # === WRITE OPERATIONS ===
    
    def write_file(self, path: Union[str, Path], content: Union[str, bytes], 
                   mode: str = 'text', atomic: bool = True) -> int:
        """Write content to file with atomic operations."""
        return self.operations.write_file(path, content, mode, atomic)
    
    def write_json(self, path: Union[str, Path], data: Any, indent: int = 2) -> int:
        """Write data as JSON to file."""
        return self.operations.write_json(path, data, indent)
    
    def append_file(self, path: Union[str, Path], content: str) -> int:
        """Append content to existing file."""
        return self.operations.append_file(path, content)
    
    # === DELETE OPERATIONS ===
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """Safely delete a file."""
        return self.operations.delete_file(path)
    
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """Delete a directory."""
        return self.operations.delete_directory(path, recursive)
    
    # === DIRECTORY OPERATIONS ===
    
    def create_directory(self, path: Union[str, Path]) -> Path:
        """Create directory with all parent directories."""
        return self.operations.create_directory(path)
    
    def list_directory(self, path: Union[str, Path], pattern: str = "*",
                      recursive: bool = False) -> List[Path]:
        """List directory contents with optional filtering."""
        return self.operations.list_directory(path, pattern, recursive)
    
    # === UTILITY OPERATIONS ===
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """Copy file from source to destination."""
        return self.operations.copy_file(source, destination)
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """Move file from source to destination."""
        return self.operations.move_file(source, destination)
    
    def file_exists(self, path: Union[str, Path]) -> bool:
        """Check if file exists within sandbox."""
        return self.operations.file_exists(path)
    
    def directory_exists(self, path: Union[str, Path]) -> bool:
        """Check if directory exists within sandbox."""
        return self.operations.directory_exists(path)
    
    def get_file_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get detailed file information."""
        return self.operations.get_file_info(path)
    
    def get_directory_size(self, path: Union[str, Path]) -> int:
        """Calculate total size of directory and its contents."""
        return self.operations.get_directory_size(path)
    
    # === ASYNC OPERATIONS ===
    
    async def async_read_file(self, path: Union[str, Path], mode: str = 'text') -> Union[str, bytes]:
        """Asynchronously read file contents."""
        return await self.async_ops.read_file(path, mode)
    
    async def async_write_file(self, path: Union[str, Path], content: Union[str, bytes],
                              mode: str = 'text') -> int:
        """Asynchronously write content to file."""
        return await self.async_ops.write_file(path, content, mode)
    
    # === METRICS ===
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.metrics.get_metrics()
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics.reset()
    
    # === SANDBOX MANAGEMENT ===
    
    def add_sandbox_path(self, path: Union[str, Path]):
        """Add a new path to the sandbox."""
        self.validator.add_sandbox_path(path)
    
    def remove_sandbox_path(self, path: Union[str, Path]):
        """Remove a path from the sandbox."""
        self.validator.remove_sandbox_path(path)
    
    def get_sandbox_paths(self) -> List[str]:
        """Get list of current sandboxed paths."""
        return self.validator.get_sandbox_paths()


# === FACTORY FUNCTION ===

def create_filesystem_core(db_core=None, base_path: str = None) -> FileSystemCore:
    """
    Factory function to create FileSystemCore instance.
    
    Args:
        db_core: Optional DatabaseCore instance
        base_path: Optional base path for operations
        
    Returns:
        Configured FileSystemCore instance
    """
    return FileSystemCore(db_core=db_core, base_path=base_path)
