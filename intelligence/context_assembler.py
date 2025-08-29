"""
context_assembler.py - Clean API for intelligent context assembly

This is the main API module for Bob's context assembly system.
It gathers, prioritizes, and structures context from multiple sources
for optimal LLM consumption. Implementation details are in submodules.
Following the modular pattern established in Phase 1.

API DOCUMENTATION:
==================
Main Methods:
- assemble_context(query, sources=None, max_tokens=None) -> dict
  Primary entry point for context assembly

Context Sources:
- add_context_source(source_type, source_config) -> bool
  Add new context sources dynamically

Caching:
- clear_context_cache(max_age_seconds=None) -> int
  Clear cached context data

Configuration:
- set_context_priorities(priority_config) -> bool
  Configure context source priorities

Metrics:
- get_context_metrics() -> dict
  Get performance and usage metrics
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import json
import asyncio
import uuid

# Import implementation modules
from .assembly import (
    SourceManager, ContextSource, SourceType, SourceStatus,
    ContextPrioritizer, ContextItem,
    ContextFormatter, FormatType, FormattedSection,
    CacheManager, CacheStrategy,
    GraphContextBuilder, TraversalStrategy,
    AssemblyMetrics, MetricType
)


class ContextAssembler:
    """
    Clean API for intelligent context assembly.
    
    Assembles relevant context from multiple sources (database, files, memories)
    and structures it optimally for LLM processing. This is the core of Bob's
    intelligence loop - providing the right context at the right time.
    
    Usage Example:
    --------------
    assembler = ContextAssembler(db_core=db, fs_core=fs)
    assembler.add_context_source('database', {'priority': 0.8})
    
    result = await assembler.assemble_context(
        "How do I implement user authentication?",
        max_tokens=8000
    )
    
    formatted_context = result['formatted_context']
    metadata = result['metadata']
    """
    
    def __init__(self,
                 db_core: Optional[Any] = None,
                 fs_core: Optional[Any] = None,
                 max_context_size: int = 128000,  # Token limit
                 cache_ttl: int = 300):  # Cache TTL in seconds
        """
        Initialize ContextAssembler with configuration.
        
        Args:
            db_core: DatabaseCore instance for accessing stored data
            fs_core: FileSystemCore instance for file operations
            max_context_size: Maximum context size in tokens
            cache_ttl: Cache time-to-live in seconds
        """
        # Store core dependencies
        self.db_core = db_core
        self.fs_core = fs_core
        self.max_context_size = max_context_size
        self.cache_ttl = cache_ttl
        
        # Initialize submodules
        self.source_manager = SourceManager()
        self.prioritizer = ContextPrioritizer({
            'max_context_tokens': max_context_size
        })
        self.formatter = ContextFormatter({
            'max_total_tokens': max_context_size
        })
        self.cache_manager = CacheManager({
            'default_ttl_seconds': cache_ttl
        })
        self.graph_builder = GraphContextBuilder()
        self.metrics = AssemblyMetrics()
        
        # Configuration
        self.config = {
            'enable_caching': True,
            'enable_graph_traversal': True,
            'default_format_type': FormatType.STRUCTURED_PROMPT,
            'source_priorities': {}
        }
        
        # Register default sources if cores provided
        self._register_default_sources()
        
        # Start metrics session
        self.session_id = str(uuid.uuid4())
        self.metrics.start_session(self.session_id)
    
    async def assemble_context(self, 
                              query: str, 
                              sources: Optional[List[str]] = None,
                              max_tokens: Optional[int] = None,
                              format_type: FormatType = FormatType.STRUCTURED_PROMPT,
                              enable_graph_expansion: bool = True) -> Dict[str, Any]:
        """
        Primary API method for context assembly.
        
        Args:
            query: Query to find relevant context for
            sources: Specific sources to use (None = use all)
            max_tokens: Override default token limit
            format_type: Output format type
            enable_graph_expansion: Whether to use graph traversal
            
        Returns:
            Dict containing formatted context and metadata
        """
        start_time = datetime.now()
        max_tokens = max_tokens or self.max_context_size
        
        try:
            # Check cache first
            cache_key = None
            if self.config['enable_caching']:
                cache_config = {
                    'sources': sources,
                    'max_tokens': max_tokens,
                    'format_type': format_type.value,
                    'graph_expansion': enable_graph_expansion
                }
                cache_key = self.cache_manager.generate_key(query, cache_config)
                cached_result = self.cache_manager.get(cache_key)
                
                if cached_result:
                    self.metrics.record_performance_metric('cache_hit', 1.0)
                    return cached_result
            
            self.metrics.record_performance_metric('cache_miss', 1.0)
            
            # Step 1: Fetch raw context from sources
            raw_context = await self._fetch_raw_context(query, sources)
            
            # Step 2: Prioritize and score context items
            prioritized_items = self.prioritizer.prioritize_context(
                raw_context,
                query,
                source_priorities=self.config.get('source_priorities', {}),
                max_items=None  # Let formatter handle token limits
            )
            
            # Step 3: Expand context using graph relationships (if enabled)
            if enable_graph_expansion and self.config['enable_graph_traversal']:
                expanded_items = await self._expand_context_via_graph(
                    prioritized_items, query
                )
                prioritized_items.extend(expanded_items)
            
            # Step 4: Format context for LLM consumption
            format_result = self.formatter.format_context(
                prioritized_items,
                format_type=format_type,
                max_tokens=max_tokens
            )
            
            # Step 5: Build final result
            result = {
                'formatted_context': format_result['formatted_context'],
                'metadata': {
                    **format_result['metadata'],
                    'query': query,
                    'assembly_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'sources_used': format_result['metadata'].get('sources_included', []),
                    'graph_expansion_enabled': enable_graph_expansion,
                    'cache_key': cache_key,
                    'session_id': self.session_id
                },
                'sections': format_result.get('sections', []),
                'raw_items_count': len(raw_context),
                'prioritized_items_count': len(prioritized_items)
            }
            
            # Step 6: Cache result if caching enabled
            if self.config['enable_caching'] and cache_key:
                self.cache_manager.put(
                    cache_key,
                    result,
                    ttl_seconds=self.cache_ttl,
                    tags={'query_hash', 'context_assembly'}
                )
            
            # Record metrics
            processing_time = result['metadata']['assembly_time_ms']
            self.metrics.record_performance_metric('assembly_time_ms', processing_time)
            self.metrics.record_performance_metric('items_processed', len(raw_context))
            self.metrics.record_quality_metric('final_token_count', result['metadata']['total_tokens'])
            
            return result
            
        except Exception as e:
            # Record error metrics
            self.metrics.record_performance_metric('assembly_errors', 1.0, {
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            
            # Return error result
            return {
                'formatted_context': f"Error assembling context: {str(e)}",
                'metadata': {
                    'error': True,
                    'error_message': str(e),
                    'query': query,
                    'session_id': self.session_id
                },
                'sections': [],
                'raw_items_count': 0,
                'prioritized_items_count': 0
            }
    
    def add_context_source(self, source_type: str, source_config: Dict[str, Any]) -> bool:
        """
        Add a new context source dynamically.
        
        Args:
            source_type: Type of source ('database', 'filesystem', etc.)
            source_config: Configuration for the source
            
        Returns:
            True if source was added successfully
        """
        try:
            # Convert string to SourceType enum
            if source_type.lower() == 'database':
                enum_type = SourceType.DATABASE
            elif source_type.lower() == 'filesystem':
                enum_type = SourceType.FILESYSTEM
            elif source_type.lower() == 'memory':
                enum_type = SourceType.MEMORY
            elif source_type.lower() == 'external_api':
                enum_type = SourceType.EXTERNAL_API
            elif source_type.lower() == 'cache':
                enum_type = SourceType.CACHE
            else:
                return False
            
            # Generate unique source ID
            source_id = f"{source_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Register with source manager
            success = self.source_manager.register_source(
                source_id,
                enum_type,
                source_config
            )
            
            if success:
                self.metrics.record_usage_metric('sources_added', 1.0, {
                    'source_type': source_type,
                    'source_id': source_id
                })
            
            return success
            
        except Exception:
            return False
    
    def clear_context_cache(self, max_age_seconds: Optional[int] = None) -> int:
        """
        Clear cached context data.
        
        Args:
            max_age_seconds: Clear entries older than this (None = clear all)
            
        Returns:
            Number of cache entries cleared
        """
        if max_age_seconds:
            # Clear expired entries
            count = self.cache_manager.invalidate_expired()
        else:
            # Clear all cache entries
            count = self.cache_manager.clear()
        
        self.metrics.record_usage_metric('cache_cleared', count)
        return count
    
    def set_context_priorities(self, priority_config: Dict[str, float]) -> bool:
        """
        Configure context source priorities.
        
        Args:
            priority_config: Dict mapping source types/IDs to priority values (0.0-1.0)
            
        Returns:
            True if priorities were set successfully
        """
        try:
            # Update internal priority configuration
            self.config['source_priorities'].update(priority_config)
            
            # Update individual source priorities
            for source_id, priority in priority_config.items():
                self.source_manager.set_source_priority(source_id, priority)
            
            # Update prioritizer weights if applicable
            if 'query_relevance' in priority_config:
                self.prioritizer.update_weights({
                    'query_relevance': priority_config['query_relevance']
                })
            
            self.metrics.record_usage_metric('priorities_updated', len(priority_config))
            return True
            
        except Exception:
            return False
    
    def get_context_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance and usage metrics.
        
        Returns:
            Dict containing metrics from all submodules
        """
        # Collect metrics from all submodules
        source_metrics = self.source_manager.get_metrics()
        cache_metrics = self.cache_manager.get_metrics()
        formatter_metrics = self.formatter.get_metrics()
        prioritizer_metrics = self.prioritizer.get_metrics()
        graph_metrics = self.graph_builder.get_metrics()
        assembly_metrics = self.metrics.get_metrics()
        
        # Get performance summaries
        perf_summary = self.metrics.get_performance_summary(time_window_hours=24)
        quality_trends = self.metrics.get_quality_trends(time_window_hours=24)
        usage_analytics = self.metrics.get_usage_analytics(time_window_hours=24)
        
        return {
            'session_id': self.session_id,
            'configuration': {
                'max_context_size': self.max_context_size,
                'cache_ttl': self.cache_ttl,
                'enable_caching': self.config['enable_caching'],
                'enable_graph_traversal': self.config['enable_graph_traversal']
            },
            'submodule_metrics': {
                'source_manager': source_metrics,
                'cache_manager': cache_metrics,
                'formatter': formatter_metrics,
                'prioritizer': prioritizer_metrics,
                'graph_builder': graph_metrics,
                'assembly_metrics': assembly_metrics
            },
            'performance_summary': perf_summary,
            'quality_trends': quality_trends,
            'usage_analytics': usage_analytics,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _fetch_raw_context(self, query: str, source_filter: Optional[List[str]] = None) -> List[Any]:
        """Fetch raw context from all configured sources."""
        # Get context from source manager
        source_results = await self.source_manager.fetch_from_sources(
            query,
            source_ids=source_filter,
            max_items_per_source=100
        )
        
        # Flatten results
        raw_context = []
        for source_id, items in source_results.items():
            for item in items:
                # Add source metadata
                if hasattr(item, '__dict__'):
                    item.source_id = source_id
                elif isinstance(item, dict):
                    item['source_id'] = source_id
                raw_context.append(item)
        
        # Add database context if available and requested
        should_fetch_db = (
            self.db_core and 
            (source_filter is None or 
             any('database' in src.lower() for src in source_filter))
        )
        
        if should_fetch_db:
            try:
                db_memories = await self._fetch_database_context(query)
                raw_context.extend(db_memories)
            except Exception as e:
                self.metrics.record_performance_metric('db_fetch_errors', 1.0, {
                    'error': str(e)
                })
        
        # Add filesystem context if available and requested
        should_fetch_fs = (
            self.fs_core and 
            (source_filter is None or 
             any('filesystem' in src.lower() or 'file' in src.lower() for src in source_filter))
        )
        
        if should_fetch_fs:
            try:
                fs_context = await self._fetch_filesystem_context(query)
                raw_context.extend(fs_context)
            except Exception as e:
                self.metrics.record_performance_metric('fs_fetch_errors', 1.0, {
                    'error': str(e)
                })
        
        return raw_context
    
    async def _fetch_database_context(self, query: str) -> List[Any]:
        """Fetch context from database core."""
        if not self.db_core or not hasattr(self.db_core, 'search_memories'):
            return []
            
        try:
            # Use the database core to search for memories
            memories = await self.db_core.search_memories(query)
            
            # Convert to ContextItem objects
            from .assembly import ContextItem
            context_items = []
            
            for memory in memories:
                item = ContextItem(
                    content=memory.get('content', ''),
                    source_id='database_memory',
                    item_type='memory'
                )
                item.relevance_score = memory.get('relevance', 0.5)
                context_items.append(item)
            
            return context_items
            
        except Exception as e:
            # Log error but don't fail
            self.metrics.record_performance_metric('db_fetch_errors', 1.0, {
                'error': str(e)
            })
            return []
    
    async def _fetch_filesystem_context(self, query: str) -> List[Any]:
        """Fetch context from filesystem core."""
        if not self.fs_core or not hasattr(self.fs_core, 'search_files'):
            return []
            
        try:
            # Use the filesystem core to search files
            files = await self.fs_core.search_files(query)
            
            # Convert to ContextItem objects
            from .assembly import ContextItem
            context_items = []
            
            for file_info in files:
                item = ContextItem(
                    content=file_info.get('content', ''),
                    source_id='filesystem_file',
                    item_type='file'
                )
                item.file_path = file_info.get('path', '')
                item.relevance_score = 0.6  # Default relevance for file content
                context_items.append(item)
            
            return context_items
            
        except Exception as e:
            # Log error but don't fail
            self.metrics.record_performance_metric('fs_fetch_errors', 1.0, {
                'error': str(e)
            })
            return []
    
    async def _expand_context_via_graph(self, prioritized_items: List[ContextItem], query: str) -> List[ContextItem]:
        """Expand context using graph relationships."""
        try:
            # Build graph from seed nodes (top prioritized items)
            seed_nodes = [item.content for item in prioritized_items[:5]]  # Top 5 as seeds
            
            graph_result = self.graph_builder.build_context_graph(
                seed_nodes,
                relationship_source=self.db_core  # Use database as relationship source
            )
            
            # Convert graph nodes back to ContextItem objects
            expanded_items = []
            for node_id, graph_node in graph_result['nodes'].items():
                if graph_node.relevance_score >= 0.3:  # Threshold for inclusion
                    context_item = ContextItem(
                        graph_node.content,
                        'graph_expansion',
                        'graph_node'
                    )
                    context_item.final_score = graph_node.relevance_score
                    expanded_items.append(context_item)
            
            self.metrics.record_graph_metrics({
                'nodes_discovered': len(graph_result['nodes']),
                'edges_traversed': len(graph_result['edges'])
            })
            
            return expanded_items
            
        except Exception as e:
            self.metrics.record_performance_metric('graph_expansion_errors', 1.0, {
                'error': str(e)
            })
            return []
    
    def _register_default_sources(self):
        """Register default sources based on available cores."""
        if self.db_core:
            self.source_manager.register_source(
                'default_database',
                SourceType.DATABASE,
                {'priority': 0.8, 'enabled': True}
            )
        
        if self.fs_core:
            self.source_manager.register_source(
                'default_filesystem', 
                SourceType.FILESYSTEM,
                {'priority': 0.6, 'enabled': True}
            )
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            # End metrics session
            if hasattr(self, 'metrics') and hasattr(self, 'session_id'):
                self.metrics.end_session()
        except:
            pass  # Ignore errors during cleanup
