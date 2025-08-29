"""
context_assembler.py - Context assembly and enrichment

Assembles comprehensive context from multiple sources for intelligent processing.
Combines knowledge, memories, and situational context.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ContextPart:
    """A single part of assembled context."""
    source: str
    type: str
    content: Any
    relevance: float
    timestamp: datetime


@dataclass
class AssembledContext:
    """Complete assembled context."""
    query: str
    parts: List[ContextPart]
    total_relevance: float
    assembly_time: float
    sources_used: List[str]
    context_size: int
    timestamp: datetime


class ContextAssembler:
    """
    Assembles comprehensive context from multiple sources.
    
    Combines:
    - Knowledge base entries
    - Historical memories
    - Current situational context
    - System state information
    """
    
    def __init__(self, knowledge_manager, db_core):
        """
        Initialize context assembler.
        
        Args:
            knowledge_manager: KnowledgeManager instance
            db_core: DatabaseCore instance
        """
        self.knowledge_manager = knowledge_manager
        self.db_core = db_core
        
        self.logger = logging.getLogger("ContextAssembler")
        self.assembly_cache = {}
        self.max_cache_size = 100
    
    async def assemble_context(self, query: str, base_context: Dict[str, Any]) -> AssembledContext:
        """
        Assemble comprehensive context for a query.
        
        Args:
            query: Query or input to assemble context for
            base_context: Base context information
            
        Returns:
            AssembledContext with all relevant information
        """
        start_time = datetime.now()
        self.logger.info(f"🔧 Assembling context for: {query[:50]}...")
        
        try:
            context_parts = []
            sources_used = []
            
            # Add base context
            if base_context:
                context_parts.append(ContextPart(
                    source="base_context",
                    type="provided",
                    content=base_context,
                    relevance=1.0,
                    timestamp=start_time
                ))
                sources_used.append("base_context")
            
            # Get knowledge context
            knowledge_context = await self._get_knowledge_context(query, base_context)
            if knowledge_context:
                context_parts.extend(knowledge_context)
                sources_used.append("knowledge")
            
            # Get memory context
            memory_context = await self._get_memory_context(query, base_context)
            if memory_context:
                context_parts.extend(memory_context)
                sources_used.append("memories")
            
            # Get system context
            system_context = await self._get_system_context(query, base_context)
            if system_context:
                context_parts.extend(system_context)
                sources_used.append("system")
            
            # Get temporal context
            temporal_context = await self._get_temporal_context(query, base_context)
            if temporal_context:
                context_parts.extend(temporal_context)
                sources_used.append("temporal")
            
            # Calculate total relevance
            total_relevance = sum(part.relevance for part in context_parts)
            context_size = len(str(context_parts))  # Approximate size
            
            # Sort by relevance
            context_parts.sort(key=lambda x: x.relevance, reverse=True)
            
            assembly_time = (datetime.now() - start_time).total_seconds()
            
            assembled = AssembledContext(
                query=query,
                parts=context_parts,
                total_relevance=total_relevance,
                assembly_time=assembly_time,
                sources_used=sources_used,
                context_size=context_size,
                timestamp=start_time
            )
            
            # Cache the result
            self._cache_context(query, assembled)
            
            self.logger.info(f"✅ Context assembled: {len(context_parts)} parts, {len(sources_used)} sources")
            return assembled
            
        except Exception as e:
            self.logger.error(f"Context assembly failed: {e}")
            return AssembledContext(
                query=query,
                parts=[],
                total_relevance=0.0,
                assembly_time=(datetime.now() - start_time).total_seconds(),
                sources_used=[],
                context_size=0,
                timestamp=start_time
            )
    
    async def _get_knowledge_context(self, query: str, base_context: Dict[str, Any]) -> List[ContextPart]:
        """Get relevant knowledge context."""
        try:
            knowledge_results = await self.knowledge_manager.retrieve_knowledge(query, base_context)
            
            context_parts = []
            for i, entry in enumerate(knowledge_results.entries[:5]):  # Limit to top 5
                relevance = knowledge_results.relevance_scores[i] if i < len(knowledge_results.relevance_scores) else 0.5
                
                part = ContextPart(
                    source=f"knowledge_{entry.id}",
                    type="knowledge",
                    content={
                        "title": entry.content[:100] + "...",
                        "content": entry.content,
                        "tags": entry.tags,
                        "importance": entry.importance
                    },
                    relevance=relevance,
                    timestamp=entry.last_accessed
                )
                context_parts.append(part)
            
            return context_parts
            
        except Exception as e:
            self.logger.error(f"Knowledge context retrieval failed: {e}")
            return []
    
    async def _get_memory_context(self, query: str, base_context: Dict[str, Any]) -> List[ContextPart]:
        """Get relevant memory context."""
        try:
            if not self.db_core:
                return []
            
            # Search for relevant memories/notes
            memories = self.db_core.search_notes(
                query=query,
                note_type="memory",
                limit=3
            )
            
            context_parts = []
            for memory in memories:
                part = ContextPart(
                    source=f"memory_{memory.get('id', 'unknown')}",
                    type="memory",
                    content={
                        "title": memory.get("title", ""),
                        "content": memory.get("content", ""),
                        "created_at": memory.get("created_at", ""),
                        "tags": memory.get("tags", [])
                    },
                    relevance=0.7,  # Base relevance for memories
                    timestamp=datetime.fromisoformat(memory.get("created_at", datetime.now().isoformat()))
                )
                context_parts.append(part)
            
            return context_parts
            
        except Exception as e:
            self.logger.error(f"Memory context retrieval failed: {e}")
            return []
    
    async def _get_system_context(self, query: str, base_context: Dict[str, Any]) -> List[ContextPart]:
        """Get relevant system context."""
        try:
            # Get current system state
            system_info = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "context_keys": list(base_context.keys()) if base_context else [],
                "system_status": "operational"
            }
            
            part = ContextPart(
                source="system_state",
                type="system",
                content=system_info,
                relevance=0.3,  # Lower relevance for system context
                timestamp=datetime.now()
            )
            
            return [part]
            
        except Exception as e:
            self.logger.error(f"System context retrieval failed: {e}")
            return []
    
    async def _get_temporal_context(self, query: str, base_context: Dict[str, Any]) -> List[ContextPart]:
        """Get temporal/chronological context."""
        try:
            now = datetime.now()
            
            temporal_info = {
                "current_time": now.isoformat(),
                "day_of_week": now.strftime("%A"),
                "time_of_day": now.strftime("%H:%M"),
                "date": now.strftime("%Y-%m-%d"),
                "temporal_context": "current_session"
            }
            
            part = ContextPart(
                source="temporal",
                type="temporal",
                content=temporal_info,
                relevance=0.2,  # Lower relevance for temporal info
                timestamp=now
            )
            
            return [part]
            
        except Exception as e:
            self.logger.error(f"Temporal context retrieval failed: {e}")
            return []
    
    def _cache_context(self, query: str, assembled_context: AssembledContext):
        """Cache assembled context for future use."""
        # Simple LRU-like caching
        cache_key = query.lower().strip()
        
        if len(self.assembly_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self.assembly_cache.keys(), 
                           key=lambda k: self.assembly_cache[k].timestamp)
            del self.assembly_cache[oldest_key]
        
        self.assembly_cache[cache_key] = assembled_context
    
    def get_cached_context(self, query: str) -> Optional[AssembledContext]:
        """Get cached context if available and recent."""
        cache_key = query.lower().strip()
        
        if cache_key in self.assembly_cache:
            cached = self.assembly_cache[cache_key]
            
            # Check if cache is still fresh (within 5 minutes)
            age = (datetime.now() - cached.timestamp).total_seconds()
            if age < 300:  # 5 minutes
                self.logger.info("📦 Using cached context")
                return cached
            else:
                # Remove stale cache
                del self.assembly_cache[cache_key]
        
        return None
    
    def get_context_summary(self, assembled_context: AssembledContext) -> Dict[str, Any]:
        """Get a summary of assembled context."""
        summary = {
            "total_parts": len(assembled_context.parts),
            "sources": assembled_context.sources_used,
            "total_relevance": assembled_context.total_relevance,
            "assembly_time": assembled_context.assembly_time,
            "context_size": assembled_context.context_size,
            "parts_by_type": {}
        }
        
        # Count parts by type
        for part in assembled_context.parts:
            part_type = part.type
            if part_type not in summary["parts_by_type"]:
                summary["parts_by_type"][part_type] = 0
            summary["parts_by_type"][part_type] += 1
        
        return summary
    
    def clear_cache(self):
        """Clear the context cache."""
        self.assembly_cache.clear()
        self.logger.info("🗑️ Context cache cleared")
