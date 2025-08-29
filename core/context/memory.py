"""
memory.py - Memory retrieval for context assembly
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


class MemoryRetrieval:
    """Handles memory retrieval and ranking for context."""
    
    def __init__(self, database_core):
        """
        Initialize with database access.
        
        Args:
            database_core: Database access for memories
        """
        self.db = database_core
        
    async def get_recent(self, 
                        limit: int = 10,
                        group_id: Optional[int] = None) -> List[Dict]:
        """
        Get recent memories with importance weighting.
        
        Args:
            limit: Maximum memories to retrieve
            group_id: Optional group filter
            
        Returns:
            List of memory dictionaries
        """
        # Get raw memories
        memories = await self.db.get_recent_memories(limit=limit * 2, group_id=group_id)
        
        # Score and rank by recency + importance
        scored = []
        now = datetime.now()
        
        for memory in memories:
            # Calculate recency score (0-1, newer = higher)
            created = datetime.fromisoformat(memory['created_at'])
            age_hours = (now - created).total_seconds() / 3600
            recency_score = max(0, 1 - (age_hours / 168))  # Decay over 1 week
            
            # Get importance score
            importance = memory.get('importance', 0.5)
            
            # Combined score
            score = (recency_score * 0.4) + (importance * 0.6)
            
            scored.append({
                **memory,
                'relevance_score': score,
                'recency_score': recency_score,
                'importance_score': importance
            })
        
        # Sort by score and return top N
        scored.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored[:limit]
    
    async def search_semantic(self, 
                             query: str,
                             limit: int = 10) -> List[Dict]:
        """
        Search memories semantically.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Relevant memories
        """
        # Use database search
        results = await self.db.search_memories(query, limit=limit)
        
        # Enhance with metadata
        enhanced = []
        for result in results:
            enhanced.append({
                **result,
                'search_relevance': result.get('relevance', 0.5),
                'source': 'semantic_search'
            })
        
        return enhanced
    
    async def get_by_tags(self, 
                         tags: List[str],
                         limit: int = 10) -> List[Dict]:
        """
        Get memories by tags.
        
        Args:
            tags: Tags to filter by
            limit: Maximum results
            
        Returns:
            Tagged memories
        """
        memories = []
        
        for tag in tags:
            tagged = await self.db.get_memories_by_tag(tag, limit=limit)
            memories.extend(tagged)
        
        # Deduplicate by ID
        seen = set()
        unique = []
        for memory in memories:
            if memory['id'] not in seen:
                seen.add(memory['id'])
                unique.append(memory)
        
        return unique[:limit]
    
    async def get_episodic(self, 
                           time_window: timedelta,
                           group_id: Optional[int] = None) -> List[Dict]:
        """
        Get episodic memories within time window.
        
        Args:
            time_window: Time window to retrieve
            group_id: Optional group filter
            
        Returns:
            Episodic memories
        """
        start_time = datetime.now() - time_window
        
        memories = await self.db.get_memories_in_timerange(
            start_time=start_time,
            end_time=datetime.now(),
            group_id=group_id
        )
        
        # Add episodic context
        for memory in memories:
            memory['episodic_context'] = True
            memory['time_window'] = str(time_window)
        
        return memories
    
    async def get_working_memory(self) -> List[Dict]:
        """
        Get current working memory (very recent, high importance).
        
        Returns:
            Working memory items
        """
        # Get memories from last hour with high importance
        recent = await self.get_episodic(timedelta(hours=1))
        
        # Filter for high importance
        working = [
            m for m in recent 
            if m.get('importance', 0) >= 0.7
        ]
        
        return working[:5]  # Keep working memory small
    
    async def get_consolidated(self, 
                              topic: str,
                              limit: int = 5) -> List[Dict]:
        """
        Get consolidated memories about a topic.
        
        Args:
            topic: Topic to retrieve
            limit: Maximum results
            
        Returns:
            Consolidated memories
        """
        # Search for topic
        topical = await self.search_semantic(topic, limit=limit * 2)
        
        # Group similar memories
        consolidated = []
        seen_content = set()
        
        for memory in topical:
            # Simple deduplication by content similarity
            content_key = memory['content'][:50].lower()
            if content_key not in seen_content:
                seen_content.add(content_key)
                memory['consolidated'] = True
                consolidated.append(memory)
        
        return consolidated[:limit]
