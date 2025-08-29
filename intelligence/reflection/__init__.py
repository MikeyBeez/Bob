"""
Reflection submodules for the ReflectionEngine.

This package contains all the specialized submodules that implement
the reflection engine's functionality:

- outcome_analyzer: Analyzes action outcomes and decision quality
- pattern_detector: Detects success/failure/temporal patterns
- insight_generator: Generates actionable insights
- learning_engine: Handles continuous learning and model updates
- memory_integrator: Integrates with memory systems for storage/retrieval
- confidence_calibrator: Calibrates confidence levels based on accuracy
"""

# Import all submodules to make them available to the parent reflection_engine
from .outcome_analyzer import OutcomeAnalyzer
from .pattern_detector import PatternDetector
from .insight_generator import InsightGenerator
from .learning_engine import LearningEngine
from .memory_integrator import MemoryIntegrator
from .confidence_calibrator import ConfidenceCalibrator

__all__ = [
    'OutcomeAnalyzer',
    'PatternDetector', 
    'InsightGenerator',
    'LearningEngine',
    'MemoryIntegrator',
    'ConfidenceCalibrator'
]
