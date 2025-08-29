"""
memory_integrator.py - Integration with memory systems for reflection storage and retrieval

This module handles the storage and retrieval of reflections, patterns, and insights
in various memory systems. It provides unified access to both short-term working
memory and long-term persistent memory.
"""

from typing import Any, Dict, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from collections import defaultdict

# Import types from parent module
from .. import Reflection

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory storage."""
    WORKING = "working"  # Short-term, volatile memory
    EPISODIC = "episodic"  # Specific event memories
    SEMANTIC = "semantic"  # General knowledge and patterns
    PROCEDURAL = "procedural"  # How-to knowledge and skills


class StorageBackend(Enum):
    """Available storage backends."""
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MEMORY_SYSTEM = "memory_system"
    HYBRID = "hybrid"


@dataclass
class MemoryEntry:
    """Represents an entry in memory storage."""
    id: str
    content: Dict[str, Any]
    memory_type: MemoryType
    timestamp: datetime
    access_count: int
    relevance_score: float
    tags: List[str]
    source: str
    expiry_date: Optional[datetime] = None


@dataclass
class RetrievalQuery:
    """Query for memory retrieval."""
    query_text: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    tags: Optional[List[str]] = None
    time_range: Optional[Tuple[datetime, datetime]] = None
    relevance_threshold: float = 0.5
    max_results: int = 10


class MemoryIntegrator:
    """
    Integrates reflection system with various memory backends.
    
    This class provides unified access to different memory systems for storing
    and retrieving reflections, patterns, insights, and learning data. It handles
    the complexity of different storage backends and provides intelligent retrieval.
    """
    
    def __init__(self, memory_system: Optional[Any] = None):
        """
        Initialize MemoryIntegrator.
        
        Args:
            memory_system: External memory system for persistent storage
        """
        self.memory_system = memory_system
        self._working_memory = {}  # In-memory cache for fast access
        self._memory_metrics = {
            "total_stored": 0,
            "total_retrieved": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "storage_backends_used": [],
            "last_updated": datetime.now()
        }
        
        # Memory management parameters
        self._working_memory_limit = 1000  # Max items in working memory
        self._default_expiry_days = 90  # Default expiry for memories
        
        # Initialize storage backends
        self._available_backends = self._detect_available_backends()
        
    # ==========================================================================
    # CORE MEMORY OPERATIONS
    # ==========================================================================
    
    def store_reflection(self, reflection: Reflection) -> bool:
        """Store reflection in long-term memory with proper indexing."""
        try:
            # Convert reflection to memory entry
            memory_entry = self._reflection_to_memory_entry(reflection)
            
            # Store in hybrid backend (working + persistent)
            success = self._store_in_hybrid(memory_entry)
            
            if success:
                self._update_storage_metrics(True, StorageBackend.HYBRID)
                
            logger.info(f"Stored reflection {reflection.id}")
            return success
            
        except Exception as e:
            logger.error(f"Error storing reflection: {str(e)}")
            return False
    
    def retrieve_relevant_reflections(self,
                                    context: Dict[str, Any],
                                    max_results: int = 10,
                                    min_relevance: float = 0.5) -> List[Reflection]:
        """Get relevant past reflections for current situation."""
        try:
            # Create retrieval query
            query = RetrievalQuery(
                query_text=self._context_to_query_text(context),
                memory_type=MemoryType.EPISODIC,
                relevance_threshold=min_relevance,
                max_results=max_results
            )
            
            # Search in working memory first
            working_results = self._search_working_memory(query)
            
            # Convert memory entries back to reflections
            reflections = []
            for entry in working_results[:max_results]:
                reflection = self._memory_entry_to_reflection(entry)
                if reflection:
                    reflections.append(reflection)
                    entry.access_count += 1
            
            self._update_retrieval_metrics(len(reflections))
            
            logger.info(f"Retrieved {len(reflections)} relevant reflections")
            return reflections
            
        except Exception as e:
            logger.error(f"Error retrieving reflections: {str(e)}")
            return []
    
    def build_learning_graph(self,
                           include_patterns: bool = True,
                           include_insights: bool = True,
                           max_depth: int = 3) -> Dict[str, Any]:
        """Construct a graph of interconnected learnings."""
        try:
            graph = {
                "nodes": [],
                "edges": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "max_depth": max_depth
                }
            }
            
            # Get all reflections from working memory
            reflections = self._get_all_reflections()
            
            # Create nodes for each reflection
            for reflection in reflections:
                node = {
                    "id": reflection.id,
                    "type": "reflection",
                    "label": reflection.type.value,
                    "timestamp": reflection.timestamp.isoformat(),
                    "confidence": reflection.confidence
                }
                graph["nodes"].append(node)
            
            # Create edges based on relationships
            for reflection in reflections:
                if hasattr(reflection, 'related_reflections') and reflection.related_reflections:
                    for related_id in reflection.related_reflections:
                        edge = {
                            "source": reflection.id,
                            "target": related_id,
                            "type": "related",
                            "weight": 0.7
                        }
                        graph["edges"].append(edge)
            
            graph["metadata"].update({
                "total_nodes": len(graph["nodes"]),
                "total_edges": len(graph["edges"])
            })
            
            logger.info(f"Built learning graph with {len(graph['nodes'])} nodes")
            return graph
            
        except Exception as e:
            logger.error(f"Error building learning graph: {str(e)}")
            return {"nodes": [], "edges": [], "error": str(e)}
    
    # ==========================================================================
    # DOMAIN-SPECIFIC RETRIEVAL METHODS
    # ==========================================================================
    
    def get_domain_expectations(self, domain: str) -> List[Dict[str, Any]]:
        """Get historical expectations for a specific domain."""
        try:
            expectations = []
            
            # Search working memory for domain-specific entries
            for entry in self._working_memory.values():
                if 'expected_outcome' in entry.content:
                    entry_domain = entry.content.get('context', {}).get('domain')
                    if entry_domain == domain:
                        expectation = {
                            'domain': domain,
                            'expected': entry.content.get('expected_outcome'),
                            'actual': entry.content.get('actual_outcome'),
                            'timestamp': entry.timestamp,
                            'confidence': entry.relevance_score
                        }
                        expectations.append(expectation)
            
            return expectations
            
        except Exception as e:
            logger.error(f"Error getting domain expectations: {str(e)}")
            return []
    
    def find_related_reflections(self, feedback_data: Dict[str, Any]) -> List[Reflection]:
        """Get reflections related to feedback data."""
        try:
            reflections = []
            
            # Simple search through working memory
            for entry in self._working_memory.values():
                if entry.content.get('type') == 'reflection':
                    reflection = self._memory_entry_to_reflection(entry)
                    if reflection and self._is_feedback_related(reflection, feedback_data):
                        reflections.append(reflection)
            
            return reflections
            
        except Exception as e:
            logger.error(f"Error finding related reflections: {str(e)}")
            return []
    
    def get_decision_history(self, decision_type: str) -> List[Dict[str, Any]]:
        """Get history of similar decisions."""
        try:
            decisions = []
            
            for entry in self._working_memory.values():
                if 'decision_data' in entry.content:
                    decision_data = entry.content['decision_data']
                    if decision_data.get('type') == decision_type:
                        decision = {
                            'type': decision_type,
                            'decision_data': decision_data,
                            'outcome': entry.content.get('outcome'),
                            'timestamp': entry.timestamp,
                            'quality_score': entry.content.get('quality_score', 0.5)
                        }
                        decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error getting decision history: {str(e)}")
            return []
    
    def get_domain_history(self, domain: str) -> List[Dict[str, Any]]:
        """Get historical data for a specific domain."""
        try:
            history = []
            
            for entry in self._working_memory.values():
                entry_domain = entry.content.get('context', {}).get('domain')
                if entry_domain == domain:
                    history_item = {
                        'domain': domain,
                        'content': entry.content,
                        'timestamp': entry.timestamp,
                        'relevance': entry.relevance_score,
                        'source': entry.source
                    }
                    history.append(history_item)
            
            # Sort by timestamp, most recent first
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting domain history: {str(e)}")
            return []
    
    def get_active_domains(self) -> List[str]:
        """Get list of active domains based on recent activity."""
        try:
            recent_date = datetime.now() - timedelta(days=30)
            domain_counts = defaultdict(int)
            
            for entry in self._working_memory.values():
                if entry.timestamp > recent_date:
                    domain = entry.content.get('context', {}).get('domain')
                    if domain:
                        domain_counts[domain] += 1
            
            # Return top domains by activity
            active_domains = sorted(
                domain_counts.keys(),
                key=lambda d: domain_counts[d],
                reverse=True
            )
            
            return active_domains[:10]
            
        except Exception as e:
            logger.error(f"Error getting active domains: {str(e)}")
            return []
    
    def find_similar_contexts(self, action_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical contexts."""
        try:
            similar_contexts = []
            
            # Extract context features for comparison
            target_features = self._extract_context_features(action_data)
            
            for entry in self._working_memory.values():
                entry_context = entry.content.get('context', {})
                similarity_score = self._calculate_context_similarity(target_features, entry_context)
                
                if similarity_score > 0.5:  # Significant similarity
                    context = {
                        'context': entry_context,
                        'outcome': entry.content.get('outcome'),
                        'similarity_score': similarity_score,
                        'timestamp': entry.timestamp
                    }
                    similar_contexts.append(context)
            
            # Sort by similarity score
            similar_contexts.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_contexts[:10]
            
        except Exception as e:
            logger.error(f"Error finding similar contexts: {str(e)}")
            return []
    
    def count_reflections_in_timeframe(self, timeframe: timedelta) -> int:
        """Count reflections within timeframe."""
        try:
            cutoff_time = datetime.now() - timeframe
            count = 0
            
            for entry in self._working_memory.values():
                if (entry.content.get('type') == 'reflection' and 
                    entry.timestamp >= cutoff_time):
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting reflections: {str(e)}")
            return 0
    
    # ==========================================================================
    # MEMORY BACKEND IMPLEMENTATIONS
    # ==========================================================================
    
    def _detect_available_backends(self) -> List[StorageBackend]:
        """Detect which storage backends are available."""
        available = [StorageBackend.HYBRID]  # Always available
        
        if self.memory_system:
            available.append(StorageBackend.MEMORY_SYSTEM)
        
        return available
    
    def _store_in_hybrid(self, memory_entry: MemoryEntry) -> bool:
        """Store memory entry using hybrid approach."""
        try:
            # Store in working memory
            self._add_to_working_memory(memory_entry)
            
            # Also attempt memory system storage if available
            if self.memory_system and hasattr(self.memory_system, 'store_memory'):
                memory_data = {
                    'key': memory_entry.id,
                    'value': json.dumps(asdict(memory_entry)),
                    'type': memory_entry.memory_type.value
                }
                self.memory_system.store_memory(memory_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Hybrid storage error: {str(e)}")
            return False
    
    def _add_to_working_memory(self, memory_entry: MemoryEntry) -> None:
        """Add memory entry to working memory cache."""
        # Implement simple eviction if at capacity
        if len(self._working_memory) >= self._working_memory_limit:
            self._evict_from_working_memory()
        
        self._working_memory[memory_entry.id] = memory_entry
    
    def _evict_from_working_memory(self) -> None:
        """Evict oldest entries from working memory."""
        if not self._working_memory:
            return
        
        # Remove oldest entries
        sorted_entries = sorted(
            self._working_memory.items(),
            key=lambda x: x[1].timestamp
        )
        
        # Remove oldest 10% of entries
        num_to_remove = max(1, len(sorted_entries) // 10)
        
        for i in range(num_to_remove):
            entry_id = sorted_entries[i][0]
            del self._working_memory[entry_id]
    
    def _search_working_memory(self, query: RetrievalQuery) -> List[MemoryEntry]:
        """Search working memory for relevant entries."""
        results = []
        
        try:
            for entry in self._working_memory.values():
                # Apply filters
                if query.memory_type and entry.memory_type != query.memory_type:
                    continue
                
                if query.time_range:
                    start_time, end_time = query.time_range
                    if not (start_time <= entry.timestamp <= end_time):
                        continue
                
                # Calculate relevance score
                relevance = self._calculate_query_relevance(query, entry)
                
                if relevance >= query.relevance_threshold:
                    entry.relevance_score = relevance
                    results.append(entry)
                    self._memory_metrics["cache_hits"] += 1
            
            # Sort by relevance
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return results[:query.max_results]
            
        except Exception as e:
            logger.error(f"Working memory search error: {str(e)}")
            return []
    
    def _calculate_query_relevance(self, query: RetrievalQuery, entry: MemoryEntry) -> float:
        """Calculate relevance score between query and memory entry."""
        relevance = 0.0
        
        try:
            # Text similarity if query text provided
            if query.query_text:
                text_content = json.dumps(entry.content).lower()
                query_text = query.query_text.lower()
                
                # Simple keyword matching
                query_words = set(query_text.split())
                content_words = set(text_content.split())
                
                if query_words and content_words:
                    intersection = query_words.intersection(content_words)
                    relevance += len(intersection) / len(query_words.union(content_words))
            
            # Tag matching
            if query.tags and entry.tags:
                tag_intersection = set(query.tags).intersection(set(entry.tags))
                if tag_intersection:
                    relevance += len(tag_intersection) / len(set(query.tags).union(set(entry.tags)))
            
            # Recency boost
            age_days = (datetime.now() - entry.timestamp).days
            recency_boost = max(0, 1 - (age_days / 365))
            relevance += recency_boost * 0.1
            
            # Access count boost
            access_boost = min(0.2, entry.access_count * 0.01)
            relevance += access_boost
            
            return min(1.0, relevance)
            
        except Exception as e:
            logger.error(f"Error calculating query relevance: {str(e)}")
            return 0.0
    
    # ==========================================================================
    # CONVERSION AND UTILITY METHODS
    # ==========================================================================
    
    def _reflection_to_memory_entry(self, reflection: Reflection) -> MemoryEntry:
        """Convert Reflection object to MemoryEntry."""
        # Extract tags from reflection
        tags = [reflection.type.value]
        if reflection.context:
            domain = reflection.context.get('domain')
            if domain:
                tags.append(f"domain:{domain}")
        
        return MemoryEntry(
            id=reflection.id,
            content={
                'reflection_data': asdict(reflection),
                'type': 'reflection',
                'context': reflection.context,
                'analysis': reflection.analysis,
                'insights': reflection.insights,
                'lessons_learned': reflection.lessons_learned,
                'actionable_items': reflection.actionable_items
            },
            memory_type=MemoryType.EPISODIC,
            timestamp=reflection.timestamp,
            access_count=0,
            relevance_score=reflection.confidence,
            tags=tags,
            source="reflection_engine",
            expiry_date=datetime.now() + timedelta(days=self._default_expiry_days)
        )
    
    def _memory_entry_to_reflection(self, entry: MemoryEntry) -> Optional[Reflection]:
        """Convert MemoryEntry back to Reflection object."""
        try:
            reflection_data = entry.content.get('reflection_data')
            if not reflection_data:
                return None
            
            from .. import Reflection, ReflectionType
            
            return Reflection(
                id=reflection_data['id'],
                type=ReflectionType(reflection_data['type']),
                timestamp=datetime.fromisoformat(reflection_data['timestamp']),
                context=reflection_data['context'],
                analysis=reflection_data['analysis'],
                insights=reflection_data['insights'],
                lessons_learned=reflection_data['lessons_learned'],
                confidence=reflection_data['confidence'],
                actionable_items=reflection_data['actionable_items'],
                related_reflections=reflection_data.get('related_reflections')
            )
            
        except Exception as e:
            logger.error(f"Error converting memory entry to reflection: {str(e)}")
            return None
    
    def _context_to_query_text(self, context: Dict[str, Any]) -> str:
        """Convert context dict to search query text."""
        query_parts = []
        
        # Add domain if present
        if 'domain' in context:
            query_parts.append(f"domain:{context['domain']}")
        
        # Add other key context elements
        for key in ['complexity', 'priority', 'type']:
            if key in context:
                query_parts.append(f"{key}:{context[key]}")
        
        return " ".join(query_parts)
    
    def _get_all_reflections(self) -> List[Reflection]:
        """Get all reflections from working memory."""
        reflections = []
        
        for entry in self._working_memory.values():
            if entry.content.get('type') == 'reflection':
                reflection = self._memory_entry_to_reflection(entry)
                if reflection:
                    reflections.append(reflection)
        
        return reflections
    
    def _is_feedback_related(self, reflection: Reflection, feedback_data: Dict[str, Any]) -> bool:
        """Check if reflection is related to feedback data."""
        feedback_type = feedback_data.get('type', '')
        reflection_type = reflection.type.value
        
        return feedback_type in reflection_type or reflection_type in feedback_type
    
    def _extract_context_features(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context features for similarity matching."""
        features = {}
        
        for key in ['domain', 'complexity', 'priority', 'time_pressure', 'resources_adequate']:
            if key in action_data:
                features[key] = action_data[key]
        
        return features
    
    def _calculate_context_similarity(self, features1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Calculate context similarity score."""
        if not features1 or not context2:
            return 0.0
        
        common_keys = set(features1.keys()).intersection(set(context2.keys()))
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if features1[key] == context2[key]:
                matches += 1
        
        return matches / len(common_keys) if common_keys else 0.0
    
    # ==========================================================================
    # METRICS AND MAINTENANCE
    # ==========================================================================
    
    def _update_storage_metrics(self, success: bool, backend: StorageBackend) -> None:
        """Update storage metrics."""
        if success:
            self._memory_metrics["total_stored"] += 1
            
            if backend.value not in self._memory_metrics["storage_backends_used"]:
                self._memory_metrics["storage_backends_used"].append(backend.value)
        
        self._memory_metrics["last_updated"] = datetime.now()
    
    def _update_retrieval_metrics(self, results_count: int) -> None:
        """Update retrieval metrics."""
        self._memory_metrics["total_retrieved"] += results_count
        self._memory_metrics["last_updated"] = datetime.now()
    
    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory integration metrics."""
        return {
            **self._memory_metrics,
            "working_memory_size": len(self._working_memory),
            "working_memory_limit": self._working_memory_limit,
            "available_backends": [b.value for b in self._available_backends],
            "cache_hit_rate": (
                self._memory_metrics["cache_hits"] / 
                max(1, self._memory_metrics["cache_hits"] + self._memory_metrics["cache_misses"])
            ),
            "timestamp": datetime.now().isoformat()
        }
