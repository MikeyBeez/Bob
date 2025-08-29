"""
metrics.py - Track metrics and statistics for Ollama usage
"""

from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict
import time


class OllamaMetrics:
    """Track metrics for Ollama API usage."""
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.request_count = 0
        self.total_tokens = 0
        self.total_duration_ms = 0
        self.errors = []
        self.model_usage = defaultdict(int)
        self.start_time = datetime.now()
        
        # Per-request tracking
        self.request_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    def track_request(self, model: str, prompt: str):
        """
        Track an outgoing request.
        
        Args:
            model: Model being used
            prompt: Input prompt
        """
        self.request_count += 1
        self.model_usage[model] += 1
        
        # Store request details
        request_info = {
            "timestamp": datetime.now(),
            "model": model,
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt
        }
        
        self._add_to_history(request_info)
        
        return request_info
    
    def track_response(self, model: str, duration_ns: int, token_count: int):
        """
        Track a response from Ollama.
        
        Args:
            model: Model that generated response
            duration_ns: Response time in nanoseconds
            token_count: Number of tokens generated
        """
        duration_ms = duration_ns / 1_000_000  # Convert to milliseconds
        
        self.total_duration_ms += duration_ms
        self.total_tokens += token_count
        
        # Calculate tokens per second
        if duration_ms > 0:
            tokens_per_second = (token_count / duration_ms) * 1000
        else:
            tokens_per_second = 0
        
        # Update last request in history
        if self.request_history:
            self.request_history[-1].update({
                "duration_ms": duration_ms,
                "tokens": token_count,
                "tokens_per_second": tokens_per_second
            })
    
    def track_chat(self, model: str, message_count: int):
        """
        Track a chat interaction.
        
        Args:
            model: Model being used
            message_count: Number of messages in conversation
        """
        self.track_request(model, f"[Chat with {message_count} messages]")
    
    def track_error(self, error: Exception, context: Dict[str, Any]):
        """
        Track an error occurrence.
        
        Args:
            error: Exception that occurred
            context: Context information about the error
        """
        error_info = {
            "timestamp": datetime.now(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        self.errors.append(error_info)
        
        # Limit error history
        if len(self.errors) > 50:
            self.errors = self.errors[-50:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.
        
        Returns:
            Dictionary of metrics and statistics
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate averages
        avg_duration = (self.total_duration_ms / self.request_count) if self.request_count > 0 else 0
        avg_tokens = (self.total_tokens / self.request_count) if self.request_count > 0 else 0
        
        # Calculate throughput
        if self.total_duration_ms > 0:
            overall_tokens_per_second = (self.total_tokens / self.total_duration_ms) * 1000
        else:
            overall_tokens_per_second = 0
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens,
            "total_duration_ms": self.total_duration_ms,
            "average_duration_ms": avg_duration,
            "average_tokens": avg_tokens,
            "tokens_per_second": overall_tokens_per_second,
            "model_usage": dict(self.model_usage),
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else [],
            "requests_per_minute": (self.request_count / uptime) * 60 if uptime > 0 else 0
        }
    
    def get_model_stats(self, model: str) -> Dict[str, Any]:
        """
        Get statistics for a specific model.
        
        Args:
            model: Model name
            
        Returns:
            Model-specific statistics
        """
        model_requests = [r for r in self.request_history if r.get("model") == model]
        
        if not model_requests:
            return {
                "model": model,
                "request_count": 0,
                "total_tokens": 0,
                "average_duration_ms": 0,
                "average_tokens": 0
            }
        
        total_duration = sum(r.get("duration_ms", 0) for r in model_requests)
        total_tokens = sum(r.get("tokens", 0) for r in model_requests)
        
        return {
            "model": model,
            "request_count": len(model_requests),
            "total_tokens": total_tokens,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / len(model_requests),
            "average_tokens": total_tokens / len(model_requests),
            "tokens_per_second": (total_tokens / total_duration) * 1000 if total_duration > 0 else 0
        }
    
    def reset(self):
        """Reset all metrics."""
        self.__init__()
    
    def _add_to_history(self, info: Dict[str, Any]):
        """Add request to history with size limit."""
        self.request_history.append(info)
        
        # Maintain size limit
        if len(self.request_history) > self.max_history:
            self.request_history = self.request_history[-self.max_history:]
