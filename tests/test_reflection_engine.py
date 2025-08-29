"""
test_reflection_engine.py - Comprehensive tests for ReflectionEngine

This file serves as both a test suite AND API documentation through tests.
Each test demonstrates how to use the ReflectionEngine API and validates
that the implementation meets the specified behavior.

Following the modular testing pattern from Phase 1 - same proven approach
as test_context_assembler.py which achieved 100% success.

TESTING ARCHITECTURE:
====================

1. Main ReflectionEngine API Tests
   - Core reflection methods
   - Pattern detection integration
   - Memory integration
   - Learning system integration

2. Submodule Integration Tests
   - OutcomeAnalyzer integration
   - PatternDetector integration  
   - InsightGenerator integration
   - LearningEngine integration
   - MemoryIntegrator integration
   - ConfidenceCalibrator integration

3. End-to-End Workflow Tests
   - Complete reflection workflows
   - Cross-module communication
   - Error handling and recovery
   - Performance and scalability
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os
from typing import Dict, List, Any
import json

# Add the Bob directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from intelligence.reflection_engine import (
    ReflectionEngine, ReflectionType, Reflection, ActionData, OutcomeData,
    PatternAnalysis, Insight, LearningUpdate, SuccessPattern, FailurePattern,
    DecisionAnalysis, LearningGraph, ConfidenceCalibration, Experiment,
    ReflectionReport
)

# Import submodules for direct testing
from intelligence.reflection.outcome_analyzer import OutcomeAnalyzer
from intelligence.reflection.pattern_detector import PatternDetector
from intelligence.reflection.insight_generator import InsightGenerator
from intelligence.reflection.learning_engine import LearningEngine
from intelligence.reflection.memory_integrator import MemoryIntegrator
from intelligence.reflection.confidence_calibrator import ConfidenceCalibrator


class TestReflectionEngineAPI:
    """
    Test suite demonstrating the ReflectionEngine API.
    
    These tests serve as living documentation of how to use
    the ReflectionEngine class and what behavior to expect.
    
    Following the same proven pattern as test_context_assembler.py
    """

    @pytest.fixture
    def mock_db_core(self):
        """Mock database core for testing."""
        mock_db = Mock()
        mock_db.query = AsyncMock()
        mock_db.store_reflection = AsyncMock(return_value=True)
        mock_db.get_reflections = AsyncMock(return_value=[])
        mock_db.store_pattern = AsyncMock(return_value=True)
        mock_db.get_patterns = AsyncMock(return_value=[])
        mock_db.store_insight = AsyncMock(return_value=True)
        mock_db.get_insights = AsyncMock(return_value=[])
        return mock_db

    @pytest.fixture
    def mock_fs_core(self):
        """Mock filesystem core for testing."""
        mock_fs = Mock()
        mock_fs.read_file = AsyncMock()
        mock_fs.write_file = AsyncMock()
        mock_fs.list_directory = AsyncMock()
        return mock_fs

    @pytest.fixture
    def mock_ollama_client(self):
        """Mock Ollama client for testing."""
        mock_ollama = Mock()
        mock_ollama.generate = AsyncMock()
        mock_ollama.analyze = AsyncMock()
        return mock_ollama

    @pytest.fixture
    async def reflection_engine(self, mock_db_core, mock_fs_core, mock_ollama_client):
        """Create a ReflectionEngine instance with mocked dependencies."""
        engine = ReflectionEngine(
            db_core=mock_db_core,
            fs_core=mock_fs_core,
            ollama_client=mock_ollama_client
        )
        await engine.initialize()
        return engine

    @pytest.fixture
    def sample_action_data(self):
        """Sample action data for testing."""
        return ActionData(
            id="action_001",
            type="file_operation",
            description="Read configuration file",
            context={"file_path": "/path/to/config.json", "purpose": "system_init"},
            timestamp=datetime.now(),
            duration=0.5,
            success=True,
            error=None,
            metadata={"complexity": "low", "criticality": "medium"}
        )

    @pytest.fixture
    def sample_outcome_data(self):
        """Sample outcome data for testing."""
        return OutcomeData(
            id="outcome_001",
            action_id="action_001",
            expected_result="Configuration loaded successfully",
            actual_result="Configuration loaded successfully",
            success=True,
            deviation_score=0.0,
            impact="positive",
            timestamp=datetime.now(),
            context={"system_state": "initialized", "performance": "optimal"},
            metadata={"user_satisfaction": "high", "efficiency": 0.95}
        )

    # ================================================
    # CORE API TESTS - Main ReflectionEngine Methods
    # ================================================

    @pytest.mark.asyncio
    async def test_reflect_on_action_basic(self, reflection_engine, sample_action_data):
        """
        Test basic action reflection functionality.
        
        API Usage:
            reflection = await engine.reflect_on_action(action_data)
        
        Expected behavior:
            - Returns a Reflection object with proper structure
            - Analyzes action outcome and quality
            - Generates initial insights
            - Stores reflection for future reference
        """
        # Execute reflection
        reflection = await reflection_engine.reflect_on_action(sample_action_data)
        
        # Validate reflection structure
        assert isinstance(reflection, Reflection)
        assert reflection.id is not None
        assert reflection.type == ReflectionType.ACTION_OUTCOME
        assert reflection.action_id == sample_action_data.id
        assert reflection.timestamp is not None
        
        # Validate analysis was performed
        assert reflection.analysis is not None
        assert "outcome_quality" in reflection.analysis
        assert "decision_factors" in reflection.analysis
        
        # Validate insights were generated
        assert len(reflection.insights) > 0
        assert all(isinstance(insight, str) for insight in reflection.insights)
        
        # Validate metadata
        assert reflection.confidence_score >= 0.0
        assert reflection.confidence_score <= 1.0
        assert reflection.learning_value > 0.0

    @pytest.mark.asyncio
    async def test_reflect_on_outcome_comprehensive(self, reflection_engine, sample_outcome_data):
        """
        Test comprehensive outcome reflection.
        
        API Usage:
            reflection = await engine.reflect_on_outcome(outcome_data)
        
        Expected behavior:
            - Analyzes outcome vs expectations
            - Calculates deviation and impact
            - Identifies contributing factors
            - Suggests improvements
        """
        # Execute outcome reflection
        reflection = await reflection_engine.reflect_on_outcome(sample_outcome_data)
        
        # Validate reflection type and structure
        assert reflection.type == ReflectionType.DECISION_QUALITY
        assert reflection.outcome_id == sample_outcome_data.id
        
        # Validate outcome analysis
        analysis = reflection.analysis
        assert "deviation_analysis" in analysis
        assert "impact_assessment" in analysis
        assert "contributing_factors" in analysis
        
        # Validate deviation scoring
        assert analysis["deviation_analysis"]["score"] == sample_outcome_data.deviation_score
        assert analysis["deviation_analysis"]["severity"] in ["low", "medium", "high"]
        
        # Validate improvement suggestions
        assert "improvement_suggestions" in analysis
        assert isinstance(analysis["improvement_suggestions"], list)

    @pytest.mark.asyncio
    async def test_analyze_patterns_timeframe(self, reflection_engine):
        """
        Test pattern analysis across timeframes.
        
        API Usage:
            patterns = await engine.analyze_patterns(timeframe="7d", domain="file_ops")
        
        Expected behavior:
            - Analyzes patterns within specified timeframe
            - Groups patterns by type and domain
            - Calculates pattern strength and frequency
            - Identifies emerging vs established patterns
        """
        # Test different timeframes
        timeframes = ["1h", "24h", "7d", "30d", "all"]
        
        for timeframe in timeframes:
            pattern_analysis = await reflection_engine.analyze_patterns(
                timeframe=timeframe, 
                domain="file_operations"
            )
            
            # Validate pattern analysis structure
            assert isinstance(pattern_analysis, PatternAnalysis)
            assert pattern_analysis.timeframe == timeframe
            assert pattern_analysis.domain == "file_operations"
            assert isinstance(pattern_analysis.patterns, list)
            
            # Validate pattern metadata
            assert hasattr(pattern_analysis, 'total_patterns')
            assert hasattr(pattern_analysis, 'confidence_score')
            assert hasattr(pattern_analysis, 'analysis_timestamp')

    @pytest.mark.asyncio
    async def test_generate_insights_contextual(self, reflection_engine):
        """
        Test contextual insight generation.
        
        API Usage:
            insights = await engine.generate_insights(context)
        
        Expected behavior:
            - Generates context-relevant insights
            - Prioritizes insights by impact and relevance
            - Provides actionable recommendations
            - Categorizes insights by type
        """
        # Test contexts
        test_contexts = [
            {"domain": "system_performance", "focus": "optimization"},
            {"domain": "error_handling", "focus": "prevention"},
            {"domain": "user_experience", "focus": "improvement"},
            {"domain": "resource_management", "focus": "efficiency"}
        ]
        
        for context in test_contexts:
            insights = await reflection_engine.generate_insights(context)
            
            # Validate insights structure
            assert isinstance(insights, list)
            assert all(isinstance(insight, Insight) for insight in insights)
            
            if insights:  # If insights were generated
                insight = insights[0]
                assert hasattr(insight, 'title')
                assert hasattr(insight, 'description')
                assert hasattr(insight, 'category')
                assert hasattr(insight, 'priority')
                assert hasattr(insight, 'actionable_steps')
                assert insight.domain == context["domain"]

    # ================================================
    # SUBMODULE INTEGRATION TESTS
    # ================================================

    @pytest.mark.asyncio
    async def test_outcome_analyzer_integration(self, reflection_engine, sample_outcome_data):
        """
        Test OutcomeAnalyzer submodule integration.
        
        Validates that the outcome analyzer correctly:
        - Processes outcome data
        - Calculates quality metrics
        - Identifies deviation patterns
        - Integrates with main reflection engine
        """
        # Get outcome analyzer instance
        analyzer = reflection_engine._outcome_analyzer
        assert isinstance(analyzer, OutcomeAnalyzer)
        
        # Test direct analyzer functionality
        analysis = await analyzer.analyze_outcome(sample_outcome_data)
        
        # Validate analysis structure
        assert "quality_score" in analysis
        assert "deviation_metrics" in analysis
        assert "improvement_areas" in analysis
        
        # Validate quality scoring
        quality_score = analysis["quality_score"]
        assert 0.0 <= quality_score <= 1.0
        
        # Test integration with reflection engine
        reflection = await reflection_engine.reflect_on_outcome(sample_outcome_data)
        assert reflection.analysis["outcome_quality"] == quality_score

    @pytest.mark.asyncio
    async def test_pattern_detector_integration(self, reflection_engine):
        """
        Test PatternDetector submodule integration.
        
        Validates pattern detection across:
        - Success patterns
        - Failure patterns  
        - Temporal patterns
        - Contextual patterns
        """
        # Get pattern detector instance
        detector = reflection_engine._pattern_detector
        assert isinstance(detector, PatternDetector)
        
        # Test success pattern detection
        success_patterns = await detector.detect_success_patterns(
            timeframe="7d", min_frequency=2
        )
        assert isinstance(success_patterns, list)
        assert all(isinstance(p, SuccessPattern) for p in success_patterns)
        
        # Test failure pattern detection
        failure_patterns = await detector.detect_failure_patterns(
            timeframe="7d", min_frequency=2
        )
        assert isinstance(failure_patterns, list)
        assert all(isinstance(p, FailurePattern) for p in failure_patterns)
        
        # Test temporal pattern analysis
        temporal_analysis = await detector.analyze_temporal_patterns(domain="all")
        assert "peak_hours" in temporal_analysis
        assert "trend_analysis" in temporal_analysis

    @pytest.mark.asyncio
    async def test_insight_generator_integration(self, reflection_engine):
        """
        Test InsightGenerator submodule integration.
        
        Validates insight generation:
        - From patterns
        - From reflections
        - With prioritization
        - With categorization
        """
        # Get insight generator instance
        generator = reflection_engine._insight_generator
        assert isinstance(generator, InsightGenerator)
        
        # Test insight generation from sample data
        sample_patterns = [
            {"type": "success", "frequency": 10, "context": "file_operations"},
            {"type": "failure", "frequency": 3, "context": "network_operations"}
        ]
        
        insights = await generator.generate_insights_from_patterns(sample_patterns)
        assert isinstance(insights, list)
        
        if insights:
            insight = insights[0]
            assert hasattr(insight, 'category')
            assert hasattr(insight, 'priority')
            assert hasattr(insight, 'actionable_steps')

    @pytest.mark.asyncio
    async def test_learning_engine_integration(self, reflection_engine):
        """
        Test LearningEngine submodule integration.
        
        Validates continuous learning:
        - Model updates from feedback
        - Hypothesis testing
        - Experiment suggestion
        - Performance tracking
        """
        # Get learning engine instance
        learner = reflection_engine._learning_engine
        assert isinstance(learner, LearningEngine)
        
        # Test feedback integration
        feedback_data = {
            "reflection_id": "test_001",
            "user_rating": 4.5,
            "accuracy": 0.9,
            "usefulness": 0.8,
            "feedback_text": "Good analysis, minor improvements needed"
        }
        
        learning_update = await learner.learn_from_feedback(feedback_data)
        assert isinstance(learning_update, LearningUpdate)
        assert learning_update.model_updated is True
        assert learning_update.confidence_adjustment != 0
        
        # Test experiment suggestion
        experiments = await learner.suggest_experiments(domain="file_operations")
        assert isinstance(experiments, list)
        assert all(isinstance(exp, Experiment) for exp in experiments)

    @pytest.mark.asyncio
    async def test_memory_integrator_integration(self, reflection_engine):
        """
        Test MemoryIntegrator submodule integration.
        
        Validates memory operations:
        - Reflection storage
        - Pattern storage
        - Insight storage
        - Retrieval with context
        """
        # Get memory integrator instance
        memory = reflection_engine._memory_integrator
        assert isinstance(memory, MemoryIntegrator)
        
        # Test reflection storage
        test_reflection = Reflection(
            id="test_refl_001",
            type=ReflectionType.ACTION_OUTCOME,
            action_id="test_action",
            timestamp=datetime.now(),
            analysis={"test": "data"},
            insights=["test insight"],
            confidence_score=0.8,
            learning_value=0.7
        )
        
        stored = await memory.store_reflection(test_reflection)
        assert stored is True
        
        # Test retrieval with context
        context = {"domain": "testing", "type": "action_outcome"}
        retrieved = await memory.retrieve_relevant_reflections(context, limit=10)
        assert isinstance(retrieved, list)

    @pytest.mark.asyncio
    async def test_confidence_calibrator_integration(self, reflection_engine):
        """
        Test ConfidenceCalibrator submodule integration.
        
        Validates confidence calibration:
        - Historical accuracy tracking
        - Confidence adjustment
        - Calibration methods
        - Domain-specific calibration
        """
        # Get confidence calibrator instance
        calibrator = reflection_engine._confidence_calibrator
        assert isinstance(calibrator, ConfidenceCalibrator)
        
        # Test confidence calibration
        domain = "file_operations"
        calibration = await calibrator.calibrate_confidence(domain)
        
        assert isinstance(calibration, ConfidenceCalibration)
        assert calibration.domain == domain
        assert 0.0 <= calibration.adjusted_confidence <= 1.0
        assert calibration.historical_accuracy >= 0.0
        assert calibration.calibration_method in ["platt", "isotonic", "beta", "temperature"]

    # ================================================
    # END-TO-END WORKFLOW TESTS
    # ================================================

    @pytest.mark.asyncio
    async def test_complete_reflection_workflow(self, reflection_engine, sample_action_data, sample_outcome_data):
        """
        Test complete end-to-end reflection workflow.
        
        Workflow:
        1. Reflect on action
        2. Reflect on outcome
        3. Detect patterns
        4. Generate insights
        5. Learn from feedback
        6. Update confidence
        """
        # Step 1: Reflect on action
        action_reflection = await reflection_engine.reflect_on_action(sample_action_data)
        assert action_reflection is not None
        
        # Step 2: Reflect on outcome
        outcome_reflection = await reflection_engine.reflect_on_outcome(sample_outcome_data)
        assert outcome_reflection is not None
        
        # Step 3: Detect patterns
        patterns = await reflection_engine.analyze_patterns("1h", "file_operations")
        assert patterns is not None
        
        # Step 4: Generate insights
        insights = await reflection_engine.generate_insights({"domain": "file_operations"})
        assert isinstance(insights, list)
        
        # Step 5: Learn from feedback
        feedback = {
            "reflection_id": action_reflection.id,
            "user_rating": 4.0,
            "accuracy": 0.85
        }
        learning_update = await reflection_engine.learn_from_feedback(feedback)
        assert learning_update is not None
        
        # Step 6: Update confidence
        calibration = await reflection_engine._confidence_calibrator.calibrate_confidence("file_operations")
        assert calibration is not None

    @pytest.mark.asyncio
    async def test_error_handling_resilience(self, reflection_engine):
        """
        Test error handling and system resilience.
        
        Tests recovery from:
        - Invalid input data
        - Database errors
        - Analysis failures
        - Memory errors
        """
        # Test invalid action data
        with pytest.raises((ValueError, TypeError)):
            await reflection_engine.reflect_on_action(None)
        
        # Test invalid outcome data
        with pytest.raises((ValueError, TypeError)):
            await reflection_engine.reflect_on_outcome("invalid")
        
        # Test invalid timeframe
        patterns = await reflection_engine.analyze_patterns("invalid_timeframe", "test")
        # Should handle gracefully and return empty or default patterns
        assert patterns is not None

    @pytest.mark.asyncio
    async def test_performance_metrics(self, reflection_engine):
        """
        Test performance metrics and reporting.
        
        Validates:
        - Learning metrics calculation
        - Performance tracking
        - Report generation
        - System statistics
        """
        # Get learning metrics
        metrics = await reflection_engine.get_learning_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_reflections" in metrics
        assert "pattern_detection_accuracy" in metrics
        assert "insight_generation_rate" in metrics
        assert "confidence_calibration_score" in metrics
        
        # Generate reflection report
        report = await reflection_engine.generate_reflection_report("7d")
        
        assert isinstance(report, ReflectionReport)
        assert report.timeframe == "7d"
        assert hasattr(report, 'summary_statistics')
        assert hasattr(report, 'key_insights')
        assert hasattr(report, 'pattern_analysis')
        assert hasattr(report, 'learning_progress')

    # ================================================
    # CROSS-MODULE COMMUNICATION TESTS
    # ================================================

    @pytest.mark.asyncio
    async def test_submodule_communication(self, reflection_engine):
        """
        Test communication between submodules.
        
        Validates:
        - Data flow between modules
        - Shared state management
        - Event propagation
        - Coordination mechanisms
        """
        # Test pattern detector -> insight generator communication
        patterns = await reflection_engine._pattern_detector.detect_success_patterns("24h", 1)
        insights = await reflection_engine._insight_generator.generate_insights_from_patterns(patterns)
        
        # Validate that insights were generated from patterns
        assert isinstance(insights, list)
        
        # Test outcome analyzer -> learning engine communication
        sample_outcome = OutcomeData(
            id="comm_test_001",
            action_id="comm_action_001",
            expected_result="test",
            actual_result="test",
            success=True,
            deviation_score=0.1,
            impact="positive",
            timestamp=datetime.now(),
            context={},
            metadata={}
        )
        
        analysis = await reflection_engine._outcome_analyzer.analyze_outcome(sample_outcome)
        learning_update = await reflection_engine._learning_engine.update_mental_models(analysis)
        
        assert learning_update is not None

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, reflection_engine):
        """
        Test concurrent operations and thread safety.
        
        Validates:
        - Multiple simultaneous reflections
        - Pattern detection during reflection
        - Memory operations concurrency
        - Resource contention handling
        """
        # Create multiple concurrent reflection tasks
        tasks = []
        
        for i in range(5):
            action_data = ActionData(
                id=f"concurrent_action_{i}",
                type="test_operation",
                description=f"Concurrent test {i}",
                context={"test": i},
                timestamp=datetime.now(),
                duration=0.1,
                success=True,
                error=None,
                metadata={}
            )
            
            task = reflection_engine.reflect_on_action(action_data)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Validate all tasks completed successfully
        for result in results:
            assert not isinstance(result, Exception)
            assert isinstance(result, Reflection)


# ================================================
# INDIVIDUAL SUBMODULE TESTS
# ================================================

class TestOutcomeAnalyzer:
    """Direct tests for the OutcomeAnalyzer submodule."""
    
    @pytest.fixture
    def outcome_analyzer(self):
        return OutcomeAnalyzer()
    
    @pytest.mark.asyncio
    async def test_outcome_analysis_accuracy(self, outcome_analyzer):
        """Test outcome analysis accuracy and scoring."""
        # Test perfect outcome
        perfect_outcome = OutcomeData(
            id="perfect_001",
            action_id="action_001",
            expected_result="success",
            actual_result="success",
            success=True,
            deviation_score=0.0,
            impact="positive",
            timestamp=datetime.now(),
            context={},
            metadata={}
        )
        
        analysis = await outcome_analyzer.analyze_outcome(perfect_outcome)
        assert analysis["quality_score"] >= 0.9


class TestPatternDetector:
    """Direct tests for the PatternDetector submodule."""
    
    @pytest.fixture
    def pattern_detector(self):
        return PatternDetector()
    
    @pytest.mark.asyncio
    async def test_pattern_detection_algorithms(self, pattern_detector):
        """Test pattern detection algorithms."""
        # Test with sample historical data
        assert hasattr(pattern_detector, 'detect_success_patterns')
        assert hasattr(pattern_detector, 'detect_failure_patterns')
        assert hasattr(pattern_detector, 'analyze_temporal_patterns')


class TestInsightGenerator:
    """Direct tests for the InsightGenerator submodule."""
    
    @pytest.fixture
    def insight_generator(self):
        return InsightGenerator()
    
    @pytest.mark.asyncio
    async def test_insight_categorization(self, insight_generator):
        """Test insight categorization and prioritization."""
        assert hasattr(insight_generator, 'generate_insights_from_patterns')
        assert hasattr(insight_generator, 'categorize_insights')
        assert hasattr(insight_generator, 'prioritize_insights')


class TestLearningEngine:
    """Direct tests for the LearningEngine submodule."""
    
    @pytest.fixture
    def learning_engine(self):
        return LearningEngine()
    
    @pytest.mark.asyncio
    async def test_continuous_learning(self, learning_engine):
        """Test continuous learning mechanisms."""
        assert hasattr(learning_engine, 'learn_from_feedback')
        assert hasattr(learning_engine, 'update_mental_models')
        assert hasattr(learning_engine, 'suggest_experiments')


class TestMemoryIntegrator:
    """Direct tests for the MemoryIntegrator submodule."""
    
    @pytest.fixture
    def memory_integrator(self):
        return MemoryIntegrator()
    
    @pytest.mark.asyncio
    async def test_memory_operations(self, memory_integrator):
        """Test memory storage and retrieval operations."""
        assert hasattr(memory_integrator, 'store_reflection')
        assert hasattr(memory_integrator, 'retrieve_relevant_reflections')
        assert hasattr(memory_integrator, 'build_learning_graph')


class TestConfidenceCalibrator:
    """Direct tests for the ConfidenceCalibrator submodule."""
    
    @pytest.fixture
    def confidence_calibrator(self):
        return ConfidenceCalibrator()
    
    @pytest.mark.asyncio
    async def test_confidence_calibration(self, confidence_calibrator):
        """Test confidence calibration methods."""
        assert hasattr(confidence_calibrator, 'calibrate_confidence')
        assert hasattr(confidence_calibrator, 'update_accuracy_history')
        assert hasattr(confidence_calibrator, 'get_calibration_metrics')


# ================================================
# PYTEST CONFIGURATION
# ================================================

if __name__ == "__main__":
    # Run tests with verbose output and coverage
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "--cov=intelligence.reflection_engine",
        "--cov=intelligence.reflection",
        "--cov-report=term-missing",
        "--cov-report=html:test_reports/reflection_engine_coverage"
    ])
