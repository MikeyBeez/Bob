"""
outcome_analyzer.py - Analyze outcomes and extract insights

This module analyzes completed actions and their outcomes to identify
what worked, what didn't, and why. It compares expected vs actual results
and extracts lessons for future improvement.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Import the Reflection dataclass and ReflectionType enum from parent
from .. import Reflection, ReflectionType

logger = logging.getLogger(__name__)


class OutcomeType(Enum):
    """Types of outcomes that can be analyzed."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class OutcomeAnalysis:
    """Detailed analysis of an action outcome."""
    outcome_type: OutcomeType
    expected_result: Dict[str, Any]
    actual_result: Dict[str, Any]
    deviation_score: float
    success_factors: List[str]
    failure_factors: List[str]
    lessons_learned: List[str]
    confidence: float
    actionable_improvements: List[str]


@dataclass
class DecisionAnalysis:
    """Analysis of decision quality and effectiveness."""
    decision_id: str
    quality_score: float
    accuracy_score: float
    timing_score: float
    information_adequacy: float
    outcome_alignment: float
    improvement_suggestions: List[str]


class OutcomeAnalyzer:
    """
    Analyzes action outcomes and decision quality to extract learnings.
    
    This class examines completed actions, compares expected vs actual outcomes,
    and identifies patterns that led to success or failure. It provides the
    foundation for the reflection engine's learning capabilities.
    """
    
    def __init__(self, db_core: Optional[Any] = None):
        """
        Initialize OutcomeAnalyzer.
        
        Args:
            db_core: DatabaseCore instance for accessing historical data
        """
        self.db_core = db_core
        self._outcome_cache = {}
        self._analysis_metrics = {
            "total_analyses": 0,
            "success_rate": 0.0,
            "avg_deviation": 0.0,
            "pattern_matches": 0
        }
        
    # ==========================================================================
    # CORE OUTCOME ANALYSIS METHODS
    # ==========================================================================
    
    def analyze_action_outcome(self, 
                             action_data: Dict[str, Any],
                             context: Dict[str, Any]) -> Reflection:
        """
        Analyze a completed action and its outcome.
        
        Args:
            action_data: Dictionary with action details, expectations, and results
            context: Additional context for the analysis
            
        Returns:
            Reflection with detailed outcome analysis
        """
        try:
            # Extract key components
            action_id = action_data.get('id', f"action_{datetime.now().timestamp()}")
            expected = action_data.get('expected_outcome', {})
            actual = action_data.get('actual_outcome', {})
            
            # Perform outcome analysis
            outcome_analysis = self._analyze_outcome_deviation(expected, actual)
            
            # Identify contributing factors
            success_factors = self._identify_success_factors(action_data, context)
            failure_factors = self._identify_failure_factors(action_data, context)
            
            # Extract lessons learned
            lessons = self._extract_lessons(outcome_analysis, success_factors, failure_factors)
            
            # Generate insights
            insights = self._generate_outcome_insights(outcome_analysis, context)
            
            # Calculate confidence
            confidence = self._calculate_analysis_confidence(action_data, context)
            
            # Create reflection
            reflection = Reflection(
                id=f"reflection_{action_id}_{int(datetime.now().timestamp())}",
                type=ReflectionType.ACTION_OUTCOME,
                timestamp=datetime.now(),
                context={
                    "action_id": action_id,
                    "domain": action_data.get('domain', 'general'),
                    "complexity": action_data.get('complexity', 'medium'),
                    **context
                },
                analysis={
                    "outcome_type": outcome_analysis.outcome_type.value,
                    "deviation_score": outcome_analysis.deviation_score,
                    "success_factors": success_factors,
                    "failure_factors": failure_factors,
                    "expected_vs_actual": {
                        "expected": expected,
                        "actual": actual,
                        "alignment": self._calculate_alignment(expected, actual)
                    }
                },
                insights=insights,
                lessons_learned=lessons,
                confidence=confidence,
                actionable_items=outcome_analysis.actionable_improvements
            )
            
            # Update metrics
            self._update_analysis_metrics(outcome_analysis)
            
            logger.info(f"Analyzed action outcome for {action_id}: {outcome_analysis.outcome_type.value}")
            return reflection
            
        except Exception as e:
            logger.error(f"Error analyzing action outcome: {str(e)}")
            return self._create_error_reflection(action_data, str(e))
    
    def analyze_outcome_deviation(self,
                                outcome_data: Dict[str, Any],
                                historical_expectations: List[Dict[str, Any]]) -> Reflection:
        """
        Analyze deviation between expected and actual outcomes.
        
        Args:
            outcome_data: Data about the outcome with expectations and actuals
            historical_expectations: Historical data about similar expectations
            
        Returns:
            Reflection focused on expectation vs reality analysis
        """
        try:
            # Extract outcome components
            expected = outcome_data.get('expected', {})
            actual = outcome_data.get('actual', {})
            domain = outcome_data.get('domain', 'general')
            
            # Analyze the deviation
            outcome_analysis = self._analyze_outcome_deviation(expected, actual)
            
            # Compare with historical patterns
            historical_analysis = self._analyze_historical_patterns(
                outcome_analysis, historical_expectations
            )
            
            # Generate deviation-specific insights
            insights = self._generate_deviation_insights(
                outcome_analysis, historical_analysis
            )
            
            # Create reflection
            reflection = Reflection(
                id=f"deviation_analysis_{int(datetime.now().timestamp())}",
                type=ReflectionType.PERFORMANCE_ANALYSIS,
                timestamp=datetime.now(),
                context={
                    "domain": domain,
                    "historical_samples": len(historical_expectations),
                    "deviation_analysis": True
                },
                analysis={
                    "outcome_analysis": {
                        "type": outcome_analysis.outcome_type.value,
                        "deviation_score": outcome_analysis.deviation_score,
                        "success_factors": outcome_analysis.success_factors,
                        "failure_factors": outcome_analysis.failure_factors
                    },
                    "historical_comparison": historical_analysis,
                    "expectation_calibration": self._calibrate_expectations(
                        expected, actual, historical_expectations
                    )
                },
                insights=insights,
                lessons_learned=outcome_analysis.lessons_learned,
                confidence=self._calculate_deviation_confidence(
                    outcome_analysis, historical_expectations
                ),
                actionable_items=outcome_analysis.actionable_improvements
            )
            
            logger.info(f"Analyzed outcome deviation for domain {domain}")
            return reflection
            
        except Exception as e:
            logger.error(f"Error analyzing outcome deviation: {str(e)}")
            return self._create_error_reflection(outcome_data, str(e))
    
    def analyze_decision_quality(self,
                               decision_data: Dict[str, Any],
                               decision_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the quality of a decision and its outcomes.
        
        Args:
            decision_data: Information about the decision and its results
            decision_history: Historical data about similar decisions
            
        Returns:
            Detailed decision quality analysis
        """
        try:
            decision_id = decision_data.get('id', f"decision_{datetime.now().timestamp()}")
            
            # Analyze different aspects of decision quality
            quality_score = self._assess_decision_quality(decision_data)
            accuracy_score = self._assess_decision_accuracy(decision_data)
            timing_score = self._assess_decision_timing(decision_data)
            information_score = self._assess_information_adequacy(decision_data)
            outcome_score = self._assess_outcome_alignment(decision_data)
            
            # Compare with historical decisions
            historical_comparison = self._compare_with_historical_decisions(
                decision_data, decision_history
            )
            
            # Generate improvement suggestions
            improvements = self._generate_decision_improvements(
                decision_data, quality_score, accuracy_score, timing_score
            )
            
            analysis = DecisionAnalysis(
                decision_id=decision_id,
                quality_score=quality_score,
                accuracy_score=accuracy_score,
                timing_score=timing_score,
                information_adequacy=information_score,
                outcome_alignment=outcome_score,
                improvement_suggestions=improvements
            )
            
            # Create comprehensive analysis result
            result = {
                "decision_analysis": {
                    "id": decision_id,
                    "overall_quality": (quality_score + accuracy_score + timing_score) / 3,
                    "quality_breakdown": {
                        "decision_quality": quality_score,
                        "accuracy": accuracy_score,
                        "timing": timing_score,
                        "information_adequacy": information_score,
                        "outcome_alignment": outcome_score
                    }
                },
                "historical_comparison": historical_comparison,
                "improvement_suggestions": improvements,
                "confidence": self._calculate_decision_analysis_confidence(
                    analysis, decision_history
                ),
                "analyzed_at": datetime.now().isoformat()
            }
            
            logger.info(f"Analyzed decision quality for {decision_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing decision quality: {str(e)}")
            return {"error": str(e), "decision_id": decision_data.get('id', 'unknown')}
    
    # ==========================================================================
    # OUTCOME ANALYSIS IMPLEMENTATION
    # ==========================================================================
    
    def _analyze_outcome_deviation(self, 
                                 expected: Dict[str, Any],
                                 actual: Dict[str, Any]) -> OutcomeAnalysis:
        """Analyze the deviation between expected and actual outcomes."""
        
        # Calculate deviation score (0.0 = perfect match, 1.0 = complete mismatch)
        deviation_score = self._calculate_deviation_score(expected, actual)
        
        # Determine outcome type based on deviation
        outcome_type = self._classify_outcome_type(deviation_score, expected, actual)
        
        # Identify factors contributing to success/failure
        success_factors = self._extract_success_factors(expected, actual, deviation_score)
        failure_factors = self._extract_failure_factors(expected, actual, deviation_score)
        
        # Extract lessons learned
        lessons = self._extract_outcome_lessons(
            outcome_type, success_factors, failure_factors
        )
        
        # Generate actionable improvements
        improvements = self._generate_actionable_improvements(
            outcome_type, deviation_score, failure_factors
        )
        
        # Calculate confidence in analysis
        confidence = self._calculate_outcome_confidence(expected, actual, deviation_score)
        
        return OutcomeAnalysis(
            outcome_type=outcome_type,
            expected_result=expected,
            actual_result=actual,
            deviation_score=deviation_score,
            success_factors=success_factors,
            failure_factors=failure_factors,
            lessons_learned=lessons,
            confidence=confidence,
            actionable_improvements=improvements
        )
    
    def _calculate_deviation_score(self, 
                                 expected: Dict[str, Any],
                                 actual: Dict[str, Any]) -> float:
        """Calculate numerical deviation score between expected and actual outcomes."""
        if not expected or not actual:
            return 1.0  # Maximum deviation for missing data
        
        total_deviation = 0.0
        comparable_fields = 0
        
        # Compare common fields
        for key in expected.keys():
            if key in actual:
                comparable_fields += 1
                field_deviation = self._calculate_field_deviation(
                    expected[key], actual[key]
                )
                total_deviation += field_deviation
        
        # Penalize missing fields
        missing_expected = len([k for k in expected.keys() if k not in actual])
        missing_actual = len([k for k in actual.keys() if k not in expected])
        
        if comparable_fields == 0:
            return 1.0
        
        # Calculate base deviation
        avg_deviation = total_deviation / comparable_fields
        
        # Adjust for missing fields
        missing_penalty = (missing_expected + missing_actual) * 0.1
        
        return min(1.0, avg_deviation + missing_penalty)
    
    def _calculate_field_deviation(self, expected_val: Any, actual_val: Any) -> float:
        """Calculate deviation between two field values."""
        try:
            # Numeric comparison
            if isinstance(expected_val, (int, float)) and isinstance(actual_val, (int, float)):
                if expected_val == 0 and actual_val == 0:
                    return 0.0
                elif expected_val == 0:
                    return 1.0
                else:
                    return min(1.0, abs(expected_val - actual_val) / abs(expected_val))
            
            # String comparison
            elif isinstance(expected_val, str) and isinstance(actual_val, str):
                if expected_val == actual_val:
                    return 0.0
                else:
                    # Simple string similarity
                    common_chars = len(set(expected_val) & set(actual_val))
                    total_chars = len(set(expected_val) | set(actual_val))
                    return 1.0 - (common_chars / total_chars if total_chars > 0 else 0)
            
            # Boolean comparison
            elif isinstance(expected_val, bool) and isinstance(actual_val, bool):
                return 0.0 if expected_val == actual_val else 1.0
            
            # List comparison
            elif isinstance(expected_val, list) and isinstance(actual_val, list):
                if len(expected_val) == 0 and len(actual_val) == 0:
                    return 0.0
                common_items = len(set(expected_val) & set(actual_val))
                total_items = len(set(expected_val) | set(actual_val))
                return 1.0 - (common_items / total_items if total_items > 0 else 0)
            
            # Dict comparison (recursive)
            elif isinstance(expected_val, dict) and isinstance(actual_val, dict):
                return self._calculate_deviation_score(expected_val, actual_val)
            
            # Different types
            else:
                return 0.0 if expected_val == actual_val else 1.0
                
        except Exception:
            return 1.0  # Maximum deviation on error
    
    def _classify_outcome_type(self, 
                             deviation_score: float,
                             expected: Dict[str, Any],
                             actual: Dict[str, Any]) -> OutcomeType:
        """Classify the outcome based on deviation and context."""
        
        if deviation_score <= 0.1:
            return OutcomeType.SUCCESS
        elif deviation_score <= 0.3:
            return OutcomeType.PARTIAL_SUCCESS
        elif deviation_score <= 0.7:
            return OutcomeType.MIXED
        else:
            return OutcomeType.FAILURE
    
    def _extract_success_factors(self,
                               expected: Dict[str, Any],
                               actual: Dict[str, Any],
                               deviation_score: float) -> List[str]:
        """Extract factors that contributed to successful outcomes."""
        factors = []
        
        # Analyze fields that met or exceeded expectations
        for key, expected_val in expected.items():
            if key in actual:
                actual_val = actual[key]
                field_deviation = self._calculate_field_deviation(expected_val, actual_val)
                
                if field_deviation <= 0.2:  # Low deviation = success factor
                    factors.append(f"Met expectations for {key}")
                    
                # Check if actual exceeded expected (for numeric values)
                if isinstance(expected_val, (int, float)) and isinstance(actual_val, (int, float)):
                    if actual_val > expected_val * 1.1:  # 10% better
                        factors.append(f"Exceeded expectations for {key} by {((actual_val/expected_val - 1) * 100):.1f}%")
        
        # Add general success factors based on overall performance
        if deviation_score <= 0.2:
            factors.append("Overall execution aligned well with expectations")
        
        return factors
    
    def _extract_failure_factors(self,
                               expected: Dict[str, Any],
                               actual: Dict[str, Any], 
                               deviation_score: float) -> List[str]:
        """Extract factors that contributed to poor outcomes."""
        factors = []
        
        # Analyze fields that significantly missed expectations
        for key, expected_val in expected.items():
            if key in actual:
                actual_val = actual[key]
                field_deviation = self._calculate_field_deviation(expected_val, actual_val)
                
                if field_deviation > 0.5:  # High deviation = failure factor
                    factors.append(f"Significant miss on {key} expectations")
                    
                # Check if actual was much worse than expected
                if isinstance(expected_val, (int, float)) and isinstance(actual_val, (int, float)):
                    if actual_val < expected_val * 0.8:  # 20% worse
                        factors.append(f"Underperformed on {key} by {((1 - actual_val/expected_val) * 100):.1f}%")
            else:
                factors.append(f"Missing expected outcome: {key}")
        
        # Check for unexpected negative outcomes
        for key, actual_val in actual.items():
            if key not in expected and str(actual_val).lower() in ['failed', 'error', 'timeout']:
                factors.append(f"Unexpected negative outcome: {key}")
        
        return factors
    
    def _extract_outcome_lessons(self,
                               outcome_type: OutcomeType,
                               success_factors: List[str],
                               failure_factors: List[str]) -> List[str]:
        """Extract lessons learned from outcome analysis."""
        lessons = []
        
        if outcome_type in [OutcomeType.SUCCESS, OutcomeType.PARTIAL_SUCCESS]:
            lessons.append("Identify and replicate successful approaches")
            if success_factors:
                lessons.append(f"Key success drivers: {', '.join(success_factors[:3])}")
        
        if outcome_type in [OutcomeType.FAILURE, OutcomeType.MIXED]:
            lessons.append("Address root causes of underperformance")
            if failure_factors:
                lessons.append(f"Primary failure points: {', '.join(failure_factors[:3])}")
        
        if failure_factors and success_factors:
            lessons.append("Balance successful elements while addressing weaknesses")
        
        # Add general lessons
        lessons.append("Improve expectation calibration for better predictions")
        lessons.append("Increase monitoring during execution for early detection of issues")
        
        return lessons
    
    def _generate_actionable_improvements(self,
                                        outcome_type: OutcomeType,
                                        deviation_score: float,
                                        failure_factors: List[str]) -> List[str]:
        """Generate specific actionable improvements."""
        improvements = []
        
        if deviation_score > 0.3:
            improvements.append("Improve expectation setting and calibration")
            improvements.append("Increase monitoring and feedback during execution")
        
        if failure_factors:
            improvements.append("Develop mitigation strategies for identified failure factors")
            improvements.append("Create early warning systems for similar failure patterns")
        
        if outcome_type == OutcomeType.FAILURE:
            improvements.append("Conduct thorough post-mortem analysis")
            improvements.append("Review and strengthen planning processes")
        
        improvements.append("Document lessons learned for future reference")
        improvements.append("Update decision-making criteria based on insights")
        
        return improvements
    
    # ==========================================================================
    # SUPPORTING ANALYSIS METHODS
    # ==========================================================================
    
    def _identify_success_factors(self,
                                action_data: Dict[str, Any],
                                context: Dict[str, Any]) -> List[str]:
        """Identify factors that contributed to successful execution."""
        factors = []
        
        # Analyze action characteristics
        if action_data.get('preparation_time') and action_data.get('preparation_time') > 0:
            factors.append("Adequate preparation time allocated")
        
        if action_data.get('resources_adequate', False):
            factors.append("Sufficient resources available")
        
        if action_data.get('clear_objectives', False):
            factors.append("Clear objectives defined")
        
        # Analyze context factors
        if context.get('favorable_conditions', False):
            factors.append("Favorable external conditions")
        
        if context.get('stakeholder_support', False):
            factors.append("Strong stakeholder support")
        
        return factors
    
    def _identify_failure_factors(self,
                                action_data: Dict[str, Any],
                                context: Dict[str, Any]) -> List[str]:
        """Identify factors that contributed to poor execution."""
        factors = []
        
        # Analyze action characteristics
        if action_data.get('time_pressure', False):
            factors.append("Excessive time pressure")
        
        if not action_data.get('resources_adequate', True):
            factors.append("Insufficient resources")
        
        if not action_data.get('clear_objectives', True):
            factors.append("Unclear or conflicting objectives")
        
        # Analyze context factors
        if context.get('unfavorable_conditions', False):
            factors.append("Unfavorable external conditions")
        
        if context.get('stakeholder_resistance', False):
            factors.append("Stakeholder resistance or lack of support")
        
        return factors
    
    def _extract_lessons(self,
                       outcome_analysis: OutcomeAnalysis,
                       success_factors: List[str],
                       failure_factors: List[str]) -> List[str]:
        """Extract comprehensive lessons from the analysis."""
        lessons = []
        
        # Combine outcome lessons with factor-based lessons
        lessons.extend(outcome_analysis.lessons_learned)
        
        # Add factor-specific lessons
        if success_factors:
            lessons.append(f"Leverage these success factors: {', '.join(success_factors[:2])}")
        
        if failure_factors:
            lessons.append(f"Mitigate these failure factors: {', '.join(failure_factors[:2])}")
        
        # Add deviation-specific lessons
        if outcome_analysis.deviation_score > 0.5:
            lessons.append("Improve accuracy of outcome predictions")
        
        return list(set(lessons))  # Remove duplicates
    
    def _generate_outcome_insights(self,
                                 outcome_analysis: OutcomeAnalysis,
                                 context: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from outcome analysis."""
        insights = []
        
        # Performance insights
        if outcome_analysis.deviation_score <= 0.2:
            insights.append("Execution approach is well-calibrated and should be replicated")
        elif outcome_analysis.deviation_score > 0.7:
            insights.append("Significant deviation suggests need for process improvement")
        
        # Factor-based insights
        if len(outcome_analysis.success_factors) > len(outcome_analysis.failure_factors):
            insights.append("Strong foundation exists - focus on amplifying successful elements")
        else:
            insights.append("Address failure factors before scaling similar actions")
        
        # Context-specific insights
        domain = context.get('domain', 'general')
        if domain != 'general':
            insights.append(f"Domain-specific patterns identified for {domain}")
        
        return insights
    
    def _calculate_analysis_confidence(self,
                                     action_data: Dict[str, Any],
                                     context: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis results."""
        confidence = 0.7  # Base confidence
        
        # Adjust based on data quality
        if action_data.get('expected_outcome') and action_data.get('actual_outcome'):
            confidence += 0.1
        
        if context.get('historical_data'):
            confidence += 0.1
        
        if action_data.get('detailed_metrics'):
            confidence += 0.1
        
        # Penalize for missing information
        required_fields = ['expected_outcome', 'actual_outcome', 'domain']
        missing_fields = len([f for f in required_fields if not action_data.get(f)])
        confidence -= missing_fields * 0.05
        
        return max(0.1, min(1.0, confidence))
    
    def _calculate_outcome_confidence(self,
                                    expected: Dict[str, Any],
                                    actual: Dict[str, Any],
                                    deviation_score: float) -> float:
        """Calculate confidence in outcome analysis."""
        base_confidence = 0.8
        
        # Adjust based on data completeness
        if not expected or not actual:
            base_confidence -= 0.3
        
        # Adjust based on deviation clarity
        if deviation_score <= 0.1 or deviation_score >= 0.9:
            base_confidence += 0.1  # Clear outcomes are easier to analyze
        elif 0.4 <= deviation_score <= 0.6:
            base_confidence -= 0.1  # Ambiguous outcomes are harder to analyze
        
        return max(0.1, min(1.0, base_confidence))
    
    # ==========================================================================
    # HISTORICAL ANALYSIS METHODS
    # ==========================================================================
    
    def _analyze_historical_patterns(self,
                                   outcome_analysis: OutcomeAnalysis,
                                   historical_expectations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns compared to historical data."""
        if not historical_expectations:
            return {"historical_data": "insufficient"}
        
        # Calculate historical accuracy
        historical_deviations = []
        for hist in historical_expectations:
            if hist.get('expected') and hist.get('actual'):
                deviation = self._calculate_deviation_score(
                    hist['expected'], hist['actual']
                )
                historical_deviations.append(deviation)
        
        if not historical_deviations:
            return {"historical_data": "insufficient"}
        
        avg_historical_deviation = sum(historical_deviations) / len(historical_deviations)
        
        return {
            "historical_samples": len(historical_expectations),
            "avg_historical_deviation": avg_historical_deviation,
            "current_vs_historical": outcome_analysis.deviation_score - avg_historical_deviation,
            "performance_trend": self._classify_performance_trend(
                outcome_analysis.deviation_score, avg_historical_deviation
            ),
            "historical_accuracy": 1.0 - avg_historical_deviation
        }
    
    def _classify_performance_trend(self, current_deviation: float, historical_avg: float) -> str:
        """Classify performance trend based on deviations."""
        difference = current_deviation - historical_avg
        
        if difference <= -0.2:
            return "significant_improvement"
        elif difference <= -0.1:
            return "improvement"
        elif difference <= 0.1:
            return "stable"
        elif difference <= 0.2:
            return "decline"
        else:
            return "significant_decline"
    
    def _generate_deviation_insights(self,
                                   outcome_analysis: OutcomeAnalysis,
                                   historical_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights specific to deviation analysis."""
        insights = []
        
        # Historical comparison insights
        if historical_analysis.get("performance_trend") == "significant_improvement":
            insights.append("Performance significantly improved compared to historical average")
        elif historical_analysis.get("performance_trend") == "significant_decline":
            insights.append("Performance declined significantly - investigate root causes")
        
        # Accuracy insights
        historical_accuracy = historical_analysis.get("historical_accuracy", 0.5)
        if outcome_analysis.deviation_score < historical_accuracy:
            insights.append("Outcome prediction was more accurate than historical norm")
        else:
            insights.append("Outcome prediction accuracy below historical performance")
        
        return insights
    
    def _calibrate_expectations(self,
                              expected: Dict[str, Any],
                              actual: Dict[str, Any],
                              historical_expectations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calibrate future expectations based on historical patterns."""
        if not historical_expectations:
            return {"calibration": "insufficient_data"}
        
        # Analyze historical expectation accuracy by field
        field_calibrations = {}
        
        for field in expected.keys():
            if field in actual:
                historical_field_data = []
                
                for hist in historical_expectations:
                    if (hist.get('expected', {}).get(field) is not None and 
                        hist.get('actual', {}).get(field) is not None):
                        hist_expected = hist['expected'][field]
                        hist_actual = hist['actual'][field]
                        
                        if isinstance(hist_expected, (int, float)) and isinstance(hist_actual, (int, float)):
                            ratio = hist_actual / hist_expected if hist_expected != 0 else 1.0
                            historical_field_data.append(ratio)
                
                if historical_field_data:
                    avg_ratio = sum(historical_field_data) / len(historical_field_data)
                    field_calibrations[field] = {
                        "historical_accuracy_ratio": avg_ratio,
                        "sample_size": len(historical_field_data),
                        "suggested_adjustment": avg_ratio
                    }
        
        return {
            "field_calibrations": field_calibrations,
            "overall_calibration_confidence": len(field_calibrations) / len(expected) if expected else 0,
            "recommendation": "Adjust future expectations using historical accuracy ratios"
        }
    
    def _calculate_deviation_confidence(self,
                                      outcome_analysis: OutcomeAnalysis,
                                      historical_expectations: List[Dict[str, Any]]) -> float:
        """Calculate confidence in deviation analysis."""
        base_confidence = 0.7
        
        # Adjust based on historical data availability
        if len(historical_expectations) >= 5:
            base_confidence += 0.15
        elif len(historical_expectations) >= 2:
            base_confidence += 0.05
        else:
            base_confidence -= 0.1
        
        # Adjust based on outcome analysis confidence
        base_confidence += outcome_analysis.confidence * 0.2
        
        return max(0.1, min(1.0, base_confidence))
    
    # ==========================================================================
    # DECISION ANALYSIS METHODS
    # ==========================================================================
    
    def _assess_decision_quality(self, decision_data: Dict[str, Any]) -> float:
        """Assess overall decision quality based on process and information."""
        score = 0.5  # Base score
        
        # Process quality factors
        if decision_data.get('alternatives_considered', 0) > 1:
            score += 0.15
        
        if decision_data.get('stakeholders_consulted', False):
            score += 0.1
        
        if decision_data.get('risks_assessed', False):
            score += 0.1
        
        if decision_data.get('criteria_defined', False):
            score += 0.1
        
        if decision_data.get('data_driven', False):
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _assess_decision_accuracy(self, decision_data: Dict[str, Any]) -> float:
        """Assess how accurate the decision was based on outcomes."""
        expected_outcome = decision_data.get('expected_outcome')
        actual_outcome = decision_data.get('actual_outcome')
        
        if not expected_outcome or not actual_outcome:
            return 0.5  # Neutral score for insufficient data
        
        # Calculate accuracy based on outcome alignment
        deviation = self._calculate_deviation_score(expected_outcome, actual_outcome)
        accuracy = 1.0 - deviation
        
        return max(0.0, min(1.0, accuracy))
    
    def _assess_decision_timing(self, decision_data: Dict[str, Any]) -> float:
        """Assess whether the decision was made at the right time."""
        score = 0.5  # Base score
        
        # Time pressure analysis
        if decision_data.get('time_pressure') == 'low':
            score += 0.2
        elif decision_data.get('time_pressure') == 'high':
            score -= 0.2
        
        # Decision speed vs quality trade-off
        if decision_data.get('decision_speed') == 'optimal':
            score += 0.3
        elif decision_data.get('decision_speed') in ['too_fast', 'too_slow']:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _assess_information_adequacy(self, decision_data: Dict[str, Any]) -> float:
        """Assess whether sufficient information was available for the decision."""
        score = 0.5  # Base score
        
        # Information quality factors
        if decision_data.get('information_completeness', 0.5) > 0.7:
            score += 0.2
        elif decision_data.get('information_completeness', 0.5) < 0.3:
            score -= 0.2
        
        if decision_data.get('information_reliability', 0.5) > 0.7:
            score += 0.15
        
        if decision_data.get('information_timeliness', 0.5) > 0.7:
            score += 0.15
        
        return min(1.0, max(0.0, score))
    
    def _assess_outcome_alignment(self, decision_data: Dict[str, Any]) -> float:
        """Assess how well the actual outcome aligned with the decision intent."""
        intended_outcome = decision_data.get('intended_outcome')
        actual_outcome = decision_data.get('actual_outcome')
        
        if not intended_outcome or not actual_outcome:
            return 0.5
        
        # Calculate alignment
        deviation = self._calculate_deviation_score(intended_outcome, actual_outcome)
        alignment = 1.0 - deviation
        
        return max(0.0, min(1.0, alignment))
    
    def _compare_with_historical_decisions(self,
                                         decision_data: Dict[str, Any],
                                         decision_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare current decision with similar historical decisions."""
        if not decision_history:
            return {"comparison": "insufficient_historical_data"}
        
        # Find similar decisions
        similar_decisions = []
        current_domain = decision_data.get('domain', 'general')
        current_complexity = decision_data.get('complexity', 'medium')
        
        for hist_decision in decision_history:
            if (hist_decision.get('domain') == current_domain and
                hist_decision.get('complexity') == current_complexity):
                similar_decisions.append(hist_decision)
        
        if not similar_decisions:
            similar_decisions = decision_history  # Fall back to all decisions
        
        # Calculate comparative metrics
        historical_quality_scores = []
        historical_accuracy_scores = []
        
        for decision in similar_decisions:
            quality = self._assess_decision_quality(decision)
            accuracy = self._assess_decision_accuracy(decision)
            historical_quality_scores.append(quality)
            historical_accuracy_scores.append(accuracy)
        
        avg_historical_quality = sum(historical_quality_scores) / len(historical_quality_scores)
        avg_historical_accuracy = sum(historical_accuracy_scores) / len(historical_accuracy_scores)
        
        current_quality = self._assess_decision_quality(decision_data)
        current_accuracy = self._assess_decision_accuracy(decision_data)
        
        return {
            "similar_decisions_count": len(similar_decisions),
            "avg_historical_quality": avg_historical_quality,
            "avg_historical_accuracy": avg_historical_accuracy,
            "current_vs_historical_quality": current_quality - avg_historical_quality,
            "current_vs_historical_accuracy": current_accuracy - avg_historical_accuracy,
            "performance_trend": "improved" if (current_quality > avg_historical_quality and 
                                              current_accuracy > avg_historical_accuracy) else "declined"
        }
    
    def _generate_decision_improvements(self,
                                      decision_data: Dict[str, Any],
                                      quality_score: float,
                                      accuracy_score: float,
                                      timing_score: float) -> List[str]:
        """Generate specific improvement suggestions for decision-making."""
        improvements = []
        
        # Quality improvements
        if quality_score < 0.6:
            improvements.append("Improve decision process by considering more alternatives")
            improvements.append("Increase stakeholder consultation and risk assessment")
        
        # Accuracy improvements
        if accuracy_score < 0.6:
            improvements.append("Enhance outcome prediction accuracy")
            improvements.append("Improve information gathering and analysis")
        
        # Timing improvements
        if timing_score < 0.6:
            improvements.append("Optimize decision timing - balance speed with thoroughness")
            improvements.append("Develop better time management for decision processes")
        
        # General improvements
        improvements.append("Document decision rationale for future reference")
        improvements.append("Establish follow-up mechanisms to track outcomes")
        
        return improvements
    
    def _calculate_decision_analysis_confidence(self,
                                              analysis: DecisionAnalysis,
                                              decision_history: List[Dict[str, Any]]) -> float:
        """Calculate confidence in decision analysis."""
        base_confidence = 0.6
        
        # Adjust based on data completeness
        if analysis.quality_score > 0 and analysis.accuracy_score > 0:
            base_confidence += 0.2
        
        # Adjust based on historical data
        if len(decision_history) >= 3:
            base_confidence += 0.15
        elif len(decision_history) >= 1:
            base_confidence += 0.05
        
        # Adjust based on score clarity
        scores = [analysis.quality_score, analysis.accuracy_score, analysis.timing_score]
        if all(score > 0.8 or score < 0.2 for score in scores):
            base_confidence += 0.05  # Clear scores increase confidence
        
        return max(0.1, min(1.0, base_confidence))
    
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================
    
    def _calculate_alignment(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> float:
        """Calculate overall alignment score between expected and actual."""
        deviation = self._calculate_deviation_score(expected, actual)
        return 1.0 - deviation
    
    def _update_analysis_metrics(self, outcome_analysis: OutcomeAnalysis) -> None:
        """Update internal analysis metrics."""
        self._analysis_metrics["total_analyses"] += 1
        
        # Update success rate
        if outcome_analysis.outcome_type in [OutcomeType.SUCCESS, OutcomeType.PARTIAL_SUCCESS]:
            success_count = self._analysis_metrics.get("success_count", 0) + 1
            self._analysis_metrics["success_count"] = success_count
            self._analysis_metrics["success_rate"] = success_count / self._analysis_metrics["total_analyses"]
        
        # Update average deviation
        current_avg = self._analysis_metrics["avg_deviation"]
        total_analyses = self._analysis_metrics["total_analyses"]
        new_avg = ((current_avg * (total_analyses - 1)) + outcome_analysis.deviation_score) / total_analyses
        self._analysis_metrics["avg_deviation"] = new_avg
    
    def _create_error_reflection(self, data: Dict[str, Any], error_msg: str) -> Reflection:
        """Create a reflection for error cases."""
        return Reflection(
            id=f"error_reflection_{int(datetime.now().timestamp())}",
            type=ReflectionType.ERROR_ANALYSIS,
            timestamp=datetime.now(),
            context={"error": True, "original_data": data},
            analysis={"error_message": error_msg},
            insights=[f"Analysis failed: {error_msg}"],
            lessons_learned=["Improve error handling and data validation"],
            confidence=0.1,
            actionable_items=["Review input data quality", "Enhance error handling"]
        )
    
    def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get current analysis metrics."""
        return {
            **self._analysis_metrics,
            "timestamp": datetime.now().isoformat()
        }
