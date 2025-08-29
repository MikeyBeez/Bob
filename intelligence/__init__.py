"""
Bob Intelligence System - Core Intelligence Layer

This package contains the main intelligence components for Bob's LLM-as-Kernel system:

- reflection_engine: Advanced reflection and learning system with 6 specialized submodules
- context_assembler: Context assembly and management (completed in previous phase)
- Additional intelligence modules (future expansion)

The intelligence layer implements Bob's canonical intelligence loop:
Perception → Analysis → Reflection → Learning → Action
"""

# Import core types and classes that submodules need
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Define core data structures used across intelligence modules
class ReflectionType(Enum):
    """Types of reflections the system can perform."""
    ACTION_OUTCOME = "action_outcome"
    DECISION_QUALITY = "decision_quality"
    PATTERN_RECOGNITION = "pattern_recognition"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ERROR_ANALYSIS = "error_analysis"

@dataclass
class Reflection:
    """Structured representation of a reflection."""
    id: str
    type: ReflectionType
    timestamp: datetime
    context: Dict[str, Any]
    analysis: Dict[str, Any]
    insights: List[str]
    lessons_learned: List[str]
    confidence: float
    actionable_items: List[str]
    related_reflections: Optional[List[str]] = None

@dataclass
class Insight:
    """Actionable insight from reflection analysis."""
    id: str
    category: str
    description: str
    evidence: List[str]
    confidence: float
    actionable: bool
    priority: int
    expiration_date: Optional[datetime] = None

@dataclass
class PatternAnalysis:
    """Analysis of detected patterns."""
    pattern_id: str
    pattern_type: str
    frequency: int
    confidence: float
    description: str
    examples: List[Dict[str, Any]]
    implications: List[str]
    recommendations: List[str]

# Import main intelligence modules (after defining core types)
from .reflection_engine import ReflectionEngine

# Export main components
__all__ = [
    'ReflectionEngine',
    'Reflection',
    'ReflectionType', 
    'Insight',
    'PatternAnalysis'
]
