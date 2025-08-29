"""
relevance.py - Relevance scoring for context items
"""

from typing import Any, Dict, List
import re
from datetime import datetime, timedelta


class RelevanceScorer:
    """Scores context items for relevance to queries."""
    
    def __init__(self):
        """Initialize relevance scorer."""
        pass
    
    def score_items(self, 
                   items: List[Dict[str, Any]],
                   query: str,
                   threshold: float) -> List[Dict[str, Any]]:
        """
        Score items for relevance to query.
        
        Args:
            items: Context items to score
            query: Query to score against
            threshold: Minimum relevance threshold
            
        Returns:
            Items with relevance scores, filtered by threshold
        """
        scored = []
        query_terms = self._extract_terms(query.lower())
        
        for item in items:
            # Calculate relevance score
            score = self._calculate_relevance(item, query_terms)
            
            # Add score to item
            item['relevance_score'] = score
            
            # Only include if above threshold
            if score >= threshold:
                scored.append(item)
        
        # Sort by relevance
        scored.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored
    
    def _calculate_relevance(self, 
                            item: Dict[str, Any],
                            query_terms: List[str]) -> float:
        """
        Calculate relevance score for an item.
        
        Args:
            item: Context item
            query_terms: Extracted query terms
            
        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        
        # Content relevance (text matching)
        content = item.get('content', '').lower()
        content_score = self._text_relevance(content, query_terms)
        score += content_score * 0.4
        
        # Source type relevance
        source_score = self._source_relevance(item.get('source', ''))
        score += source_score * 0.2
        
        # Recency relevance
        recency_score = self._recency_relevance(item.get('metadata', {}))
        score += recency_score * 0.2
        
        # Importance/weight relevance
        importance_score = self._importance_relevance(item.get('metadata', {}))
        score += importance_score * 0.2
        
        return min(1.0, score)
    
    def _text_relevance(self, text: str, terms: List[str]) -> float:
        """
        Calculate text relevance score.
        
        Args:
            text: Text to analyze
            terms: Query terms
            
        Returns:
            Text relevance (0-1)
        """
        if not text or not terms:
            return 0.0
        
        # Count term occurrences
        matches = 0
        for term in terms:
            # Exact match
            if term in text:
                matches += 1
            # Partial match (for longer terms)
            elif len(term) > 3 and any(term in word for word in text.split()):
                matches += 0.5
        
        # Normalize by number of terms
        return min(1.0, matches / len(terms))
    
    def _source_relevance(self, source: str) -> float:
        """
        Score relevance based on source type.
        
        Args:
            source: Source type
            
        Returns:
            Source relevance (0-1)
        """
        # Source priorities
        priorities = {
            'memory_search': 1.0,
            'state': 0.9,
            'memory': 0.8,
            'note': 0.7,
            'tool_history': 0.6,
            'graph': 0.5
        }
        
        return priorities.get(source, 0.3)
    
    def _recency_relevance(self, metadata: Dict) -> float:
        """
        Score relevance based on recency.
        
        Args:
            metadata: Item metadata
            
        Returns:
            Recency relevance (0-1)
        """
        # Check for timestamp fields
        timestamp = None
        for field in ['created_at', 'updated_at', 'timestamp']:
            if field in metadata:
                timestamp = metadata[field]
                break
        
        if not timestamp:
            return 0.5  # Neutral score if no timestamp
        
        try:
            # Parse timestamp
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            # Calculate age
            age = datetime.now() - dt
            
            # Score based on age (decay over 7 days)
            if age < timedelta(hours=1):
                return 1.0
            elif age < timedelta(days=1):
                return 0.8
            elif age < timedelta(days=3):
                return 0.6
            elif age < timedelta(days=7):
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.5
    
    def _importance_relevance(self, metadata: Dict) -> float:
        """
        Score relevance based on importance/weight.
        
        Args:
            metadata: Item metadata
            
        Returns:
            Importance relevance (0-1)
        """
        # Check for importance indicators
        importance = metadata.get('importance', 
                                 metadata.get('weight',
                                            metadata.get('relevance', 0.5)))
        
        # Ensure in valid range
        return max(0.0, min(1.0, float(importance)))
    
    def _extract_terms(self, query: str) -> List[str]:
        """
        Extract search terms from query.
        
        Args:
            query: Query string
            
        Returns:
            List of terms
        """
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                    'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was'}
        
        # Extract words
        words = re.findall(r'\w+', query.lower())
        
        # Filter stopwords and short words
        terms = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Also include important bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if words[i] not in stopwords or words[i+1] not in stopwords:
                terms.append(bigram)
        
        return terms
    
    def explain_score(self, item: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Explain how a score was calculated.
        
        Args:
            item: Context item
            query: Query string
            
        Returns:
            Explanation of scoring
        """
        query_terms = self._extract_terms(query.lower())
        content = item.get('content', '').lower()
        
        explanation = {
            'query': query,
            'query_terms': query_terms,
            'scores': {
                'text_relevance': self._text_relevance(content, query_terms),
                'source_relevance': self._source_relevance(item.get('source', '')),
                'recency_relevance': self._recency_relevance(item.get('metadata', {})),
                'importance_relevance': self._importance_relevance(item.get('metadata', {}))
            },
            'weights': {
                'text': 0.4,
                'source': 0.2,
                'recency': 0.2,
                'importance': 0.2
            }
        }
        
        # Calculate total
        total = sum(
            score * explanation['weights'][key.replace('_relevance', '')]
            for key, score in explanation['scores'].items()
        )
        
        explanation['total_score'] = total
        explanation['item_preview'] = content[:100] + '...' if len(content) > 100 else content
        
        return explanation
