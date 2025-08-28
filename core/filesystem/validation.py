"""
validation.py - Path validation and sandboxing for FileSystemCore

Handles all path validation, sandboxing, and security checks.
"""

from pathlib import Path
from typing import List, Union


class PathValidator:
    """Validates paths and enforces sandbox restrictions."""
    
    def __init__(self, base_path: Path):
        """
        Initialize validator with base sandbox path.
        
        Args:
            base_path: Primary sandbox directory
        """
        self.base_path = Path(base_path).expanduser().resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize sandbox with base path and Bob directory
        self.sandboxed_paths = [
            self.base_path,
            Path("~/Bob").expanduser().resolve(),
        ]
    
    def validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate and resolve a path, ensuring it's within sandbox.
        
        Args:
            path: Path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If path is outside sandbox or invalid
        """
        path = Path(path).expanduser().resolve()
        
        # Check if path is within any sandboxed directory
        is_valid = any(
            path == sandbox or sandbox in path.parents or path in sandbox.parents
            for sandbox in self.sandboxed_paths
        )
        
        if not is_valid:
            raise ValueError(f"Path {path} is outside sandboxed directories")
        
        return path
    
    def add_sandbox_path(self, path: Union[str, Path]):
        """Add a new path to the sandbox."""
        path = Path(path).expanduser().resolve()
        if path not in self.sandboxed_paths:
            self.sandboxed_paths.append(path)
    
    def remove_sandbox_path(self, path: Union[str, Path]):
        """Remove a path from the sandbox (except base path)."""
        path = Path(path).expanduser().resolve()
        if path in self.sandboxed_paths and path != self.base_path:
            self.sandboxed_paths.remove(path)
    
    def get_sandbox_paths(self) -> List[str]:
        """Get list of current sandboxed paths."""
        return [str(p) for p in self.sandboxed_paths]
    
    def is_within_sandbox(self, path: Union[str, Path]) -> bool:
        """Check if path is within sandbox without raising error."""
        try:
            self.validate_path(path)
            return True
        except ValueError:
            return False
