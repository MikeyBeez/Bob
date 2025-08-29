"""
source_manager.py - Context source management module

Handles registration, configuration, and management of different
context sources (database, filesystem, external APIs).
Clean API that hides implementation complexity.
"""

from typing import Any, Dict, List, Optional, Set
from enum import Enum
from datetime import datetime
import asyncio


class SourceType(Enum):
    """Supported context source types."""
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    MEMORY = "memory"
    EXTERNAL_API = "external_api"
    CACHE = "cache"


class SourceStatus(Enum):
    """Source availability status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNKNOWN = "unknown"


class ContextSource:
    """
    Represents a single context source with its configuration.
    
    Clean abstraction that handles source-specific details
    while providing a uniform interface.
    """
    
    def __init__(self, source_id: str, source_type: SourceType, config: Dict[str, Any]):
        self.source_id = source_id
        self.source_type = source_type
        self.config = config
        self.status = SourceStatus.UNKNOWN
        self.last_accessed = None
        self.priority = config.get('priority', 0.5)  # 0.0-1.0
        self.weight = config.get('weight', 1.0)
        self.enabled = config.get('enabled', True)
    
    async def test_connection(self) -> bool:
        """Test if source is accessible."""
        try:
            # Implementation would test actual connectivity
            self.status = SourceStatus.ACTIVE
            return True
        except Exception:
            self.status = SourceStatus.ERROR
            return False
    
    async def fetch_context(self, query: str, max_items: int = 100) -> List[Dict[str, Any]]:
        """Fetch context from this source."""
        # This would be implemented per source type
        self.last_accessed = datetime.now()
        return []


class SourceManager:
    """
    Manages multiple context sources and their lifecycle.
    
    Public API for registering, configuring, and accessing
    context sources. Handles load balancing and fallbacks.
    """
    
    def __init__(self):
        self.sources: Dict[str, ContextSource] = {}
        self.source_groups: Dict[str, Set[str]] = {}
        self._metrics = {
            'sources_registered': 0,
            'sources_active': 0,
            'total_requests': 0,
            'failed_requests': 0
        }
    
    def register_source(self, source_id: str, source_type: SourceType, 
                       config: Dict[str, Any]) -> bool:
        """
        Register a new context source.
        
        Args:
            source_id: Unique identifier for the source
            source_type: Type of source (database, filesystem, etc.)
            config: Source-specific configuration
            
        Returns:
            True if source registered successfully
        """
        try:
            source = ContextSource(source_id, source_type, config)
            self.sources[source_id] = source
            self._metrics['sources_registered'] += 1
            return True
        except Exception:
            return False
    
    def unregister_source(self, source_id: str) -> bool:
        """Remove a source from management."""
        if source_id in self.sources:
            del self.sources[source_id]
            # Remove from groups
            for group_sources in self.source_groups.values():
                group_sources.discard(source_id)
            return True
        return False
    
    def get_source(self, source_id: str) -> Optional[ContextSource]:
        """Get source by ID."""
        return self.sources.get(source_id)
    
    def list_sources(self, source_type: Optional[SourceType] = None,
                    status: Optional[SourceStatus] = None) -> List[ContextSource]:
        """List sources with optional filtering."""
        sources = list(self.sources.values())
        
        if source_type:
            sources = [s for s in sources if s.source_type == source_type]
        
        if status:
            sources = [s for s in sources if s.status == status]
        
        return sources
    
    def create_source_group(self, group_name: str, source_ids: List[str]) -> bool:
        """Create a named group of sources for bulk operations."""
        valid_sources = [sid for sid in source_ids if sid in self.sources]
        if valid_sources:
            self.source_groups[group_name] = set(valid_sources)
            return True
        return False
    
    async def test_all_sources(self) -> Dict[str, bool]:
        """Test connectivity to all sources."""
        results = {}
        tasks = []
        
        for source_id, source in self.sources.items():
            task = asyncio.create_task(source.test_connection())
            tasks.append((source_id, task))
        
        for source_id, task in tasks:
            try:
                results[source_id] = await task
            except Exception:
                results[source_id] = False
        
        # Update metrics
        self._metrics['sources_active'] = sum(results.values())
        
        return results
    
    async def fetch_from_sources(self, query: str, source_ids: Optional[List[str]] = None,
                                max_items_per_source: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch context from multiple sources in parallel.
        
        Args:
            query: Search query
            source_ids: Specific sources to query (None = all active)
            max_items_per_source: Max items per source
            
        Returns:
            Dict mapping source_id to list of context items
        """
        if source_ids is None:
            sources_to_query = [s for s in self.sources.values() 
                               if s.enabled and s.status == SourceStatus.ACTIVE]
        else:
            sources_to_query = [self.sources[sid] for sid in source_ids 
                               if sid in self.sources]
        
        results = {}
        tasks = []
        
        self._metrics['total_requests'] += 1
        
        for source in sources_to_query:
            task = asyncio.create_task(
                source.fetch_context(query, max_items_per_source)
            )
            tasks.append((source.source_id, task))
        
        for source_id, task in tasks:
            try:
                results[source_id] = await task
            except Exception:
                results[source_id] = []
                self._metrics['failed_requests'] += 1
        
        return results
    
    def set_source_priority(self, source_id: str, priority: float) -> bool:
        """Set source priority (0.0-1.0, higher = more important)."""
        if source_id in self.sources:
            self.sources[source_id].priority = max(0.0, min(1.0, priority))
            return True
        return False
    
    def enable_source(self, source_id: str) -> bool:
        """Enable a source for queries."""
        if source_id in self.sources:
            self.sources[source_id].enabled = True
            return True
        return False
    
    def disable_source(self, source_id: str) -> bool:
        """Disable a source from queries."""
        if source_id in self.sources:
            self.sources[source_id].enabled = False
            return True
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get source management metrics."""
        active_sources = len([s for s in self.sources.values() 
                             if s.status == SourceStatus.ACTIVE])
        
        return {
            **self._metrics,
            'sources_active': active_sources,
            'total_sources': len(self.sources),
            'source_types': {st.value: len([s for s in self.sources.values() 
                                          if s.source_type == st]) 
                            for st in SourceType},
            'source_groups': len(self.source_groups)
        }
