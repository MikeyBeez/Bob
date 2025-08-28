"""
metrics.py - Performance metrics tracking for FileSystemCore

Tracks operation counts, data transfer, and errors.
"""

import threading
from typing import Dict, Any


class MetricsTracker:
    """Tracks file system operation metrics."""
    
    def __init__(self):
        """Initialize metrics tracking."""
        self._lock = threading.RLock()
        self.reset()
    
    def reset(self):
        """Reset all metrics to zero."""
        with self._lock:
            self.metrics = {
                "reads": 0,
                "writes": 0,
                "deletes": 0,
                "errors": 0,
                "total_bytes_read": 0,
                "total_bytes_written": 0
            }
    
    def record_read(self, bytes_read: int):
        """Record a read operation."""
        with self._lock:
            self.metrics["reads"] += 1
            self.metrics["total_bytes_read"] += bytes_read
    
    def record_write(self, bytes_written: int):
        """Record a write operation."""
        with self._lock:
            self.metrics["writes"] += 1
            self.metrics["total_bytes_written"] += bytes_written
    
    def record_delete(self):
        """Record a delete operation."""
        with self._lock:
            self.metrics["deletes"] += 1
    
    def record_error(self):
        """Record an error."""
        with self._lock:
            self.metrics["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            return self.metrics.copy()
