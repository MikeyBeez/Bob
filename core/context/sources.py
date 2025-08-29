"""
sources.py - Manage context sources for assembly
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
import json


class SourceManager:
    """Manages gathering context from multiple sources."""
    
    def __init__(self, database_core, filesystem_core):
        """
        Initialize with core dependencies.
        
        Args:
            database_core: Database access
            filesystem_core: File system access
        """
        self.db = database_core
        self.fs = filesystem_core
        
    async def gather_sources(self, 
                            query: str,
                            group_id: Optional[int],
                            context_type: str) -> List[Dict[str, Any]]:
        """
        Gather raw context from all available sources.
        
        Args:
            query: Query to contextualize
            group_id: Optional group filter
            context_type: Type of context needed
            
        Returns:
            List of context items from all sources
        """
        context_items = []
        
        # Gather from memories
        memories = await self._gather_memories(query, group_id)
        context_items.extend(memories)
        
        # Gather from notes
        notes = await self._gather_notes(query, group_id)
        context_items.extend(notes)
        
        # Gather from state
        state = await self._gather_state(context_type)
        context_items.extend(state)
        
        # Gather from tool history
        tools = await self._gather_tools(context_type)
        context_items.extend(tools)
        
        # Gather from graph relationships if group specified
        if group_id:
            graph = await self._gather_graph(group_id)
            context_items.extend(graph)
        
        return context_items
    
    async def _gather_memories(self, 
                              query: str, 
                              group_id: Optional[int]) -> List[Dict]:
        """Gather relevant memories."""
        memories = []
        
        # Get recent memories
        recent = await self.db.get_recent_memories(limit=20, group_id=group_id)
        for memory in recent:
            memories.append({
                'source': 'memory',
                'content': memory['content'],
                'metadata': {
                    'id': memory['id'],
                    'created_at': memory['created_at'],
                    'importance': memory.get('importance', 0.5)
                }
            })
        
        # Search for relevant memories by content
        if query:
            searched = await self.db.search_memories(query, limit=10)
            for memory in searched:
                memories.append({
                    'source': 'memory_search',
                    'content': memory['content'],
                    'metadata': {
                        'id': memory['id'],
                        'relevance': memory.get('relevance', 0.5)
                    }
                })
        
        return memories
    
    async def _gather_notes(self, 
                           query: str,
                           group_id: Optional[int]) -> List[Dict]:
        """Gather relevant notes."""
        notes = []
        
        # Get recent notes
        recent = await self.db.get_recent_notes(limit=10, group_id=group_id)
        for note in recent:
            notes.append({
                'source': 'note',
                'content': note['content'],
                'metadata': {
                    'id': note['id'],
                    'title': note.get('title', ''),
                    'created_at': note['created_at']
                }
            })
        
        return notes
    
    async def _gather_state(self, context_type: str) -> List[Dict]:
        """Gather relevant state information."""
        state_items = []
        
        # Get current state values
        states = await self.db.get_all_states()
        
        # Filter by relevance to context type
        relevant_keys = self._get_relevant_state_keys(context_type)
        
        for state in states:
            if state['key'] in relevant_keys:
                state_items.append({
                    'source': 'state',
                    'content': f"{state['key']}: {state['value']}",
                    'metadata': {
                        'key': state['key'],
                        'updated_at': state['updated_at']
                    }
                })
        
        return state_items
    
    async def _gather_tools(self, context_type: str) -> List[Dict]:
        """Gather tool usage history."""
        tools = []
        
        # Get recent tool usage
        recent_tools = await self.db.get_recent_tool_usage(limit=20)
        
        for tool in recent_tools:
            tools.append({
                'source': 'tool_history',
                'content': f"Used {tool['tool_name']}: {tool.get('result_summary', 'No summary')}",
                'metadata': {
                    'tool': tool['tool_name'],
                    'timestamp': tool['timestamp'],
                    'success': tool.get('success', True)
                }
            })
        
        return tools
    
    async def _gather_graph(self, group_id: int) -> List[Dict]:
        """Gather graph relationship context."""
        graph_items = []
        
        # Get graph edges for the group
        edges = await self.db.get_graph_edges(group_id, limit=10)
        
        for edge in edges:
            graph_items.append({
                'source': 'graph',
                'content': f"Relationship: {edge['relationship_type']} between {edge['source']} and {edge['target']}",
                'metadata': {
                    'edge_id': edge['id'],
                    'weight': edge.get('weight', 1.0)
                }
            })
        
        return graph_items
    
    def _get_relevant_state_keys(self, context_type: str) -> Set[str]:
        """Get state keys relevant to context type."""
        base_keys = {'current_task', 'active_session', 'last_error'}
        
        type_specific = {
            'task': {'task_queue', 'task_status', 'task_dependencies'},
            'reflection': {'last_output', 'reflection_history', 'quality_metrics'},
            'assessment': {'performance_metrics', 'success_rate', 'error_patterns'},
            'general': {'user_preferences', 'system_config', 'active_features'}
        }
        
        return base_keys | type_specific.get(context_type, set())
    
    async def list_available_sources(self) -> List[str]:
        """List all available context sources."""
        return [
            'memories',
            'notes', 
            'state',
            'tool_history',
            'graph_relationships',
            'file_system'
        ]
    
    async def get_tool_history(self, limit: int) -> List[Dict]:
        """Get recent tool usage history."""
        return await self.db.get_recent_tool_usage(limit=limit)
    
    async def get_graph_neighborhood(self, node_id: int, depth: int) -> Dict[str, Any]:
        """Get graph neighborhood around a node."""
        visited = set()
        to_visit = [(node_id, 0)]
        nodes = []
        edges = []
        
        while to_visit:
            current_id, current_depth = to_visit.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
                
            visited.add(current_id)
            
            # Get node information
            node_info = await self.db.get_node_info(current_id)
            if node_info:
                nodes.append(node_info)
            
            # Get edges
            node_edges = await self.db.get_node_edges(current_id)
            for edge in node_edges:
                edges.append(edge)
                
                # Add neighbors to visit
                if current_depth < depth:
                    neighbor_id = edge['target'] if edge['source'] == current_id else edge['source']
                    to_visit.append((neighbor_id, current_depth + 1))
        
        return {
            'center_node': node_id,
            'depth': depth,
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }
