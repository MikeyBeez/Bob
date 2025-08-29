"""
prioritizer.py - Context prioritization and ranking module

Handles intelligent prioritization of context items based on
relevance, recency, importance, and query matching.
Clean API that implements sophisticated ranking algorithms.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
import re
from collections import defaultdict


class ContextItem:
    """
    Wrapper for context items with scoring metadata.
    
    Provides uniform interface for different types of context
    while preserving original data and adding relevance metrics.
    """
    
    def __init__(self, content: Any, source_id: str, item_type: str = "generic"):
        self.content = content
        self.source_id = source_id
        self.item_type = item_type
        self.created_at = getattr(content, 'created_at', datetime.now())
        self.scores = {}
        self.final_score = 0.0
        self.metadata = {}
    
    def add_score(self, score_type: str, score: float, weight: float = 1.0):
        """Add a component score with optional weight."""
        self.scores[score_type] = {
            'score': score,
            'weight': weight,
            'contribution': score * weight
        }
    
    def calculate_final_score(self) -> float:
        """Calculate final weighted score from all components."""
        total_contribution = sum(s['contribution'] for s in self.scores.values())
        total_weight = sum(s['weight'] for s in self.scores.values())
        
        if total_weight == 0:
            self.final_score = 0.0
        else:
            self.final_score = total_contribution / total_weight
        
        return self.final_score


class ContextPrioritizer:
    """
    Intelligent context prioritization system.
    
    Public API for ranking context items using multiple
    algorithms and combining scores intelligently.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Scoring weights (configurable)
        self.weights = {
            'query_relevance': self.config.get('query_relevance_weight', 0.4),
            'temporal_relevance': self.config.get('temporal_relevance_weight', 0.3),
            'source_priority': self.config.get('source_priority_weight', 0.2),
            'content_quality': self.config.get('content_quality_weight', 0.1)
        }
        
        # Temporal decay parameters
        self.temporal_config = {
            'half_life_hours': self.config.get('temporal_half_life_hours', 24),
            'max_age_days': self.config.get('max_age_days', 30)
        }
        
        self._metrics = {
            'items_scored': 0,
            'scoring_time_ms': 0,
            'average_score': 0.0
        }
    
    def prioritize_context(self, items: List[Any], query: str,
                          source_priorities: Optional[Dict[str, float]] = None,
                          max_items: Optional[int] = None) -> List[ContextItem]:
        """
        Main API for context prioritization.
        
        Args:
            items: Raw context items from various sources
            query: Query to match against
            source_priorities: Per-source priority multipliers
            max_items: Maximum items to return
            
        Returns:
            List of ContextItem objects sorted by relevance
        """
        start_time = datetime.now()
        
        # Convert to ContextItem objects
        context_items = []
        for item in items:
            source_id = getattr(item, 'source_id', 'unknown')
            item_type = getattr(item, 'type', 'generic')
            context_items.append(ContextItem(item, source_id, item_type))
        
        # Score each item
        for item in context_items:
            self._score_item(item, query, source_priorities or {})
        
        # Sort by final score (descending)
        context_items.sort(key=lambda x: x.final_score, reverse=True)
        
        # Apply limit
        if max_items:
            context_items = context_items[:max_items]
        
        # Update metrics
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self._metrics['items_scored'] += len(context_items)
        self._metrics['scoring_time_ms'] += processing_time
        if context_items:
            self._metrics['average_score'] = sum(item.final_score for item in context_items) / len(context_items)
        
        return context_items
    
    def _score_item(self, item: ContextItem, query: str, source_priorities: Dict[str, float]):
        """Score a single context item using multiple factors."""
        
        # Query relevance scoring
        query_score = self._calculate_query_relevance(item.content, query)
        item.add_score('query_relevance', query_score, self.weights['query_relevance'])
        
        # Temporal relevance scoring
        temporal_score = self._calculate_temporal_relevance(item.created_at)
        item.add_score('temporal_relevance', temporal_score, self.weights['temporal_relevance'])
        
        # Source priority scoring
        source_score = source_priorities.get(item.source_id, 0.5)
        item.add_score('source_priority', source_score, self.weights['source_priority'])
        
        # Content quality scoring
        quality_score = self._calculate_content_quality(item.content)
        item.add_score('content_quality', quality_score, self.weights['content_quality'])
        
        # Calculate final score
        item.calculate_final_score()
    
    def _calculate_query_relevance(self, content: Any, query: str) -> float:
        """
        Calculate how well content matches the query.
        
        Uses multiple matching strategies:
        - Exact keyword matches
        - Semantic similarity (simplified)
        - Context overlap
        """
        if not query or not content:
            return 0.0
        
        # Convert content to searchable text
        text = self._extract_text(content)
        if not text:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Exact match bonus
        exact_match_score = 1.0 if query_lower in text_lower else 0.0
        
        # Keyword matching
        query_words = set(re.findall(r'\w+', query_lower))
        text_words = set(re.findall(r'\w+', text_lower))
        
        if not query_words:
            return 0.0
        
        keyword_matches = len(query_words.intersection(text_words))
        keyword_score = keyword_matches / len(query_words)
        
        # Length normalization (longer content gets slight penalty)
        length_factor = 1.0 / (1.0 + len(text) / 1000.0)
        
        # Combine scores
        relevance_score = (
            exact_match_score * 0.4 +
            keyword_score * 0.5 +
            length_factor * 0.1
        )
        
        return min(1.0, relevance_score)
    
    def _calculate_temporal_relevance(self, created_at: datetime) -> float:
        """
        Calculate relevance based on recency.
        
        Uses exponential decay with configurable half-life.
        """
        if not created_at:
            return 0.0
        
        now = datetime.now()
        age_hours = (now - created_at).total_seconds() / 3600.0
        
        # Check max age cutoff
        max_age_hours = self.temporal_config['max_age_days'] * 24
        if age_hours > max_age_hours:
            return 0.0
        
        # Exponential decay
        half_life = self.temporal_config['half_life_hours']
        decay_factor = math.exp(-0.693 * age_hours / half_life)
        
        return decay_factor
    
    def _calculate_content_quality(self, content: Any) -> float:
        """
        Assess content quality based on various factors.
        
        Considers:
        - Content length (not too short, not too long)
        - Structure indicators
        - Completeness
        """
        text = self._extract_text(content)
        if not text:
            return 0.0
        
        # Length scoring (sweet spot around 200-1000 chars)
        length = len(text)
        if length < 50:
            length_score = length / 50.0  # Penalize very short
        elif length > 2000:
            length_score = 2000.0 / length  # Penalize very long
        else:
            length_score = 1.0  # Good length
        
        # Structure indicators
        structure_score = 0.5
        if any(marker in text for marker in ['\n\n', '- ', '1. ', '* ']):
            structure_score += 0.2  # Has structure
        if any(marker in text for marker in ['?', '!', ':']):
            structure_score += 0.1  # Has punctuation variety
        
        # Completeness (heuristic: doesn't end mid-sentence)
        completeness_score = 1.0
        if text.rstrip() and text.rstrip()[-1] not in '.!?':
            completeness_score = 0.7  # Might be incomplete
        
        quality_score = (
            length_score * 0.4 +
            structure_score * 0.3 +
            completeness_score * 0.3
        )
        
        return min(1.0, quality_score)
    
    def _extract_text(self, content: Any) -> str:
        """Extract text from various content types."""
        if isinstance(content, str):
            return content
        
        if hasattr(content, 'content'):
            return str(content.content)
        
        if hasattr(content, 'text'):
            return str(content.text)
        
        if isinstance(content, dict):
            # Try common text fields
            for field in ['content', 'text', 'body', 'description', 'message']:
                if field in content:
                    return str(content[field])
        
        # Fallback to string representation
        return str(content)
    
    def update_weights(self, new_weights: Dict[str, float]) -> bool:
        """Update scoring weights dynamically."""
        try:
            for key, value in new_weights.items():
                if key in self.weights and 0.0 <= value <= 1.0:
                    self.weights[key] = value
            return True
        except Exception:
            return False
    
    def get_scoring_explanation(self, item: ContextItem) -> Dict[str, Any]:
        """Get detailed explanation of how an item was scored."""
        return {
            'final_score': item.final_score,
            'component_scores': item.scores,
            'weights_used': self.weights,
            'item_metadata': {
                'source_id': item.source_id,
                'item_type': item.item_type,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get prioritization performance metrics."""
        return {
            **self._metrics,
            'current_weights': self.weights,
            'temporal_config': self.temporal_config
        }
