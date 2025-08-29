"""
assembly/__init__.py - Clean exports for context assembly submodules

Provides clean access to all context assembly components
following the established modular pattern.
"""

from .source_manager import SourceManager, ContextSource, SourceType, SourceStatus
from .prioritizer import ContextPrioritizer, ContextItem
from .formatter import ContextFormatter, FormatType, FormattedSection, TokenEstimator
from .cache_manager import CacheManager, CacheStrategy, CacheEntry
from .graph_builder import GraphContextBuilder, GraphNode, GraphEdge, RelationshipType, TraversalStrategy
from .metrics import AssemblyMetrics, MetricEvent, MetricType

__all__ = [
    # Source Management
    'SourceManager',
    'ContextSource', 
    'SourceType',
    'SourceStatus',
    
    # Prioritization
    'ContextPrioritizer',
    'ContextItem',
    
    # Formatting
    'ContextFormatter',
    'FormatType',
    'FormattedSection',
    'TokenEstimator',
    
    # Caching
    'CacheManager',
    'CacheStrategy',
    'CacheEntry',
    
    # Graph Building
    'GraphContextBuilder',
    'GraphNode',
    'GraphEdge',
    'RelationshipType',
    'TraversalStrategy',
    
    # Metrics
    'AssemblyMetrics',
    'MetricEvent',
    'MetricType'
]
