"""
pattern_detector.py - Detect patterns in actions, decisions, and outcomes

This module identifies recurring patterns across historical data to understand
what consistently leads to success or failure. It uses statistical analysis
and machine learning techniques to extract meaningful patterns.
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import json
import logging
import math

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns that can be detected."""
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    TEMPORAL_PATTERN = "temporal_pattern"
    CONTEXTUAL_PATTERN = "contextual_pattern"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    CORRELATION_PATTERN = "correlation_pattern"


@dataclass
class Pattern:
    """Represents a detected pattern."""
    id: str
    type: PatternType
    description: str
    conditions: List[Dict[str, Any]]
    frequency: int
    confidence: float
    support: float  # Frequency relative to total data
    lift: float  # How much more likely than random
    examples: List[Dict[str, Any]]
    implications: List[str]
    created_at: datetime
    last_seen: datetime


@dataclass
class PatternMatch:
    """Represents a match between current context and detected pattern."""
    pattern_id: str
    match_confidence: float
    matching_conditions: List[str]
    implications: List[str]
    recommended_actions: List[str]


class PatternDetector:
    """
    Detects recurring patterns in actions, decisions, and outcomes.
    
    This class analyzes historical data to identify patterns that consistently
    lead to success or failure, helping improve future decision-making through
    pattern recognition and application.
    """
    
    def __init__(self, 
                 db_core: Optional[Any] = None,
                 learning_rate: float = 0.1,
                 min_pattern_frequency: int = 3,
                 confidence_threshold: float = 0.6):
        """
        Initialize PatternDetector.
        
        Args:
            db_core: DatabaseCore instance for accessing historical data
            learning_rate: Rate at which patterns are updated with new data
            min_pattern_frequency: Minimum occurrences to consider a pattern
            confidence_threshold: Minimum confidence for pattern detection
        """
        self.db_core = db_core
        self.learning_rate = learning_rate
        self.min_pattern_frequency = min_pattern_frequency
        self.confidence_threshold = confidence_threshold
        
        # Pattern storage
        self._detected_patterns = {}
        self._pattern_cache = {}
        self._pattern_metrics = {
            "total_patterns_detected": 0,
            "success_patterns": 0,
            "failure_patterns": 0,
            "pattern_accuracy": 0.0,
            "last_updated": datetime.now()
        }
        
        # Analysis parameters
        self._lookback_window = timedelta(days=90)
        self._pattern_similarity_threshold = 0.8
        
    # ==========================================================================
    # CORE PATTERN DETECTION METHODS
    # ==========================================================================
    
    def detect_patterns(self,
                       timeframe: timedelta,
                       domain: Optional[str] = None,
                       min_confidence: float = 0.6) -> Dict[str, Any]:
        """
        Identify recurring patterns across actions and outcomes.
        
        Args:
            timeframe: Time period to analyze
            domain: Specific domain to focus on (optional)
            min_confidence: Minimum confidence for pattern inclusion
            
        Returns:
            Dictionary containing detected patterns and analysis
        """
        try:
            # Get historical data
            historical_data = self._get_historical_data(timeframe, domain)
            
            if len(historical_data) < self.min_pattern_frequency:
                return {"patterns": [], "message": "Insufficient data for pattern detection"}
            
            # Detect different types of patterns
            success_patterns = self._detect_success_patterns_internal(historical_data, min_confidence)
            failure_patterns = self._detect_failure_patterns_internal(historical_data, min_confidence)
            temporal_patterns = self._detect_temporal_patterns(historical_data, min_confidence)
            contextual_patterns = self._detect_contextual_patterns(historical_data, min_confidence)
            
            # Combine and rank patterns
            all_patterns = success_patterns + failure_patterns + temporal_patterns + contextual_patterns
            ranked_patterns = self._rank_patterns_by_importance(all_patterns)
            
            # Update pattern cache
            self._update_pattern_cache(ranked_patterns)
            
            # Generate analysis summary
            analysis = {
                "timeframe": str(timeframe),
                "domain": domain or "all",
                "data_points": len(historical_data),
                "patterns_detected": len(ranked_patterns),
                "pattern_breakdown": {
                    "success_patterns": len(success_patterns),
                    "failure_patterns": len(failure_patterns),
                    "temporal_patterns": len(temporal_patterns),
                    "contextual_patterns": len(contextual_patterns)
                },
                "top_patterns": ranked_patterns[:10],
                "confidence_stats": self._calculate_confidence_stats(ranked_patterns),
                "analyzed_at": datetime.now().isoformat()
            }
            
            logger.info(f"Detected {len(ranked_patterns)} patterns in {domain or 'all'} domain(s)")
            return analysis
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {str(e)}")
            return {"error": str(e), "patterns": []}
    
    def detect_success_patterns(self,
                              min_frequency: int = 3,
                              min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """
        Identify what consistently leads to successful outcomes.
        
        Args:
            min_frequency: Minimum occurrences for pattern consideration
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of success patterns with confidence scores
        """
        try:
            # Get successful outcomes from historical data
            historical_data = self._get_historical_data(self._lookback_window)
            success_data = [d for d in historical_data if self._is_successful_outcome(d)]
            
            if len(success_data) < min_frequency:
                return []
            
            # Detect patterns in successful outcomes
            patterns = self._detect_success_patterns_internal(success_data, min_confidence)
            
            # Filter by frequency and confidence
            filtered_patterns = [
                p for p in patterns 
                if p.frequency >= min_frequency and p.confidence >= min_confidence
            ]
            
            # Convert to dictionary format for API
            result = []
            for pattern in filtered_patterns:
                result.append({
                    "id": pattern.id,
                    "description": pattern.description,
                    "conditions": pattern.conditions,
                    "frequency": pattern.frequency,
                    "confidence": pattern.confidence,
                    "support": pattern.support,
                    "lift": pattern.lift,
                    "examples": pattern.examples[:3],  # Limit examples
                    "implications": pattern.implications,
                    "type": "success_pattern"
                })
            
            self._pattern_metrics["success_patterns"] = len(result)
            logger.info(f"Detected {len(result)} success patterns")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting success patterns: {str(e)}")
            return []
    
    def detect_failure_patterns(self,
                              min_frequency: int = 2,
                              min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Identify what consistently leads to poor outcomes.
        
        Args:
            min_frequency: Minimum occurrences (lower for failures to catch early)
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of failure patterns with mitigation strategies
        """
        try:
            # Get failure outcomes from historical data
            historical_data = self._get_historical_data(self._lookback_window)
            failure_data = [d for d in historical_data if self._is_failed_outcome(d)]
            
            if len(failure_data) < min_frequency:
                return []
            
            # Detect patterns in failed outcomes
            patterns = self._detect_failure_patterns_internal(failure_data, min_confidence)
            
            # Filter by frequency and confidence
            filtered_patterns = [
                p for p in patterns 
                if p.frequency >= min_frequency and p.confidence >= min_confidence
            ]
            
            # Convert to dictionary format with mitigation strategies
            result = []
            for pattern in filtered_patterns:
                result.append({
                    "id": pattern.id,
                    "description": pattern.description,
                    "conditions": pattern.conditions,
                    "frequency": pattern.frequency,
                    "confidence": pattern.confidence,
                    "support": pattern.support,
                    "lift": pattern.lift,
                    "examples": pattern.examples[:3],
                    "implications": pattern.implications,
                    "mitigation_strategies": self._generate_mitigation_strategies(pattern),
                    "warning_signs": self._extract_warning_signs(pattern),
                    "type": "failure_pattern"
                })
            
            self._pattern_metrics["failure_patterns"] = len(result)
            logger.info(f"Detected {len(result)} failure patterns")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting failure patterns: {str(e)}")
            return []
    
    def match_patterns(self, context: Dict[str, Any]) -> List[PatternMatch]:
        """
        Match current context against known patterns.
        
        Args:
            context: Current situation context
            
        Returns:
            List of pattern matches with confidence scores
        """
        matches = []
        
        try:
            # Get cached patterns
            patterns = self._get_cached_patterns()
            
            for pattern in patterns:
                # Calculate match confidence
                match_confidence = self._calculate_pattern_match_confidence(context, pattern)
                
                if match_confidence > 0.5:  # Significant match
                    # Identify matching conditions
                    matching_conditions = self._identify_matching_conditions(context, pattern)
                    
                    # Generate implications and recommendations
                    implications = self._generate_match_implications(pattern, match_confidence)
                    recommendations = self._generate_match_recommendations(pattern, context)
                    
                    match = PatternMatch(
                        pattern_id=pattern.id,
                        match_confidence=match_confidence,
                        matching_conditions=matching_conditions,
                        implications=implications,
                        recommended_actions=recommendations
                    )
                    
                    matches.append(match)
            
            # Sort by confidence
            matches.sort(key=lambda x: x.match_confidence, reverse=True)
            
            logger.info(f"Found {len(matches)} pattern matches for current context")
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Error matching patterns: {str(e)}")
            return []
    
    # The rest of the implementation continues with all the detailed methods...
    # This is getting quite long, so I'll continue in the next part
    
    def count_patterns_in_timeframe(self, timeframe: timedelta) -> int:
        """Count patterns detected within timeframe."""
        # Placeholder implementation
        return len(self._detected_patterns)
    
    def get_accuracy_metrics(self) -> Dict[str, float]:
        """Get pattern accuracy metrics."""
        return {
            "overall_accuracy": self._pattern_metrics.get("pattern_accuracy", 0.0),
            "success_pattern_accuracy": 0.8,  # Placeholder
            "failure_pattern_accuracy": 0.85  # Placeholder
        }
    
    # ==========================================================================
    # HELPER METHODS (Stub implementations for now)
    # ==========================================================================
    
    def _get_historical_data(self, timeframe: timedelta, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical data for analysis."""
        # Stub implementation
        return []
    
    def _is_successful_outcome(self, data: Dict[str, Any]) -> bool:
        """Determine if outcome was successful."""
        # Stub implementation
        return data.get('outcome_type') == 'success'
    
    def _is_failed_outcome(self, data: Dict[str, Any]) -> bool:
        """Determine if outcome was a failure."""
        # Stub implementation  
        return data.get('outcome_type') == 'failure'
    
    def _group_by_characteristics(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group data by common characteristics."""
        # Stub implementation
        return {}
    
    def _detect_success_patterns_internal(self, data: List[Dict[str, Any]], min_confidence: float) -> List[Pattern]:
        """Internal success pattern detection."""
        # Stub implementation
        return []
    
    def _detect_failure_patterns_internal(self, data: List[Dict[str, Any]], min_confidence: float) -> List[Pattern]:
        """Internal failure pattern detection."""
        # Stub implementation
        return []
    
    def _detect_temporal_patterns(self, data: List[Dict[str, Any]], min_confidence: float) -> List[Pattern]:
        """Detect temporal patterns."""
        # Stub implementation
        return []
    
    def _detect_contextual_patterns(self, data: List[Dict[str, Any]], min_confidence: float) -> List[Pattern]:
        """Detect contextual patterns."""
        # Stub implementation
        return []
    
    def _rank_patterns_by_importance(self, patterns: List[Pattern]) -> List[Pattern]:
        """Rank patterns by importance."""
        # Stub implementation
        return patterns
    
    def _update_pattern_cache(self, patterns: List[Pattern]) -> None:
        """Update pattern cache."""
        # Stub implementation
        pass
    
    def _calculate_confidence_stats(self, patterns: List[Pattern]) -> Dict[str, float]:
        """Calculate confidence statistics."""
        # Stub implementation
        return {"avg_confidence": 0.7, "min_confidence": 0.5, "max_confidence": 0.9}
    
    def _get_total_data_count(self) -> int:
        """Get total data count."""
        # Stub implementation
        return 100
    
    def _get_overall_success_rate(self) -> float:
        """Get overall success rate."""
        # Stub implementation
        return 0.6
    
    def _get_overall_failure_rate(self) -> float:
        """Get overall failure rate."""
        # Stub implementation
        return 0.3
    
    def _generate_mitigation_strategies(self, pattern: Pattern) -> List[str]:
        """Generate mitigation strategies for failure patterns."""
        # Stub implementation
        return ["Implement early warning system", "Develop contingency plan"]
    
    def _extract_warning_signs(self, pattern: Pattern) -> List[str]:
        """Extract warning signs from failure pattern."""
        # Stub implementation
        return ["High time pressure detected", "Inadequate resources"]
    
    def _get_cached_patterns(self) -> List[Pattern]:
        """Get cached patterns."""
        # Stub implementation
        return []
    
    def _calculate_pattern_match_confidence(self, context: Dict[str, Any], pattern: Pattern) -> float:
        """Calculate pattern match confidence."""
        # Stub implementation
        return 0.7
    
    def _identify_matching_conditions(self, context: Dict[str, Any], pattern: Pattern) -> List[str]:
        """Identify matching conditions."""
        # Stub implementation
        return ["condition1", "condition2"]
    
    def _generate_match_implications(self, pattern: Pattern, confidence: float) -> List[str]:
        """Generate implications for pattern match."""
        # Stub implementation
        return [f"Pattern match with {confidence:.1%} confidence"]
    
    def _generate_match_recommendations(self, pattern: Pattern, context: Dict[str, Any]) -> List[str]:
        """Generate recommendations for pattern match."""
        # Stub implementation
        return ["Follow success pattern", "Avoid failure conditions"]
    
    def _describe_conditions(self, conditions: List[Dict[str, Any]]) -> str:
        """Generate human-readable description of conditions."""
        # Stub implementation
        return "conditions description"
    
    def _detect_sequence_patterns(self, data: List[Dict[str, Any]], pattern_type: PatternType) -> List[Pattern]:
        """Detect sequence patterns in data."""
        # Stub implementation
        return []
    
    def _detect_correlation_patterns(self, data: List[Dict[str, Any]], pattern_type: PatternType) -> List[Pattern]:
        """Detect correlation patterns in data."""
        # Stub implementation
        return []
