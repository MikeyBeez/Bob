"""
reflection_engine.py - Clean API for intelligent reflection and learning

This is the main API module for Bob's reflection system.
It analyzes outcomes, extracts patterns, and generates insights
to improve future decision-making. Implementation details are in submodules.
Following the modular pattern established in Phase 1.

API DOCUMENTATION:
==================

Core Methods:
-------------
• reflect_on_action(action_data) -> Reflection
    Analyze a completed action and extract lessons learned
    
• reflect_on_outcome(outcome_data) -> Reflection
    Analyze an outcome against expectations and generate insights
    
• analyze_patterns(timeframe, domain) -> PatternAnalysis
    Identify recurring patterns across actions and outcomes
    
• generate_insights(context) -> List[Insight]
    Generate actionable insights from accumulated reflections
    
• learn_from_feedback(feedback_data) -> LearningUpdate
    Incorporate external feedback into the learning system

Pattern Detection:
------------------
• detect_success_patterns() -> List[SuccessPattern]
    Identify what consistently leads to successful outcomes
    
• detect_failure_patterns() -> List[FailurePattern]
    Identify what consistently leads to poor outcomes
    
• analyze_decision_quality(decision_data) -> DecisionAnalysis
    Evaluate the quality of past decisions and their outcomes

Memory Integration:
-------------------
• store_reflection(reflection) -> bool
    Store reflection in long-term memory with proper indexing
    
• retrieve_relevant_reflections(context) -> List[Reflection]
    Get relevant past reflections for current situation
    
• build_learning_graph() -> LearningGraph
    Construct a graph of interconnected learnings

Continuous Learning:
--------------------
• update_mental_models(new_data) -> bool
    Update internal models based on new evidence
    
• calibrate_confidence(domain) -> ConfidenceCalibration
    Adjust confidence levels based on historical accuracy
    
• suggest_experiments() -> List[Experiment]
    Suggest experiments to test hypotheses and improve understanding

Metrics & Reporting:
--------------------
• get_learning_metrics() -> Dict[str, Any]
    Get comprehensive metrics on learning progress
    
• generate_reflection_report(timeframe) -> ReflectionReport
    Generate detailed report on reflections and insights
"""

from typing import Any, Dict, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json

# Import implementation modules
from .reflection.outcome_analyzer import OutcomeAnalyzer
from .reflection.pattern_detector import PatternDetector
from .reflection.insight_generator import InsightGenerator
from .reflection.learning_engine import LearningEngine
from .reflection.memory_integrator import MemoryIntegrator
from .reflection.confidence_calibrator import ConfidenceCalibrator


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
    related_reflections: List[str] = None


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


class ReflectionEngine:
    """
    Clean API for intelligent reflection and continuous learning.
    
    This system analyzes past actions, decisions, and outcomes to extract
    patterns, generate insights, and improve future performance. It forms
    the learning component of Bob's intelligence loop.
    """
    
    def __init__(self,
                 db_core: Optional[Any] = None,
                 fs_core: Optional[Any] = None,
                 memory_system: Optional[Any] = None,
                 learning_rate: float = 0.1,
                 confidence_threshold: float = 0.7):
        """
        Initialize ReflectionEngine with configuration.
        
        Args:
            db_core: DatabaseCore instance for accessing stored data
            fs_core: FileSystemCore instance for file operations  
            memory_system: Memory system for storing/retrieving reflections
            learning_rate: Rate at which the system adapts to new information
            confidence_threshold: Minimum confidence for actionable insights
        """
        # Store core dependencies
        self.db_core = db_core
        self.fs_core = fs_core
        self.memory_system = memory_system
        self.learning_rate = learning_rate
        self.confidence_threshold = confidence_threshold
        
        # Initialize components
        self.outcome_analyzer = OutcomeAnalyzer(db_core)
        self.pattern_detector = PatternDetector(db_core, learning_rate)
        self.insight_generator = InsightGenerator(confidence_threshold)
        self.learning_engine = LearningEngine(learning_rate)
        self.memory_integrator = MemoryIntegrator(memory_system)
        self.confidence_calibrator = ConfidenceCalibrator()
        
        # Internal state
        self._reflection_cache = {}
        self._pattern_cache = {}
        self._learning_metrics = {
            "total_reflections": 0,
            "actionable_insights": 0,
            "patterns_detected": 0,
            "accuracy_improvements": 0,
            "confidence_calibrations": 0
        }
    
    # =============================================================================
    # CORE REFLECTION METHODS
    # =============================================================================
    
    def reflect_on_action(self, action_data: Dict[str, Any]) -> Reflection:
        """
        Analyze a completed action and extract lessons learned.
        
        Args:
            action_data: Dictionary containing action details, context, and outcome
            
        Returns:
            Reflection object with analysis, insights, and lessons learned
        """
        return self.outcome_analyzer.analyze_action_outcome(
            action_data,
            self._get_reflection_context(action_data)
        )
    
    def reflect_on_outcome(self, outcome_data: Dict[str, Any]) -> Reflection:
        """
        Analyze an outcome against expectations and generate insights.
        
        Args:
            outcome_data: Dictionary containing expected vs actual outcomes
            
        Returns:
            Reflection object with outcome analysis and improvement suggestions
        """
        return self.outcome_analyzer.analyze_outcome_deviation(
            outcome_data,
            self._get_historical_expectations(outcome_data.get('domain'))
        )
    
    def analyze_patterns(self, 
                        timeframe: Optional[timedelta] = None,
                        domain: Optional[str] = None) -> PatternAnalysis:
        """
        Identify recurring patterns across actions and outcomes.
        
        Args:
            timeframe: Time period to analyze (default: last 30 days)
            domain: Specific domain to focus on (optional)
            
        Returns:
            PatternAnalysis with detected patterns and their implications
        """
        timeframe = timeframe or timedelta(days=30)
        
        return self.pattern_detector.detect_patterns(
            timeframe=timeframe,
            domain=domain,
            min_confidence=self.confidence_threshold
        )
    
    def generate_insights(self, context: Dict[str, Any]) -> List[Insight]:
        """
        Generate actionable insights from accumulated reflections.
        
        Args:
            context: Current context for which insights are needed
            
        Returns:
            List of prioritized, actionable insights
        """
        return self.insight_generator.generate_contextual_insights(
            context=context,
            historical_data=self._get_relevant_reflections(context),
            confidence_threshold=self.confidence_threshold
        )
    
    def learn_from_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Incorporate external feedback into the learning system.
        
        Args:
            feedback_data: Feedback on past actions/decisions
            
        Returns:
            True if feedback was successfully incorporated
        """
        return self.learning_engine.incorporate_feedback(
            feedback_data,
            self._get_related_reflections(feedback_data)
        )
    
    # =============================================================================
    # PATTERN DETECTION METHODS
    # =============================================================================
    
    def detect_success_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify what consistently leads to successful outcomes.
        
        Returns:
            List of success patterns with confidence scores
        """
        return self.pattern_detector.detect_success_patterns(
            min_frequency=3,
            min_confidence=self.confidence_threshold
        )
    
    def detect_failure_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify what consistently leads to poor outcomes.
        
        Returns:
            List of failure patterns with mitigation strategies
        """
        return self.pattern_detector.detect_failure_patterns(
            min_frequency=2,  # Failures are more important to catch early
            min_confidence=0.6  # Slightly lower threshold for failures
        )
    
    def analyze_decision_quality(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the quality of past decisions and their outcomes.
        
        Args:
            decision_data: Information about the decision and its results
            
        Returns:
            Decision analysis with quality scores and improvement suggestions
        """
        return self.outcome_analyzer.analyze_decision_quality(
            decision_data,
            self._get_decision_history(decision_data.get('type'))
        )
    
    # =============================================================================
    # MEMORY INTEGRATION METHODS
    # =============================================================================
    
    def store_reflection(self, reflection: Reflection) -> bool:
        """
        Store reflection in long-term memory with proper indexing.
        
        Args:
            reflection: Reflection object to store
            
        Returns:
            True if successfully stored
        """
        success = self.memory_integrator.store_reflection(reflection)
        if success:
            self._learning_metrics["total_reflections"] += 1
        return success
    
    def retrieve_relevant_reflections(self, context: Dict[str, Any]) -> List[Reflection]:
        """
        Get relevant past reflections for current situation.
        
        Args:
            context: Current context to find relevant reflections for
            
        Returns:
            List of relevant reflections sorted by relevance
        """
        return self.memory_integrator.retrieve_relevant_reflections(
            context,
            max_results=10,
            min_relevance=0.5
        )
    
    def build_learning_graph(self) -> Dict[str, Any]:
        """
        Construct a graph of interconnected learnings.
        
        Returns:
            Learning graph showing relationships between insights
        """
        return self.memory_integrator.build_learning_graph(
            include_patterns=True,
            include_insights=True,
            max_depth=3
        )
    
    # =============================================================================
    # CONTINUOUS LEARNING METHODS
    # =============================================================================
    
    def update_mental_models(self, new_data: Dict[str, Any]) -> bool:
        """
        Update internal models based on new evidence.
        
        Args:
            new_data: New evidence to incorporate into models
            
        Returns:
            True if models were successfully updated
        """
        return self.learning_engine.update_models(
            new_data,
            learning_rate=self.learning_rate
        )
    
    def calibrate_confidence(self, domain: str) -> Dict[str, float]:
        """
        Adjust confidence levels based on historical accuracy.
        
        Args:
            domain: Domain to calibrate confidence for
            
        Returns:
            Confidence calibration results
        """
        calibration = self.confidence_calibrator.calibrate_domain_confidence(
            domain,
            self._get_domain_history(domain)
        )
        
        if calibration:
            self._learning_metrics["confidence_calibrations"] += 1
            
        return calibration
    
    def suggest_experiments(self) -> List[Dict[str, Any]]:
        """
        Suggest experiments to test hypotheses and improve understanding.
        
        Returns:
            List of suggested experiments with expected outcomes
        """
        return self.learning_engine.suggest_experiments(
            current_knowledge=self._get_current_knowledge_state(),
            uncertainty_areas=self._identify_uncertainty_areas()
        )
    
    # =============================================================================
    # METRICS & REPORTING METHODS
    # =============================================================================
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics on learning progress.
        
        Returns:
            Dictionary with detailed learning metrics
        """
        return {
            **self._learning_metrics,
            "pattern_accuracy": self.pattern_detector.get_accuracy_metrics(),
            "insight_effectiveness": self.insight_generator.get_effectiveness_metrics(),
            "confidence_accuracy": self.confidence_calibrator.get_calibration_metrics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_reflection_report(self, 
                                 timeframe: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Generate detailed report on reflections and insights.
        
        Args:
            timeframe: Time period to report on (default: last 7 days)
            
        Returns:
            Comprehensive reflection report
        """
        timeframe = timeframe or timedelta(days=7)
        
        return {
            "timeframe": str(timeframe),
            "summary": self._generate_summary_stats(timeframe),
            "top_patterns": self.detect_success_patterns()[:5],
            "key_insights": self.generate_insights({"timeframe": timeframe})[:10],
            "learning_progress": self.get_learning_metrics(),
            "recommendations": self._generate_recommendations(timeframe),
            "generated_at": datetime.now().isoformat()
        }
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _get_reflection_context(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant context for reflection analysis."""
        return {
            "recent_actions": self._get_recent_actions(limit=5),
            "similar_contexts": self._find_similar_contexts(action_data),
            "current_goals": self._get_current_goals(),
            "constraints": self._get_active_constraints()
        }
    
    def _get_historical_expectations(self, domain: Optional[str]) -> List[Dict[str, Any]]:
        """Get historical expectations for outcome analysis."""
        if not domain:
            return []
        return self.memory_integrator.get_domain_expectations(domain)
    
    def _get_relevant_reflections(self, context: Dict[str, Any]) -> List[Reflection]:
        """Get reflections relevant to current context."""
        return self.retrieve_relevant_reflections(context)
    
    def _get_related_reflections(self, feedback_data: Dict[str, Any]) -> List[Reflection]:
        """Get reflections related to feedback."""
        return self.memory_integrator.find_related_reflections(feedback_data)
    
    def _get_decision_history(self, decision_type: Optional[str]) -> List[Dict[str, Any]]:
        """Get history of similar decisions."""
        if not decision_type:
            return []
        return self.memory_integrator.get_decision_history(decision_type)
    
    def _get_domain_history(self, domain: str) -> List[Dict[str, Any]]:
        """Get historical data for a specific domain."""
        return self.memory_integrator.get_domain_history(domain)
    
    def _get_current_knowledge_state(self) -> Dict[str, Any]:
        """Get current state of accumulated knowledge."""
        return {
            "patterns": len(self._pattern_cache),
            "reflections": self._learning_metrics["total_reflections"],
            "insights": self._learning_metrics["actionable_insights"],
            "domains": self.memory_integrator.get_active_domains()
        }
    
    def _identify_uncertainty_areas(self) -> List[str]:
        """Identify areas with high uncertainty or low confidence."""
        return self.confidence_calibrator.identify_uncertainty_areas()
    
    def _get_recent_actions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent actions for context."""
        if self.db_core:
            return self.db_core.get_recent_actions(limit=limit)
        return []
    
    def _find_similar_contexts(self, action_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical contexts."""
        return self.memory_integrator.find_similar_contexts(action_data)
    
    def _get_current_goals(self) -> List[str]:
        """Get current active goals."""
        if self.db_core:
            return self.db_core.get_active_goals()
        return []
    
    def _get_active_constraints(self) -> List[str]:
        """Get current active constraints."""
        if self.db_core:
            return self.db_core.get_active_constraints()
        return []
    
    def _generate_summary_stats(self, timeframe: timedelta) -> Dict[str, Any]:
        """Generate summary statistics for reporting."""
        return {
            "reflections_count": self._count_reflections_in_timeframe(timeframe),
            "patterns_detected": self._count_patterns_in_timeframe(timeframe),
            "insights_generated": self._count_insights_in_timeframe(timeframe),
            "accuracy_improvement": self._calculate_accuracy_improvement(timeframe)
        }
    
    def _generate_recommendations(self, timeframe: timedelta) -> List[str]:
        """Generate recommendations based on recent analysis."""
        recommendations = []
        
        # Add pattern-based recommendations
        patterns = self.detect_success_patterns()
        if patterns:
            recommendations.append("Continue leveraging identified success patterns")
            
        # Add failure pattern warnings
        failures = self.detect_failure_patterns()
        if failures:
            recommendations.append("Address identified failure patterns immediately")
            
        # Add learning recommendations
        experiments = self.suggest_experiments()
        if experiments:
            recommendations.extend([exp["recommendation"] for exp in experiments[:3]])
            
        return recommendations
    
    def _count_reflections_in_timeframe(self, timeframe: timedelta) -> int:
        """Count reflections within timeframe."""
        return self.memory_integrator.count_reflections_in_timeframe(timeframe)
    
    def _count_patterns_in_timeframe(self, timeframe: timedelta) -> int:
        """Count patterns detected within timeframe.""" 
        return self.pattern_detector.count_patterns_in_timeframe(timeframe)
    
    def _count_insights_in_timeframe(self, timeframe: timedelta) -> int:
        """Count insights generated within timeframe."""
        return self.insight_generator.count_insights_in_timeframe(timeframe)
    
    def _calculate_accuracy_improvement(self, timeframe: timedelta) -> float:
        """Calculate accuracy improvement over timeframe."""
        return self.confidence_calibrator.calculate_accuracy_improvement(timeframe)
