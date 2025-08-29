"""
filesystem_core.py - Safe file operations with validation for Bob

This module provides secure, validated file operations with comprehensive
error handling, path sandboxing, and performance monitoring.

Key Features:
- Path security and sandboxing
- Safe read/write operations
- Directory management
- File metadata operations
- Performance monitoring
- Comprehensive error handling
- Async operation support
"""

import os
import json
import shutil
import hashlib
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple
from contextlib import contextmanager
# Optional async support
try:
    import aiofiles
    ASYNC_AVAILABLE = True
except ImportError:
    aiofiles = None
    ASYNC_AVAILABLE = False
import asyncio


class FileSystemCore:
    """
    Safe file system operations with validation and monitoring.
    
    Provides sandboxed file operations with comprehensive error handling,
    validation, and performance tracking. All operations are logged to
    the database for observability.
    """
    
    def __init__(self, db_core=None, base_path: str = None):
        """
        Initialize FileSystemCore with optional database connection.
        
        Args:
            db_core: DatabaseCore instance for logging operations
            base_path: Base directory for sandboxed operations (default: ~/Bob/data)
        """
        self.db_core = db_core
        self.base_path = Path(base_path or os.path.expanduser("~/Bob/data"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance metrics
        self.metrics = {
            "reads": 0,
            "writes": 0,
            "deletes": 0,
            "errors": 0,
            "total_bytes_read": 0,
            "total_bytes_written": 0
        }
        
        # Sandboxed paths - operations restricted to these directories
        self.sandboxed_paths = [
            self.base_path,
            Path(os.path.expanduser("~/Bob")),
        ]
    
    def _validate_path(self, path: Union[str, Path]) -> Path:
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
    
    def _log_operation(self, operation: str, path: str, success: bool, 
                       details: Dict[str, Any] = None):
        """Log file operation to database if available."""
        if self.db_core:
            try:
                self.db_core.track_tool_usage(
                    tool_name="filesystem_core",
                    operation=operation,
                    parameters={"path": str(path), "details": details},
                    success=success,
                    duration_ms=details.get("duration_ms", 0) if details else 0
                )
            except:
                pass  # Don't let logging failures break operations
    
    @contextmanager
    def _atomic_write(self, path: Path):
        """
        Context manager for atomic file writes using temporary files.
        
        Ensures file writes are atomic - either completely succeeds or fails
        without leaving partial data.
        """
        temp_fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp"
        )
        temp_path = Path(temp_path)
        
        try:
            yield temp_path
            # Atomic move on success
            temp_path.replace(path)
        except Exception:
            # Clean up temp file on failure
            try:
                temp_path.unlink()
            except:
                pass
            raise
        finally:
            try:
                os.close(temp_fd)
            except:
                pass
    
    # === READ OPERATIONS ===
    
    def read_file(self, path: Union[str, Path], mode: str = 'text') -> Union[str, bytes]:
        """
        Read file contents with validation and error handling.
        
        Args:
            path: Path to file
            mode: 'text' or 'binary'
            
        Returns:
            File contents as string (text) or bytes (binary)
            
        Raises:
            ValueError: Invalid path or mode
            FileNotFoundError: File doesn't exist
            IOError: Read failure
        """
        start_time = datetime.now()
        
        try:
            path = self._validate_path(path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            
            with self._lock:
                if mode == 'text':
                    content = path.read_text(encoding='utf-8')
                elif mode == 'binary':
                    content = path.read_bytes()
                else:
                    raise ValueError(f"Invalid mode: {mode}")
                
                self.metrics["reads"] += 1
                self.metrics["total_bytes_read"] += len(content)
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_operation("read", str(path), True, {
                "mode": mode,
                "size": len(content),
                "duration_ms": duration_ms
            })
            
            return content
            
        except Exception as e:
            self.metrics["errors"] += 1
            self._log_operation("read", str(path), False, {"error": str(e)})
            raise
    
    def read_json(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read and parse JSON file.
        
        Args:
            path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            json.JSONDecodeError: Invalid JSON
        """
        content = self.read_file(path, mode='text')
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            self._log_operation("read_json", str(path), False, {"error": str(e)})
            raise
    
    # === WRITE OPERATIONS ===
    
    def write_file(self, path: Union[str, Path], content: Union[str, bytes], 
                   mode: str = 'text', atomic: bool = True) -> int:
        """
        Write content to file with atomic operations and validation.
        
        Args:
            path: Path to write to
            content: Content to write
            mode: 'text' or 'binary'
            atomic: Use atomic write (default: True)
            
        Returns:
            Number of bytes written
            
        Raises:
            ValueError: Invalid path or mode
            IOError: Write failure
        """
        start_time = datetime.now()
        
        try:
            path = self._validate_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._lock:
                if atomic:
                    with self._atomic_write(path) as temp_path:
                        if mode == 'text':
                            if isinstance(content, bytes):
                                content = content.decode('utf-8')
                            temp_path.write_text(content, encoding='utf-8')
                        elif mode == 'binary':
                            if isinstance(content, str):
                                content = content.encode('utf-8')
                            temp_path.write_bytes(content)
                        else:
                            raise ValueError(f"Invalid mode: {mode}")
                else:
                    if mode == 'text':
                        if isinstance(content, bytes):
                            content = content.decode('utf-8')
                        path.write_text(content, encoding='utf-8')
                    else:
                        if isinstance(content, str):
                            content = content.encode('utf-8')
                        path.write_bytes(content)
                
                size = len(content)
                self.metrics["writes"] += 1
                self.metrics["total_bytes_written"] += size
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_operation("write", str(path), True, {
                "mode": mode,
                "size": size,
                "atomic": atomic,
                "duration_ms": duration_ms
            })
            
            return size
            
        except Exception as e:
            self.metrics["errors"] += 1
            self._log_operation("write", str(path), False, {"error": str(e)})
            raise
    
    def write_json(self, path: Union[str, Path], data: Any, indent: int = 2) -> int:
        """
        Write data as JSON to file.
        
        Args:
            path: Path to write to
            data: Data to serialize as JSON
            indent: JSON indentation (default: 2)
            
        Returns:
            Number of bytes written
        """
        try:
            content = json.dumps(data, indent=indent, default=str)
            return self.write_file(path, content, mode='text')
        except Exception as e:
            self._log_operation("write_json", str(path), False, {"error": str(e)})
            raise
    
    def append_file(self, path: Union[str, Path], content: str) -> int:
        """
        Append content to existing file.
        
        Args:
            path: Path to file
            content: Content to append
            
        Returns:
            Number of bytes appended
        """
        try:
            path = self._validate_path(path)
            
            with self._lock:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(content)
                
                size = len(content)
                self.metrics["writes"] += 1
                self.metrics["total_bytes_written"] += size
            
            self._log_operation("append", str(path), True, {"size": size})
            return size
            
        except Exception as e:
            self.metrics["errors"] += 1
            self._log_operation("append", str(path), False, {"error": str(e)})
            raise
    
    # === DELETE OPERATIONS ===
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """
        Safely delete a file.
        
        Args:
            path: Path to file to delete
            
        Returns:
            True if file was deleted
            
        Raises:
            FileNotFoundError: File doesn't exist
        """
        try:
            path = self._validate_path(path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            
            with self._lock:
                path.unlink()
                self.metrics["deletes"] += 1
            
            self._log_operation("delete", str(path), True, {})
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            self._log_operation("delete", str(path), False, {"error": str(e)})
            raise
    
    # === DIRECTORY OPERATIONS ===
    
    def create_directory(self, path: Union[str, Path]) -> Path:
        """
        Create directory with all parent directories.
        
        Args:
            path: Directory path to create
            
        Returns:
            Created directory Path
        """
        try:
            path = self._validate_path(path)
            path.mkdir(parents=True, exist_ok=True)
            
            self._log_operation("mkdir", str(path), True, {})
            return path
            
        except Exception as e:
            self._log_operation("mkdir", str(path), False, {"error": str(e)})
            raise
    
    def list_directory(self, path: Union[str, Path], pattern: str = "*",
                      recursive: bool = False) -> List[Path]:
        """
        List directory contents with optional filtering.
        
        Args:
            path: Directory to list
            pattern: Glob pattern for filtering (default: "*")
            recursive: Search recursively (default: False)
            
        Returns:
            List of Path objects matching pattern
        """
        try:
            path = self._validate_path(path)
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            
            if recursive:
                results = list(path.rglob(pattern))
            else:
                results = list(path.glob(pattern))
            
            self._log_operation("list_dir", str(path), True, {
                "pattern": pattern,
                "recursive": recursive,
                "count": len(results)
            })
            
            return results
            
        except Exception as e:
            self._log_operation("list_dir", str(path), False, {"error": str(e)})
            raise
    
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """
        Delete a directory.
        
        Args:
            path: Directory to delete
            recursive: Delete recursively with all contents
            
        Returns:
            True if deleted successfully
        """
        try:
            path = self._validate_path(path)
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            
            with self._lock:
                if recursive:
                    shutil.rmtree(path)
                else:
                    path.rmdir()  # Only works if directory is empty
                
                self.metrics["deletes"] += 1
            
            self._log_operation("delete_dir", str(path), True, {"recursive": recursive})
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            self._log_operation("delete_dir", str(path), False, {"error": str(e)})
            raise
    
    # === UTILITY OPERATIONS ===
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Copy file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination path
            
        Returns:
            Destination Path
        """
        try:
            source = self._validate_path(source)
            destination = self._validate_path(destination)
            
            if not source.is_file():
                raise ValueError(f"Source is not a file: {source}")
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            
            self._log_operation("copy", str(source), True, {"destination": str(destination)})
            return destination
            
        except Exception as e:
            self._log_operation("copy", str(source), False, {"error": str(e)})
            raise
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Move file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination path
            
        Returns:
            Destination Path
        """
        try:
            source = self._validate_path(source)
            destination = self._validate_path(destination)
            
            if not source.exists():
                raise FileNotFoundError(f"Source not found: {source}")
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            
            self._log_operation("move", str(source), True, {"destination": str(destination)})
            return destination
            
        except Exception as e:
            self._log_operation("move", str(source), False, {"error": str(e)})
            raise
    
    def file_exists(self, path: Union[str, Path]) -> bool:
        """Check if file exists within sandbox."""
        try:
            path = self._validate_path(path)
            return path.exists() and path.is_file()
        except ValueError:
            return False
    
    def directory_exists(self, path: Union[str, Path]) -> bool:
        """Check if directory exists within sandbox."""
        try:
            path = self._validate_path(path)
            return path.exists() and path.is_dir()
        except ValueError:
            return False
    
    def get_file_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get detailed file information.
        
        Args:
            path: Path to file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            path = self._validate_path(path)
            
            if not path.exists():
                raise FileNotFoundError(f"Path not found: {path}")
            
            stat = path.stat()
            
            info = {
                "path": str(path),
                "name": path.name,
                "size": stat.st_size,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            }
            
            if path.is_file():
                info["extension"] = path.suffix
                # Calculate file hash for integrity
                with open(path, 'rb') as f:
                    info["md5"] = hashlib.md5(f.read()).hexdigest()
            
            self._log_operation("file_info", str(path), True, info)
            return info
            
        except Exception as e:
            self._log_operation("file_info", str(path), False, {"error": str(e)})
            raise
    
    def get_directory_size(self, path: Union[str, Path]) -> int:
        """
        Calculate total size of directory and its contents.
        
        Args:
            path: Directory path
            
        Returns:
            Total size in bytes
        """
        try:
            path = self._validate_path(path)
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            
            total_size = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
            
            self._log_operation("dir_size", str(path), True, {"size": total_size})
            return total_size
            
        except Exception as e:
            self._log_operation("dir_size", str(path), False, {"error": str(e)})
            raise
    
    # === ASYNC OPERATIONS ===
    
    async def async_read_file(self, path: Union[str, Path], mode: str = 'text') -> Union[str, bytes]:
        """
        Asynchronously read file contents.
        
        Args:
            path: Path to file
            mode: 'text' or 'binary'
            
        Returns:
            File contents
        """
        if not ASYNC_AVAILABLE:
            raise ImportError("aiofiles not installed. Run: pip install aiofiles")
        
        path = self._validate_path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        async with aiofiles.open(path, mode='r' if mode == 'text' else 'rb') as f:
            content = await f.read()
            
        self.metrics["reads"] += 1
        self.metrics["total_bytes_read"] += len(content)
        
        return content
    
    async def async_write_file(self, path: Union[str, Path], content: Union[str, bytes],
                              mode: str = 'text') -> int:
        """
        Asynchronously write content to file.
        
        Args:
            path: Path to write to
            content: Content to write
            mode: 'text' or 'binary'
            
        Returns:
            Number of bytes written
        """
        if not ASYNC_AVAILABLE:
            raise ImportError("aiofiles not installed. Run: pip install aiofiles")
        
        path = self._validate_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, mode='w' if mode == 'text' else 'wb') as f:
            await f.write(content)
        
        size = len(content)
        self.metrics["writes"] += 1
        self.metrics["total_bytes_written"] += size
        
        return size
    
    # === PERFORMANCE METRICS ===
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        with self._lock:
            return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics."""
        with self._lock:
            self.metrics = {
                "reads": 0,
                "writes": 0,
                "deletes": 0,
                "errors": 0,
                "total_bytes_read": 0,
                "total_bytes_written": 0
            }
    
    # === SANDBOX MANAGEMENT ===
    
    def add_sandbox_path(self, path: Union[str, Path]):
        """
        Add a new path to the sandbox.
        
        Args:
            path: Path to add to sandbox
        """
        path = Path(path).expanduser().resolve()
        if path not in self.sandboxed_paths:
            self.sandboxed_paths.append(path)
    
    def remove_sandbox_path(self, path: Union[str, Path]):
        """
        Remove a path from the sandbox.
        
        Args:
            path: Path to remove from sandbox
        """
        path = Path(path).expanduser().resolve()
        if path in self.sandboxed_paths and path != self.base_path:
            self.sandboxed_paths.remove(path)
    
    def get_sandbox_paths(self) -> List[str]:
        """Get list of current sandboxed paths."""
        return [str(p) for p in self.sandboxed_paths]


# === CONVENIENCE FUNCTIONS ===

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
