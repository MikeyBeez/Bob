"""
assembly.py - Context assembly engine
"""

from typing import Any, Dict, List
import json


class AssemblyEngine:
    """Assembles scored context items into final context."""
    
    def __init__(self, max_size: int = 8192):
        """
        Initialize assembly engine.
        
        Args:
            max_size: Maximum context size in tokens (approximate)
        """
        self.max_size = max_size
        
    def assemble(self, 
                scored_items: List[Dict[str, Any]],
                max_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Assemble scored items into final context.
        
        Args:
            scored_items: Items with relevance scores
            max_size: Override max size
            
        Returns:
            Assembled context with metadata
        """
        if max_size is None:
            max_size = self.max_size
        
        # Group items by source
        grouped = self._group_by_source(scored_items)
        
        # Build context sections
        sections = []
        total_size = 0
        items_included = 0
        
        # Priority order for sources
        source_priority = [
            'memory_search',
            'state',
            'memory',
            'note',
            'tool_history',
            'graph'
        ]
        
        for source in source_priority:
            if source not in grouped:
                continue
            
            section = self._build_section(
                source, 
                grouped[source],
                max_size - total_size
            )
            
            if section:
                sections.append(section)
                total_size += section['size']
                items_included += section['item_count']
                
                if total_size >= max_size * 0.95:  # Leave some buffer
                    break
        
        # Build final context
        context = self._format_context(sections)
        
        return {
            'context': context,
            'metadata': {
                'total_items': len(scored_items),
                'items_included': items_included,
                'size': total_size,
                'max_size': max_size,
                'utilization': total_size / max_size if max_size > 0 else 0,
                'sections': len(sections),
                'sources': [s['source'] for s in sections]
            },
            'sections': sections
        }
    
    def _group_by_source(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group items by source type."""
        grouped = {}
        
        for item in items:
            source = item.get('source', 'unknown')
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(item)
        
        return grouped
    
    def _build_section(self, 
                      source: str,
                      items: List[Dict],
                      remaining_size: int) -> Optional[Dict]:
        """
        Build a context section from items.
        
        Args:
            source: Source type
            items: Items from this source
            remaining_size: Remaining space
            
        Returns:
            Section dictionary or None if no space
        """
        if remaining_size <= 0:
            return None
        
        section_items = []
        section_size = 0
        
        for item in items:
            # Estimate item size (rough token count)
            item_size = self._estimate_size(item['content'])
            
            if section_size + item_size <= remaining_size:
                section_items.append(item)
                section_size += item_size
            else:
                break  # No more space
        
        if not section_items:
            return None
        
        return {
            'source': source,
            'items': section_items,
            'item_count': len(section_items),
            'size': section_size,
            'avg_relevance': sum(i['relevance_score'] for i in section_items) / len(section_items)
        }
    
    def _format_context(self, sections: List[Dict]) -> str:
        """
        Format sections into final context string.
        
        Args:
            sections: Context sections
            
        Returns:
            Formatted context
        """
        context_parts = []
        
        for section in sections:
            # Add section header
            header = self._get_section_header(section['source'])
            if header:
                context_parts.append(header)
            
            # Add items
            for item in section['items']:
                formatted = self._format_item(item)
                context_parts.append(formatted)
            
            # Add separator
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _get_section_header(self, source: str) -> str:
        """Get header for context section."""
        headers = {
            'memory_search': "## Relevant Memories",
            'state': "## Current State",
            'memory': "## Recent Memories",
            'note': "## Related Notes",
            'tool_history': "## Tool Usage History",
            'graph': "## Graph Relationships"
        }
        
        return headers.get(source, f"## {source.title()}")
    
    def _format_item(self, item: Dict) -> str:
        """
        Format a context item.
        
        Args:
            item: Context item
            
        Returns:
            Formatted string
        """
        content = item['content']
        metadata = item.get('metadata', {})
        
        # Add relevance indicator
        relevance = item.get('relevance_score', 0)
        if relevance >= 0.9:
            prefix = "★★★"
        elif relevance >= 0.7:
            prefix = "★★"
        elif relevance >= 0.5:
            prefix = "★"
        else:
            prefix = "•"
        
        # Format with metadata hints
        formatted = f"{prefix} {content}"
        
        # Add timestamp if recent
        if 'created_at' in metadata or 'timestamp' in metadata:
            formatted += f" [{metadata.get('created_at', metadata.get('timestamp', ''))}]"
        
        return formatted
    
    def _estimate_size(self, text: str) -> int:
        """
        Estimate token size of text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def optimize_assembly(self, 
                         scored_items: List[Dict],
                         constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize assembly with specific constraints.
        
        Args:
            scored_items: Items to assemble
            constraints: Assembly constraints
            
        Returns:
            Optimized assembly
        """
        # Apply constraints
        max_items = constraints.get('max_items', 100)
        min_relevance = constraints.get('min_relevance', 0.3)
        required_sources = constraints.get('required_sources', [])
        
        # Filter by constraints
        filtered = []
        for item in scored_items:
            if item['relevance_score'] >= min_relevance:
                filtered.append(item)
        
        # Ensure required sources
        for source in required_sources:
            source_items = [i for i in filtered if i['source'] == source]
            if not source_items:
                # Try to find at least one from original
                for item in scored_items:
                    if item['source'] == source:
                        filtered.append(item)
                        break
        
        # Limit items
        filtered = filtered[:max_items]
        
        # Assemble with constraints
        return self.assemble(filtered, self.max_size)
