"""
context_assembler.py - Intelligent context assembly for Bob's intelligence layer

This is the main API module for assembling context from multiple sources.
Implementation details are hidden in submodules for clarity.
Following the modular pattern established in Phase 1.
"""

from typing import Any, Dict, List, Optional, Union, Set, Tuple
from pathlib import Path
from datetime import datetime
import json

# Import implementation modules (to be created)
from .context.sources import SourceManager
from .context.memory import MemoryRetrieval
from .context.state import StateManager
from .context.relevance import RelevanceScorer
from .context.assembly import AssemblyEngine
from .context.metrics import ContextMetrics


class ContextAssembler:
    """
    Intelligent context assembly from multiple sources.
    
    This is the clean API surface for assembling relevant context
    for Bob's intelligence operations. It pulls from:
    - Recent memories and notes
    - Current state and active groups
    - Tool usage history
    - Graph relationships
    - File system context
    """
    
    def __init__(self, 
                 database_core,
                 filesystem_core,
                 max_context_size: int = 8192,
                 relevance_threshold: float = 0.7):
        """
        Initialize ContextAssembler with dependencies.
        
        Args:
            database_core: DatabaseCore instance for data access
            filesystem_core: FileSystemCore instance for file operations
            max_context_size: Maximum context size in tokens
            relevance_threshold: Minimum relevance score (0-1)
        """
        # Store core dependencies
        self.db = database_core
        self.fs = filesystem_core
        
        # Initialize submodules
        self.source_manager = SourceManager(self.db, self.fs)
        self.memory_retrieval = MemoryRetrieval(self.db)
        self.state_manager = StateManager(self.db)
        self.relevance_scorer = RelevanceScorer()
        self.assembly_engine = AssemblyEngine(max_context_size)
        self.metrics = ContextMetrics()
        
        # Store configuration
        self.max_context_size = max_context_size
        self.relevance_threshold = relevance_threshold
        
    # ==========================================
    # Main API Methods
    # ==========================================
    
    async def assemble_context(self, 
                              query: str,
                              group_id: Optional[int] = None,
                              context_type: str = "general") -> Dict[str, Any]:
        """
        Assemble relevant context for a query.
        
        Args:
            query: The query or prompt to contextualize
            group_id: Optional group to focus context on
            context_type: Type of context (general, task, reflection, assessment)
            
        Returns:
            Assembled context with metadata
        """
        start_time = datetime.now()
        
        # Gather raw context from all sources
        raw_context = await self.source_manager.gather_sources(
            query, group_id, context_type
        )
        
        # Score relevance of each context item
        scored_context = self.relevance_scorer.score_items(
            raw_context, query, self.relevance_threshold
        )
        
        # Assemble into final context
        assembled = self.assembly_engine.assemble(
            scored_context, 
            self.max_context_size
        )
        
        # Record metrics
        self.metrics.record_assembly(
            query_length=len(query),
            raw_items=len(raw_context),
            scored_items=len(scored_context),
            final_size=assembled['size'],
            duration=(datetime.now() - start_time).total_seconds()
        )
        
        return assembled
    
    async def get_memory_context(self, 
                                limit: int = 10,
                                group_id: Optional[int] = None) -> List[Dict]:
        """
        Retrieve recent memories as context.
        
        Args:
            limit: Maximum number of memories
            group_id: Optional group filter
            
        Returns:
            List of relevant memories
        """
        return await self.memory_retrieval.get_recent(limit, group_id)
    
    async def get_state_context(self, 
                               keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get current state as context.
        
        Args:
            keys: Specific state keys to retrieve (None for all)
            
        Returns:
            Current state dictionary
        """
        return await self.state_manager.get_state(keys)
    
    async def get_tool_context(self, 
                              limit: int = 20) -> List[Dict]:
        """
        Get recent tool usage as context.
        
        Args:
            limit: Maximum number of tool records
            
        Returns:
            Recent tool usage history
        """
        return await self.source_manager.get_tool_history(limit)
    
    async def get_graph_context(self, 
                               node_id: int,
                               depth: int = 2) -> Dict[str, Any]:
        """
        Get graph relationships as context.
        
        Args:
            node_id: Central node ID
            depth: How many hops to traverse
            
        Returns:
            Graph context with nodes and edges
        """
        return await self.source_manager.get_graph_neighborhood(node_id, depth)
    
    # ==========================================
    # Context Management
    # ==========================================
    
    def set_relevance_threshold(self, threshold: float):
        """Update relevance threshold (0-1)."""
        self.relevance_threshold = max(0.0, min(1.0, threshold))
        
    def set_max_context_size(self, size: int):
        """Update maximum context size."""
        self.max_context_size = max(1024, size)
        self.assembly_engine.max_size = self.max_context_size
    
    async def optimize_for_model(self, model_name: str):
        """
        Optimize context assembly for specific model.
        
        Args:
            model_name: Name of the model (e.g., 'llama3.2', 'mixtral')
        """
        # Model-specific optimizations
        model_configs = {
            'llama3.2': {'max_context': 4096, 'relevance': 0.75},
            'mixtral': {'max_context': 32768, 'relevance': 0.65},
            'deepseek-r1': {'max_context': 8192, 'relevance': 0.8}
        }
        
        if model_name in model_configs:
            config = model_configs[model_name]
            self.set_max_context_size(config['max_context'])
            self.set_relevance_threshold(config['relevance'])
    
    # ==========================================
    # Metrics and Analysis
    # ==========================================
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get context assembly metrics."""
        return self.metrics.get_summary()
    
    def reset_metrics(self):
        """Reset metrics tracking."""
        self.metrics.reset()
    
    # ==========================================
    # Context Templates
    # ==========================================
    
    async def assemble_task_context(self, task_description: str) -> Dict[str, Any]:
        """Assemble context specifically for task execution."""
        return await self.assemble_context(
            task_description, 
            context_type="task"
        )
    
    async def assemble_reflection_context(self, 
                                         output_to_reflect: str) -> Dict[str, Any]:
        """Assemble context for reflecting on generated output."""
        return await self.assemble_context(
            f"Reflection on: {output_to_reflect[:200]}...",
            context_type="reflection"
        )
    
    async def assemble_assessment_context(self, 
                                         session_id: Optional[int] = None) -> Dict[str, Any]:
        """Assemble context for performance assessment."""
        query = f"Assessment for session {session_id}" if session_id else "General assessment"
        return await self.assemble_context(
            query,
            context_type="assessment"
        )
    
    # ==========================================
    # Debugging and Inspection
    # ==========================================
    
    async def explain_assembly(self, 
                              query: str,
                              verbose: bool = False) -> Dict[str, Any]:
        """
        Explain how context would be assembled for a query.
        
        Args:
            query: The query to analyze
            verbose: Include detailed scoring information
            
        Returns:
            Explanation of assembly process
        """
        explanation = {
            'query': query,
            'sources': await self.source_manager.list_available_sources(),
            'relevance_threshold': self.relevance_threshold,
            'max_context_size': self.max_context_size
        }
        
        if verbose:
            # Perform dry run to show scoring
            raw_context = await self.source_manager.gather_sources(query, None, "general")
            scored = self.relevance_scorer.score_items(raw_context, query, 0.0)
            
            explanation['scoring_details'] = [
                {
                    'item': item['content'][:100] + '...' if len(item['content']) > 100 else item['content'],
                    'score': item['relevance_score'],
                    'included': item['relevance_score'] >= self.relevance_threshold
                }
                for item in scored[:10]  # Show top 10
            ]
        
        return explanation
