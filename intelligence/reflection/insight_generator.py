"""
insight_generator.py - Generate actionable insights from reflection data

This module takes analyzed data from reflections and pattern detection
to generate actionable insights that can improve future decision-making
and performance.
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging
from collections import defaultdict, Counter

# Import the Insight dataclass from parent module
from .. import Insight

logger = logging.getLogger(__name__)


class InsightCategory(Enum):
    """Categories of insights that can be generated."""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RISK_MITIGATION = "risk_mitigation"
    PROCESS_IMPROVEMENT = "process_improvement"
    STRATEGIC_RECOMMENDATION = "strategic_recommendation"
    LEARNING_OPPORTUNITY = "learning_opportunity"
    PATTERN_APPLICATION = "pattern_application"


class InsightPriority(Enum):
    """Priority levels for insights."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class InsightSource:
    """Represents the source data for an insight."""
    source_type: str  # reflection, pattern, correlation, etc.
    source_id: str
    confidence: float
    relevance: float


class InsightGenerator:
    """
    Generates actionable insights from reflection and pattern analysis.
    
    This class synthesizes information from various sources to create
    prioritized, actionable insights that can improve future performance
    and decision-making.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize InsightGenerator.
        
        Args:
            confidence_threshold: Minimum confidence for actionable insights
        """
        self.confidence_threshold = confidence_threshold
        self._insight_cache = {}
        self._insight_metrics = {
            "total_insights_generated": 0,
            "actionable_insights": 0,
            "insights_by_category": {},
            "avg_confidence": 0.0,
            "last_updated": datetime.now()
        }
        
        # Insight generation parameters
        self._max_insights_per_request = 20
        self._insight_expiry_days = 30
        
    # ==========================================================================
    # CORE INSIGHT GENERATION METHODS
    # ==========================================================================
    
    def generate_contextual_insights(self,
                                   context: Dict[str, Any],
                                   historical_data: List[Any],
                                   confidence_threshold: Optional[float] = None) -> List[Insight]:
        """
        Generate actionable insights from accumulated reflections.
        
        Args:
            context: Current context for which insights are needed
            historical_data: Historical reflections and analysis data
            confidence_threshold: Override default confidence threshold
            
        Returns:
            List of prioritized, actionable insights
        """
        try:
            threshold = confidence_threshold or self.confidence_threshold
            insights = []
            
            # Generate different types of insights
            performance_insights = self._generate_performance_insights(context, historical_data)
            risk_insights = self._generate_risk_insights(context, historical_data)
            process_insights = self._generate_process_insights(context, historical_data)
            strategic_insights = self._generate_strategic_insights(context, historical_data)
            learning_insights = self._generate_learning_insights(context, historical_data)
            pattern_insights = self._generate_pattern_insights(context, historical_data)
            
            # Combine all insights
            all_insights = (
                performance_insights + risk_insights + process_insights +
                strategic_insights + learning_insights + pattern_insights
            )
            
            # Filter by confidence threshold
            filtered_insights = [i for i in all_insights if i.confidence >= threshold]
            
            # Remove duplicates and merge similar insights
            unique_insights = self._deduplicate_insights(filtered_insights)
            
            # Prioritize insights
            prioritized_insights = self._prioritize_insights(unique_insights, context)
            
            # Limit results
            final_insights = prioritized_insights[:self._max_insights_per_request]
            
            # Update metrics
            self._update_insight_metrics(final_insights)
            
            logger.info(f"Generated {len(final_insights)} contextual insights")
            return final_insights
            
        except Exception as e:
            logger.error(f"Error generating contextual insights: {str(e)}")
            return []
    
    def generate_insights_from_patterns(self,
                                      patterns: List[Dict[str, Any]],
                                      current_context: Optional[Dict[str, Any]] = None) -> List[Insight]:
        """Generate insights specifically from detected patterns."""
        try:
            insights = []
            
            for pattern in patterns:
                # Generate insights for success patterns
                if pattern.get('type') in ['success_pattern', 'SUCCESS_PATTERN']:
                    success_insights = self._generate_success_pattern_insights(pattern, current_context)
                    insights.extend(success_insights)
                
                # Generate insights for failure patterns
                elif pattern.get('type') in ['failure_pattern', 'FAILURE_PATTERN']:
                    failure_insights = self._generate_failure_pattern_insights(pattern, current_context)
                    insights.extend(failure_insights)
                
                # Generate insights for temporal patterns
                elif pattern.get('type') in ['temporal_pattern', 'TEMPORAL_PATTERN']:
                    temporal_insights = self._generate_temporal_pattern_insights(pattern, current_context)
                    insights.extend(temporal_insights)
            
            # Filter and prioritize
            filtered_insights = [i for i in insights if i.confidence >= self.confidence_threshold]
            prioritized_insights = self._prioritize_insights(filtered_insights, current_context or {})
            
            logger.info(f"Generated {len(prioritized_insights)} pattern-based insights")
            return prioritized_insights
            
        except Exception as e:
            logger.error(f"Error generating pattern insights: {str(e)}")
            return []
    
    def generate_comparative_insights(self,
                                    current_performance: Dict[str, Any],
                                    historical_baseline: Dict[str, Any]) -> List[Insight]:
        """Generate insights by comparing current vs historical performance."""
        try:
            insights = []
            
            # Compare key metrics
            for metric, current_value in current_performance.items():
                if metric in historical_baseline:
                    historical_value = historical_baseline[metric]
                    
                    # Generate comparison insight
                    comparison_insight = self._generate_comparison_insight(
                        metric, current_value, historical_value
                    )
                    
                    if comparison_insight:
                        insights.append(comparison_insight)
            
            # Generate trend insights
            trend_insights = self._generate_trend_insights(current_performance, historical_baseline)
            insights.extend(trend_insights)
            
            # Filter and sort
            filtered_insights = [i for i in insights if i.confidence >= self.confidence_threshold]
            sorted_insights = sorted(filtered_insights, key=lambda x: x.priority)
            
            logger.info(f"Generated {len(sorted_insights)} comparative insights")
            return sorted_insights
            
        except Exception as e:
            logger.error(f"Error generating comparative insights: {str(e)}")
            return []
    
    # ==========================================================================
    # SPECIFIC INSIGHT TYPE GENERATORS  
    # ==========================================================================
    
    def _generate_performance_insights(self,
                                     context: Dict[str, Any],
                                     historical_data: List[Any]) -> List[Insight]:
        """Generate performance optimization insights."""
        insights = []
        
        try:
            # Analyze performance trends
            if historical_data:
                # Look for performance improvement opportunities
                low_performing_areas = self._identify_low_performing_areas(historical_data)
                
                for area in low_performing_areas:
                    insight = Insight(
                        id=f"perf_{area['metric']}_{int(datetime.now().timestamp())}",
                        category=InsightCategory.PERFORMANCE_OPTIMIZATION.value,
                        description=f"Improve {area['metric']}: current performance at {area['current']:.1%}, potential for {area['improvement']:.1%} improvement",
                        evidence=area['evidence'],
                        confidence=area['confidence'],
                        actionable=True,
                        priority=self._calculate_insight_priority(area['impact']),
                        expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                    )
                    insights.append(insight)
                
                # Look for high-performing patterns to replicate
                high_performing_patterns = self._identify_high_performing_patterns(historical_data)
                
                for pattern in high_performing_patterns:
                    insight = Insight(
                        id=f"perf_pattern_{pattern['id']}",
                        category=InsightCategory.PERFORMANCE_OPTIMIZATION.value,
                        description=f"Replicate success pattern: {pattern['description']}",
                        evidence=pattern['evidence'],
                        confidence=pattern['confidence'],
                        actionable=True,
                        priority=2,  # High priority for proven patterns
                        expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                    )
                    insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating performance insights: {str(e)}")
        
        return insights
    
    def _generate_risk_insights(self,
                              context: Dict[str, Any],
                              historical_data: List[Any]) -> List[Insight]:
        """Generate risk mitigation insights."""
        insights = []
        
        try:
            # Identify potential risks based on current context and historical failures
            risk_indicators = self._identify_risk_indicators(context, historical_data)
            
            for risk in risk_indicators:
                insight = Insight(
                    id=f"risk_{risk['type']}_{int(datetime.now().timestamp())}",
                    category=InsightCategory.RISK_MITIGATION.value,
                    description=f"Risk detected: {risk['description']} (probability: {risk['probability']:.1%})",
                    evidence=risk['evidence'],
                    confidence=risk['confidence'],
                    actionable=True,
                    priority=1 if risk['severity'] == 'high' else 2,
                    expiration_date=datetime.now() + timedelta(days=7)  # Shorter expiry for risks
                )
                insights.append(insight)
                
                # Generate specific mitigation insight
                mitigation_insight = Insight(
                    id=f"mitigation_{risk['type']}_{int(datetime.now().timestamp())}",
                    category=InsightCategory.RISK_MITIGATION.value,
                    description=f"Mitigate {risk['type']} risk: {risk['mitigation_strategy']}",
                    evidence=risk['evidence'],
                    confidence=risk['confidence'] * 0.9,
                    actionable=True,
                    priority=1 if risk['severity'] == 'high' else 2,
                    expiration_date=datetime.now() + timedelta(days=7)
                )
                insights.append(mitigation_insight)
        
        except Exception as e:
            logger.error(f"Error generating risk insights: {str(e)}")
        
        return insights
    
    def _generate_process_insights(self,
                                 context: Dict[str, Any],
                                 historical_data: List[Any]) -> List[Insight]:
        """Generate process improvement insights."""
        insights = []
        
        try:
            # Analyze process inefficiencies
            inefficiencies = self._identify_process_inefficiencies(historical_data)
            
            for inefficiency in inefficiencies:
                insight = Insight(
                    id=f"process_{inefficiency['area']}_{int(datetime.now().timestamp())}",
                    category=InsightCategory.PROCESS_IMPROVEMENT.value,
                    description=f"Process improvement opportunity: {inefficiency['description']}",
                    evidence=inefficiency['evidence'],
                    confidence=inefficiency['confidence'],
                    actionable=True,
                    priority=3,  # Medium priority for process improvements
                    expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                )
                insights.append(insight)
            
            # Identify automation opportunities
            automation_opportunities = self._identify_automation_opportunities(historical_data)
            
            for opportunity in automation_opportunities:
                insight = Insight(
                    id=f"automation_{opportunity['process']}_{int(datetime.now().timestamp())}",
                    category=InsightCategory.PROCESS_IMPROVEMENT.value,
                    description=f"Automation opportunity: {opportunity['description']}",
                    evidence=opportunity['evidence'],
                    confidence=opportunity['confidence'],
                    actionable=True,
                    priority=2,  # High priority for automation
                    expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating process insights: {str(e)}")
        
        return insights
    
    def _generate_strategic_insights(self,
                                   context: Dict[str, Any],
                                   historical_data: List[Any]) -> List[Insight]:
        """Generate strategic recommendation insights."""
        insights = []
        
        try:
            # Analyze strategic trends and opportunities
            strategic_opportunities = self._identify_strategic_opportunities(context, historical_data)
            
            for opportunity in strategic_opportunities:
                insight = Insight(
                    id=f"strategic_{opportunity['area']}_{int(datetime.now().timestamp())}",
                    category=InsightCategory.STRATEGIC_RECOMMENDATION.value,
                    description=f"Strategic opportunity: {opportunity['description']}",
                    evidence=opportunity['evidence'],
                    confidence=opportunity['confidence'],
                    actionable=True,
                    priority=self._calculate_strategic_priority(opportunity),
                    expiration_date=datetime.now() + timedelta(days=60)  # Longer expiry for strategic insights
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating strategic insights: {str(e)}")
        
        return insights
    
    def _generate_learning_insights(self,
                                  context: Dict[str, Any],
                                  historical_data: List[Any]) -> List[Insight]:
        """Generate learning opportunity insights."""
        insights = []
        
        try:
            # Identify knowledge gaps
            knowledge_gaps = self._identify_knowledge_gaps(historical_data)
            
            for gap in knowledge_gaps:
                insight = Insight(
                    id=f"learning_{gap['area']}_{int(datetime.now().timestamp())}",
                    category=InsightCategory.LEARNING_OPPORTUNITY.value,
                    description=f"Learning opportunity: {gap['description']}",
                    evidence=gap['evidence'],
                    confidence=gap['confidence'],
                    actionable=True,
                    priority=3,  # Medium priority for learning
                    expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating learning insights: {str(e)}")
        
        return insights
    
    def _generate_pattern_insights(self,
                                 context: Dict[str, Any],
                                 historical_data: List[Any]) -> List[Insight]:
        """Generate pattern application insights."""
        insights = []
        
        try:
            # Find applicable patterns for current context
            applicable_patterns = self._find_applicable_patterns(context, historical_data)
            
            for pattern in applicable_patterns:
                insight = Insight(
                    id=f"pattern_{pattern['id']}",
                    category=InsightCategory.PATTERN_APPLICATION.value,
                    description=f"Apply pattern: {pattern['description']}",
                    evidence=pattern['evidence'],
                    confidence=pattern['match_confidence'],
                    actionable=True,
                    priority=2 if pattern['pattern_type'] == 'success' else 1,
                    expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating pattern insights: {str(e)}")
        
        return insights
    
    # ==========================================================================
    # PATTERN-SPECIFIC INSIGHT GENERATORS
    # ==========================================================================
    
    def _generate_success_pattern_insights(self,
                                         pattern: Dict[str, Any],
                                         context: Optional[Dict[str, Any]]) -> List[Insight]:
        """Generate insights from success patterns."""
        insights = []
        
        try:
            # Main application insight
            insight = Insight(
                id=f"success_pattern_{pattern.get('id', 'unknown')}",
                category=InsightCategory.PATTERN_APPLICATION.value,
                description=f"Apply proven success pattern: {pattern.get('description', 'Unknown pattern')}",
                evidence=[f"Pattern observed {pattern.get('frequency', 0)} times with {pattern.get('confidence', 0):.1%} confidence"],
                confidence=pattern.get('confidence', 0.5),
                actionable=True,
                priority=2,
                expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
            )
            insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating success pattern insights: {str(e)}")
        
        return insights
    
    def _generate_failure_pattern_insights(self,
                                         pattern: Dict[str, Any],
                                         context: Optional[Dict[str, Any]]) -> List[Insight]:
        """Generate insights from failure patterns."""
        insights = []
        
        try:
            # Warning insight
            insight = Insight(
                id=f"failure_pattern_{pattern.get('id', 'unknown')}",
                category=InsightCategory.RISK_MITIGATION.value,
                description=f"Avoid failure pattern: {pattern.get('description', 'Unknown pattern')}",
                evidence=[f"Pattern leads to failure {pattern.get('frequency', 0)} times"],
                confidence=pattern.get('confidence', 0.5),
                actionable=True,
                priority=1,
                expiration_date=datetime.now() + timedelta(days=7)
            )
            insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating failure pattern insights: {str(e)}")
        
        return insights
    
    def _generate_temporal_pattern_insights(self,
                                          pattern: Dict[str, Any],
                                          context: Optional[Dict[str, Any]]) -> List[Insight]:
        """Generate insights from temporal patterns."""
        insights = []
        
        try:
            insight = Insight(
                id=f"temporal_{pattern.get('id', 'unknown')}",
                category=InsightCategory.STRATEGIC_RECOMMENDATION.value,
                description=f"Timing optimization: {pattern.get('description', 'Unknown temporal pattern')}",
                evidence=[f"Temporal pattern observed with {pattern.get('confidence', 0):.1%} confidence"],
                confidence=pattern.get('confidence', 0.5),
                actionable=True,
                priority=3,
                expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
            )
            insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error generating temporal pattern insights: {str(e)}")
        
        return insights
    
    # ==========================================================================
    # SUPPORTING ANALYSIS METHODS (Simplified implementations)
    # ==========================================================================
    
    def _generate_comparison_insight(self,
                                   metric: str,
                                   current_value: Any,
                                   historical_value: Any) -> Optional[Insight]:
        """Generate insight from metric comparison."""
        try:
            if isinstance(current_value, (int, float)) and isinstance(historical_value, (int, float)):
                if historical_value != 0:
                    change_percent = ((current_value - historical_value) / historical_value) * 100
                else:
                    change_percent = 100 if current_value > 0 else 0
                
                if abs(change_percent) < 5:
                    return None
                
                if change_percent > 0:
                    description = f"{metric} improved by {change_percent:.1f}%"
                    category = InsightCategory.PERFORMANCE_OPTIMIZATION.value
                    priority = 3
                else:
                    description = f"{metric} declined by {abs(change_percent):.1f}%"
                    category = InsightCategory.RISK_MITIGATION.value
                    priority = 2
                
                return Insight(
                    id=f"comparison_{metric}_{int(datetime.now().timestamp())}",
                    category=category,
                    description=description,
                    evidence=[f"Historical: {historical_value}, Current: {current_value}"],
                    confidence=0.8,
                    actionable=True,
                    priority=priority,
                    expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                )
                
        except Exception as e:
            logger.error(f"Error generating comparison insight: {str(e)}")
            return None
    
    def _generate_trend_insights(self,
                               current_performance: Dict[str, Any],
                               historical_baseline: Dict[str, Any]) -> List[Insight]:
        """Generate insights from performance trends."""
        insights = []
        
        try:
            improving_metrics = []
            declining_metrics = []
            
            for metric, current_value in current_performance.items():
                if metric in historical_baseline:
                    historical_value = historical_baseline[metric]
                    
                    if isinstance(current_value, (int, float)) and isinstance(historical_value, (int, float)):
                        if current_value > historical_value * 1.1:
                            improving_metrics.append(metric)
                        elif current_value < historical_value * 0.9:
                            declining_metrics.append(metric)
            
            if improving_metrics:
                insight = Insight(
                    id=f"trend_positive_{int(datetime.now().timestamp())}",
                    category=InsightCategory.PERFORMANCE_OPTIMIZATION.value,
                    description=f"Positive trend in {len(improving_metrics)} metrics: {', '.join(improving_metrics[:3])}",
                    evidence=[f"Improving metrics: {', '.join(improving_metrics)}"],
                    confidence=0.75,
                    actionable=True,
                    priority=3,
                    expiration_date=datetime.now() + timedelta(days=self._insight_expiry_days)
                )
                insights.append(insight)
            
            if declining_metrics:
                insight = Insight(
                    id=f"trend_negative_{int(datetime.now().timestamp())}",
                    category=InsightCategory.RISK_MITIGATION.value,
                    description=f"Declining trend in {len(declining_metrics)} metrics: {', '.join(declining_metrics[:3])}",
                    evidence=[f"Declining metrics: {', '.join(declining_metrics)}"],
                    confidence=0.8,
                    actionable=True,
                    priority=1,
                    expiration_date=datetime.now() + timedelta(days=7)
                )
                insights.append(insight)
            
        except Exception as e:
            logger.error(f"Error generating trend insights: {str(e)}")
        
        return insights
    
    def _deduplicate_insights(self, insights: List[Insight]) -> List[Insight]:
        """Remove duplicate insights."""
        unique_insights = []
        seen_descriptions = set()
        
        for insight in insights:
            if insight.description not in seen_descriptions:
                unique_insights.append(insight)
                seen_descriptions.add(insight.description)
        
        return unique_insights
    
    def _prioritize_insights(self, insights: List[Insight], context: Dict[str, Any]) -> List[Insight]:
        """Prioritize insights based on context."""
        return sorted(insights, key=lambda x: (x.priority, -x.confidence))
    
    def _calculate_insight_priority(self, impact_score: float) -> int:
        """Calculate priority based on impact score."""
        if impact_score >= 0.8:
            return 1  # Critical
        elif impact_score >= 0.6:
            return 2  # High
        elif impact_score >= 0.4:
            return 3  # Medium
        else:
            return 4  # Low
    
    def _calculate_strategic_priority(self, opportunity: Dict[str, Any]) -> int:
        """Calculate priority for strategic opportunities."""
        impact = opportunity.get('impact', 0.5)
        feasibility = opportunity.get('feasibility', 0.5)
        urgency = opportunity.get('urgency', 0.5)
        
        score = (impact * 0.5) + (feasibility * 0.3) + (urgency * 0.2)
        return self._calculate_insight_priority(score)
    
    def _update_insight_metrics(self, insights: List[Insight]) -> None:
        """Update insight generation metrics."""
        self._insight_metrics["total_insights_generated"] += len(insights)
        self._insight_metrics["actionable_insights"] += len([i for i in insights if i.actionable])
        
        for insight in insights:
            category = insight.category
            current_count = self._insight_metrics["insights_by_category"].get(category, 0)
            self._insight_metrics["insights_by_category"][category] = current_count + 1
        
        if insights:
            avg_confidence = sum(i.confidence for i in insights) / len(insights)
            total_insights = self._insight_metrics["total_insights_generated"]
            current_avg = self._insight_metrics["avg_confidence"]
            
            new_avg = ((current_avg * (total_insights - len(insights))) + (avg_confidence * len(insights))) / total_insights
            self._insight_metrics["avg_confidence"] = new_avg
        
        self._insight_metrics["last_updated"] = datetime.now()
    
    # ==========================================================================
    # HELPER METHODS (Simplified mock implementations)
    # ==========================================================================
    
    def _identify_low_performing_areas(self, historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify low-performing areas."""
        return [{
            'metric': 'task_completion_rate',
            'current': 0.65,
            'improvement': 0.85,
            'evidence': ['Multiple tasks incomplete', 'Resource constraints identified'],
            'confidence': 0.75,
            'impact': 0.8
        }]
    
    def _identify_high_performing_patterns(self, historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify high-performing patterns."""
        return [{
            'id': 'high_prep_pattern',
            'description': 'Thorough preparation leads to better outcomes',
            'evidence': ['5+ hours preparation correlates with success'],
            'confidence': 0.85
        }]
    
    def _identify_risk_indicators(self, context: Dict[str, Any], historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify potential risks."""
        risks = []
        
        if context.get('time_pressure') == 'high':
            risks.append({
                'type': 'time_pressure',
                'description': 'High time pressure increases failure risk',
                'probability': 0.6,
                'severity': 'high',
                'evidence': ['Time pressure correlation with failures'],
                'confidence': 0.8,
                'mitigation_strategy': 'Reduce scope or extend timeline'
            })
        
        return risks
    
    def _identify_process_inefficiencies(self, historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify process inefficiencies."""
        return [{
            'area': 'communication_delays',
            'description': 'Communication delays add 2 days to timelines',
            'evidence': ['48-hour average response time'],
            'confidence': 0.75
        }]
    
    def _identify_automation_opportunities(self, historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify automation opportunities."""
        return [{
            'process': 'status_reporting',
            'description': 'Automate weekly status reports - saves 3 hours',
            'evidence': ['Manual reporting takes 3 hours weekly'],
            'confidence': 0.9
        }]
    
    def _identify_strategic_opportunities(self, context: Dict[str, Any], historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify strategic opportunities."""
        return [{
            'area': 'skill_development',
            'description': 'Invest in advanced analytics for 25% efficiency gain',
            'evidence': ['Analytics tasks outsourced', 'Internal gap identified'],
            'confidence': 0.7,
            'impact': 0.8,
            'feasibility': 0.6,
            'urgency': 0.5
        }]
    
    def _identify_knowledge_gaps(self, historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Identify knowledge gaps."""
        return [{
            'area': 'advanced_python',
            'description': 'Advanced Python could improve code quality by 30%',
            'evidence': ['Code reviews identify gaps'],
            'confidence': 0.75
        }]
    
    def _find_applicable_patterns(self, context: Dict[str, Any], historical_data: List[Any]) -> List[Dict[str, Any]]:
        """Find applicable patterns."""
        return [{
            'id': 'preparation_success_pattern',
            'description': 'Thorough preparation correlates with 85% success rate',
            'evidence': ['Pattern observed in 15+ cases'],
            'match_confidence': 0.8,
            'pattern_type': 'success'
        }]
    
    # ==========================================================================
    # METRICS AND REPORTING
    # ==========================================================================
    
    def get_effectiveness_metrics(self) -> Dict[str, Any]:
        """Get insight effectiveness metrics."""
        return {
            **self._insight_metrics,
            "actionability_rate": self._insight_metrics["actionable_insights"] / max(1, self._insight_metrics["total_insights_generated"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def count_insights_in_timeframe(self, timeframe: timedelta) -> int:
        """Count insights generated within timeframe."""
        return len(self._insight_cache)
    
    def get_insight_summary(self) -> Dict[str, Any]:
        """Get summary of insight generation performance."""
        return {
            "total_generated": self._insight_metrics["total_insights_generated"],
            "actionable_count": self._insight_metrics["actionable_insights"],
            "category_breakdown": self._insight_metrics["insights_by_category"],
            "average_confidence": self._insight_metrics["avg_confidence"],
            "last_updated": self._insight_metrics["last_updated"].isoformat()
        }
