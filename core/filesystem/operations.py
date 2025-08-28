"""
operations.py - Core file operations for FileSystemCore

Handles all synchronous file and directory operations.
"""

import os
import json
import shutil
import hashlib
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Union
from contextlib import contextmanager

from .validation import PathValidator
from .metrics import MetricsTracker


class FileOperations:
    """Handles core file system operations."""
    
    def __init__(self, validator: PathValidator, metrics: MetricsTracker, db_core=None):
        """
        Initialize file operations handler.
        
        Args:
            validator: Path validator instance
            metrics: Metrics tracker instance
            db_core: Optional database core for logging
        """
        self.validator = validator
        self.metrics = metrics
        self.db_core = db_core
        self._lock = threading.RLock()
    
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
        """Context manager for atomic file writes."""
        temp_fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp"
        )
        temp_path = Path(temp_path)
        
        try:
            yield temp_path
            temp_path.replace(path)
        except Exception:
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
        """Read file contents with validation and error handling."""
        start_time = datetime.now()
        
        try:
            path = self.validator.validate_path(path)
            
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
                
                self.metrics.record_read(len(content))
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_operation("read", str(path), True, {
                "mode": mode,
                "size": len(content),
                "duration_ms": duration_ms
            })
            
            return content
            
        except Exception as e:
            self.metrics.record_error()
            self._log_operation("read", str(path), False, {"error": str(e)})
            raise
    
    def read_json(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Read and parse JSON file."""
        content = self.read_file(path, mode='text')
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            self._log_operation("read_json", str(path), False, {"error": str(e)})
            raise
    
    # === WRITE OPERATIONS ===
    
    def write_file(self, path: Union[str, Path], content: Union[str, bytes], 
                   mode: str = 'text', atomic: bool = True) -> int:
        """Write content to file with atomic operations and validation."""
        start_time = datetime.now()
        
        try:
            path = self.validator.validate_path(path)
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
                self.metrics.record_write(size)
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_operation("write", str(path), True, {
                "mode": mode,
                "size": size,
                "atomic": atomic,
                "duration_ms": duration_ms
            })
            
            return size
            
        except Exception as e:
            self.metrics.record_error()
            self._log_operation("write", str(path), False, {"error": str(e)})
            raise
    
    def write_json(self, path: Union[str, Path], data: Any, indent: int = 2) -> int:
        """Write data as JSON to file."""
        try:
            content = json.dumps(data, indent=indent, default=str)
            return self.write_file(path, content, mode='text')
        except Exception as e:
            self._log_operation("write_json", str(path), False, {"error": str(e)})
            raise
    
    def append_file(self, path: Union[str, Path], content: str) -> int:
        """Append content to existing file."""
        try:
            path = self.validator.validate_path(path)
            
            with self._lock:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(content)
                
                size = len(content)
                self.metrics.record_write(size)
            
            self._log_operation("append", str(path), True, {"size": size})
            return size
            
        except Exception as e:
            self.metrics.record_error()
            self._log_operation("append", str(path), False, {"error": str(e)})
            raise
    
    # === DELETE OPERATIONS ===
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """Safely delete a file."""
        try:
            path = self.validator.validate_path(path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            
            with self._lock:
                path.unlink()
                self.metrics.record_delete()
            
            self._log_operation("delete", str(path), True, {})
            return True
            
        except Exception as e:
            self.metrics.record_error()
            self._log_operation("delete", str(path), False, {"error": str(e)})
            raise
    
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """Delete a directory."""
        try:
            path = self.validator.validate_path(path)
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            
            with self._lock:
                if recursive:
                    shutil.rmtree(path)
                else:
                    path.rmdir()  # Only works if directory is empty
                
                self.metrics.record_delete()
            
            self._log_operation("delete_dir", str(path), True, {"recursive": recursive})
            return True
            
        except Exception as e:
            self.metrics.record_error()
            self._log_operation("delete_dir", str(path), False, {"error": str(e)})
            raise
    
    # === DIRECTORY OPERATIONS ===
    
    def create_directory(self, path: Union[str, Path]) -> Path:
        """Create directory with all parent directories."""
        try:
            path = self.validator.validate_path(path)
            path.mkdir(parents=True, exist_ok=True)
            
            self._log_operation("mkdir", str(path), True, {})
            return path
            
        except Exception as e:
            self._log_operation("mkdir", str(path), False, {"error": str(e)})
            raise
    
    def list_directory(self, path: Union[str, Path], pattern: str = "*",
                      recursive: bool = False) -> List[Path]:
        """List directory contents with optional filtering."""
        try:
            path = self.validator.validate_path(path)
            
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
    
    # === UTILITY OPERATIONS ===
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """Copy file from source to destination."""
        try:
            source = self.validator.validate_path(source)
            destination = self.validator.validate_path(destination)
            
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
        """Move file from source to destination."""
        try:
            source = self.validator.validate_path(source)
            destination = self.validator.validate_path(destination)
            
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
            path = self.validator.validate_path(path)
            return path.exists() and path.is_file()
        except ValueError:
            return False
    
    def directory_exists(self, path: Union[str, Path]) -> bool:
        """Check if directory exists within sandbox."""
        try:
            path = self.validator.validate_path(path)
            return path.exists() and path.is_dir()
        except ValueError:
            return False
    
    def get_file_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get detailed file information."""
        try:
            path = self.validator.validate_path(path)
            
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
        """Calculate total size of directory and its contents."""
        try:
            path = self.validator.validate_path(path)
            
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
