"""
learning_engine.py - Continuous learning and model updates

This module handles the continuous learning aspects of the reflection system,
updating internal models based on new evidence, feedback, and outcomes.
It manages the learning rate, model adaptation, and knowledge evolution.
"""

from typing import Any, Dict, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging
import math
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class LearningType(Enum):
    """Types of learning that can occur."""
    REINFORCEMENT = "reinforcement"  # Learning from outcomes
    SUPERVISED = "supervised"  # Learning from feedback
    UNSUPERVISED = "unsupervised"  # Pattern discovery
    TRANSFER = "transfer"  # Applying knowledge to new domains
    META = "meta"  # Learning how to learn better


class ModelType(Enum):
    """Types of models that can be updated."""
    OUTCOME_PREDICTOR = "outcome_predictor"
    PATTERN_RECOGNIZER = "pattern_recognizer"
    RISK_ASSESSOR = "risk_assessor"
    PERFORMANCE_ESTIMATOR = "performance_estimator"
    CONTEXT_CLASSIFIER = "context_classifier"


@dataclass
class LearningUpdate:
    """Represents a learning update to be applied."""
    model_type: ModelType
    update_type: LearningType
    old_value: Any
    new_value: Any
    confidence: float
    evidence: List[str]
    timestamp: datetime
    learning_rate: float


@dataclass
class Experiment:
    """Represents a suggested experiment to test hypotheses."""
    id: str
    hypothesis: str
    experiment_design: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    success_criteria: List[str]
    risk_level: str
    estimated_duration: timedelta
    resource_requirements: List[str]


class LearningEngine:
    """
    Handles continuous learning and model updates.
    
    This class manages the evolution of internal models based on new evidence,
    feedback, and outcomes. It implements various learning strategies including
    reinforcement learning from outcomes, supervised learning from feedback,
    and meta-learning to improve the learning process itself.
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """
        Initialize LearningEngine.
        
        Args:
            learning_rate: Base learning rate for model updates
        """
        self.learning_rate = learning_rate
        self._models = {}
        self._learning_history = deque(maxlen=1000)  # Keep recent learning events
        self._learning_metrics = {
            "total_updates": 0,
            "successful_updates": 0,
            "learning_accuracy": 0.0,
            "model_performance": {},
            "last_updated": datetime.now()
        }
        
        # Learning parameters
        self._confidence_threshold = 0.6
        self._max_learning_rate = 0.5
        self._min_learning_rate = 0.01
        self._adaptation_factor = 1.2
        
        # Initialize basic models
        self._initialize_models()
        
    # ==========================================================================
    # CORE LEARNING METHODS
    # ==========================================================================
    
    def incorporate_feedback(self,
                           feedback_data: Dict[str, Any],
                           related_reflections: List[Any]) -> bool:
        """
        Incorporate external feedback into the learning system.
        
        Args:
            feedback_data: Feedback on past actions/decisions
            related_reflections: Related reflections for context
            
        Returns:
            True if feedback was successfully incorporated
        """
        try:
            # Extract feedback components
            feedback_type = feedback_data.get('type', 'general')
            feedback_value = feedback_data.get('value')
            confidence = feedback_data.get('confidence', 0.7)
            source = feedback_data.get('source', 'unknown')
            
            # Determine which models to update
            affected_models = self._identify_affected_models(feedback_data, related_reflections)
            
            updates_applied = 0
            
            for model_type in affected_models:
                # Calculate learning update
                learning_update = self._calculate_learning_update(
                    model_type, feedback_data, related_reflections
                )
                
                if learning_update and learning_update.confidence >= self._confidence_threshold:
                    # Apply the update
                    success = self._apply_learning_update(learning_update)
                    
                    if success:
                        updates_applied += 1
                        
                        # Record the learning event
                        self._record_learning_event(learning_update, source)
            
            # Update learning metrics
            self._update_learning_metrics(updates_applied > 0, updates_applied)
            
            logger.info(f"Incorporated feedback: {updates_applied} model updates applied")
            return updates_applied > 0
            
        except Exception as e:
            logger.error(f"Error incorporating feedback: {str(e)}")
            return False
    
    def update_models(self,
                     new_data: Dict[str, Any],
                     learning_rate: Optional[float] = None) -> bool:
        """
        Update internal models based on new evidence.
        
        Args:
            new_data: New evidence to incorporate into models
            learning_rate: Override default learning rate
            
        Returns:
            True if models were successfully updated
        """
        try:
            effective_learning_rate = learning_rate or self.learning_rate
            
            # Determine data type and relevance
            data_type = self._classify_data_type(new_data)
            relevant_models = self._identify_relevant_models(new_data, data_type)
            
            updates_applied = 0
            
            for model_type in relevant_models:
                # Calculate model update
                update = self._calculate_model_update(
                    model_type, new_data, effective_learning_rate
                )
                
                if update:
                    # Apply the update
                    success = self._apply_model_update(model_type, update)
                    
                    if success:
                        updates_applied += 1
                        
                        # Record the update
                        learning_update = LearningUpdate(
                            model_type=model_type,
                            update_type=LearningType.UNSUPERVISED,
                            old_value=update.get('old_value'),
                            new_value=update.get('new_value'),
                            confidence=update.get('confidence', 0.7),
                            evidence=[f"New data incorporated: {data_type}"],
                            timestamp=datetime.now(),
                            learning_rate=effective_learning_rate
                        )
                        
                        self._record_learning_event(learning_update, "model_update")
            
            # Update learning metrics
            self._update_learning_metrics(updates_applied > 0, updates_applied)
            
            logger.info(f"Updated models: {updates_applied} updates applied")
            return updates_applied > 0
            
        except Exception as e:
            logger.error(f"Error updating models: {str(e)}")
            return False
    
    def suggest_experiments(self,
                          current_knowledge: Dict[str, Any],
                          uncertainty_areas: List[str]) -> List[Dict[str, Any]]:
        """Suggest experiments to test hypotheses and improve understanding."""
        try:
            experiments = []
            
            # Generate experiments for each uncertainty area
            for area in uncertainty_areas:
                experiment_suggestions = self._generate_experiments_for_area(
                    area, current_knowledge
                )
                experiments.extend(experiment_suggestions)
            
            # Generate general exploration experiments
            exploration_experiments = self._generate_exploration_experiments(
                current_knowledge
            )
            experiments.extend(exploration_experiments)
            
            # Prioritize experiments
            prioritized_experiments = self._prioritize_experiments(experiments)
            
            # Convert to API format
            result = []
            for exp in prioritized_experiments[:10]:  # Top 10 experiments
                result.append({
                    "id": exp.id,
                    "hypothesis": exp.hypothesis,
                    "experiment_design": exp.experiment_design,
                    "expected_outcome": exp.expected_outcome,
                    "success_criteria": exp.success_criteria,
                    "risk_level": exp.risk_level,
                    "estimated_duration": str(exp.estimated_duration),
                    "resource_requirements": exp.resource_requirements,
                    "recommendation": f"Test hypothesis: {exp.hypothesis}"
                })
            
            logger.info(f"Generated {len(result)} experiment suggestions")
            return result
            
        except Exception as e:
            logger.error(f"Error suggesting experiments: {str(e)}")
            return []
    
    # ==========================================================================
    # MODEL MANAGEMENT METHODS (Simplified implementations for core functionality)
    # ==========================================================================
    
    def _initialize_models(self) -> None:
        """Initialize basic learning models."""
        # Simplified model initialization
        self._models[ModelType.OUTCOME_PREDICTOR] = {
            "accuracy": 0.65,
            "confidence": 0.7,
            "last_updated": datetime.now(),
            "update_count": 0
        }
        
        self._models[ModelType.PATTERN_RECOGNIZER] = {
            "accuracy": 0.6,
            "confidence": 0.65,
            "last_updated": datetime.now(),
            "update_count": 0
        }
        
        self._models[ModelType.RISK_ASSESSOR] = {
            "accuracy": 0.7,
            "confidence": 0.75,
            "last_updated": datetime.now(),
            "update_count": 0
        }
    
    def _identify_affected_models(self,
                                feedback_data: Dict[str, Any],
                                related_reflections: List[Any]) -> List[ModelType]:
        """Identify which models are affected by the feedback."""
        affected_models = []
        
        feedback_type = feedback_data.get('type', 'general')
        
        # Map feedback types to affected models
        if feedback_type in ['outcome', 'result', 'success', 'failure']:
            affected_models.append(ModelType.OUTCOME_PREDICTOR)
            
        if feedback_type in ['pattern', 'trend', 'recurring']:
            affected_models.append(ModelType.PATTERN_RECOGNIZER)
            
        if feedback_type in ['risk', 'danger', 'warning', 'threat']:
            affected_models.append(ModelType.RISK_ASSESSOR)
        
        # If no specific type, update all models with lower confidence
        if not affected_models:
            affected_models = list(ModelType)
            
        return affected_models
    
    def _calculate_learning_update(self,
                                 model_type: ModelType,
                                 feedback_data: Dict[str, Any],
                                 related_reflections: List[Any]) -> Optional[LearningUpdate]:
        """Calculate how to update a model based on feedback."""
        try:
            current_model = self._models.get(model_type)
            if not current_model:
                return None
            
            # Simple learning update calculation
            current_accuracy = current_model.get('accuracy', 0.5)
            feedback_confidence = feedback_data.get('confidence', 0.7)
            
            # Basic update logic - would be more sophisticated in practice
            if feedback_data.get('positive', True):
                new_accuracy = min(0.95, current_accuracy + 0.02)
            else:
                new_accuracy = max(0.3, current_accuracy - 0.03)
            
            return LearningUpdate(
                model_type=model_type,
                update_type=LearningType.SUPERVISED,
                old_value=current_accuracy,
                new_value=new_accuracy,
                confidence=feedback_confidence,
                evidence=[f"Feedback: {feedback_data.get('type', 'general')}"],
                timestamp=datetime.now(),
                learning_rate=self.learning_rate
            )
            
        except Exception as e:
            logger.error(f"Error calculating learning update: {str(e)}")
            return None
    
    def _apply_learning_update(self, learning_update: LearningUpdate) -> bool:
        """Apply a learning update to a model."""
        try:
            model = self._models.get(learning_update.model_type)
            if not model:
                return False
            
            # Apply the update using the specified learning rate
            old_value = learning_update.old_value
            new_value = learning_update.new_value
            learning_rate = learning_update.learning_rate
            
            # Weighted update
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                updated_value = old_value * (1 - learning_rate) + new_value * learning_rate
                model['accuracy'] = max(0.1, min(0.95, updated_value))
            
            model['last_updated'] = datetime.now()
            model['update_count'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying learning update: {str(e)}")
            return False
    
    def _record_learning_event(self, learning_update: LearningUpdate, source: str) -> None:
        """Record a learning event for tracking and analysis."""
        event = {
            'timestamp': learning_update.timestamp.isoformat(),
            'model_type': learning_update.model_type.value,
            'update_type': learning_update.update_type.value,
            'confidence': learning_update.confidence,
            'learning_rate': learning_update.learning_rate,
            'source': source,
            'evidence_count': len(learning_update.evidence)
        }
        
        self._learning_history.append(event)
    
    def _classify_data_type(self, data: Dict[str, Any]) -> str:
        """Classify the type of new data."""
        if 'outcome' in data or 'result' in data:
            return 'outcome_data'
        elif 'pattern' in data or 'trend' in data:
            return 'pattern_data'
        elif 'risk' in data or 'threat' in data:
            return 'risk_data'
        else:
            return 'general_data'
    
    def _identify_relevant_models(self, data: Dict[str, Any], data_type: str) -> List[ModelType]:
        """Identify which models are relevant for the new data."""
        relevant_models = []
        
        if data_type == 'outcome_data':
            relevant_models.append(ModelType.OUTCOME_PREDICTOR)
        elif data_type == 'pattern_data':
            relevant_models.append(ModelType.PATTERN_RECOGNIZER)
        elif data_type == 'risk_data':
            relevant_models.append(ModelType.RISK_ASSESSOR)
        else:
            relevant_models = list(ModelType)
        
        return relevant_models
    
    def _calculate_model_update(self,
                              model_type: ModelType,
                              data: Dict[str, Any],
                              learning_rate: float) -> Optional[Dict[str, Any]]:
        """Calculate how to update a model based on new data."""
        try:
            model = self._models.get(model_type)
            if not model:
                return None
            
            return {
                'old_value': model.get('accuracy', 0.5),
                'new_value': min(0.95, model.get('accuracy', 0.5) + 0.01),
                'confidence': 0.6,
                'learning_rate': learning_rate
            }
            
        except Exception as e:
            logger.error(f"Error calculating model update: {str(e)}")
            return None
    
    def _apply_model_update(self, model_type: ModelType, update: Dict[str, Any]) -> bool:
        """Apply an update to a model."""
        try:
            model = self._models.get(model_type)
            if not model:
                return False
            
            # Apply the update
            old_accuracy = model.get('accuracy', 0.5)
            new_accuracy = update.get('new_value', old_accuracy)
            learning_rate = update.get('learning_rate', self.learning_rate)
            
            # Weighted update
            updated_accuracy = old_accuracy * (1 - learning_rate) + new_accuracy * learning_rate
            
            model['accuracy'] = max(0.1, min(0.95, updated_accuracy))
            model['last_updated'] = datetime.now()
            model['update_count'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying model update: {str(e)}")
            return False
    
    # ==========================================================================
    # EXPERIMENT GENERATION (Simplified implementations)
    # ==========================================================================
    
    def _generate_experiments_for_area(self,
                                     area: str,
                                     current_knowledge: Dict[str, Any]) -> List[Experiment]:
        """Generate experiments for a specific uncertainty area."""
        experiments = []
        
        if area == "outcome_prediction":
            exp = Experiment(
                id=f"outcome_exp_{int(datetime.now().timestamp())}",
                hypothesis="Improved data collection will enhance prediction accuracy",
                experiment_design={"type": "controlled_comparison", "duration": 14},
                expected_outcome={"accuracy_improvement": 0.1},
                success_criteria=["5% improvement in accuracy"],
                risk_level="low",
                estimated_duration=timedelta(days=14),
                resource_requirements=["data_collection_tools"]
            )
            experiments.append(exp)
        
        return experiments
    
    def _generate_exploration_experiments(self, current_knowledge: Dict[str, Any]) -> List[Experiment]:
        """Generate general exploration experiments."""
        experiments = []
        
        exp = Experiment(
            id=f"exploration_exp_{int(datetime.now().timestamp())}",
            hypothesis="Cross-domain learning can improve overall performance",
            experiment_design={"type": "transfer_learning", "duration": 28},
            expected_outcome={"cross_domain_accuracy": 0.6},
            success_criteria=["Above 50% accuracy in new domain"],
            risk_level="medium",
            estimated_duration=timedelta(days=28),
            resource_requirements=["multi_domain_data"]
        )
        experiments.append(exp)
        
        return experiments
    
    def _prioritize_experiments(self, experiments: List[Experiment]) -> List[Experiment]:
        """Prioritize experiments based on potential impact and feasibility."""
        def calculate_priority_score(exp: Experiment) -> float:
            risk_multiplier = {'low': 1.0, 'medium': 0.8, 'high': 0.6}[exp.risk_level]
            duration_penalty = min(1.0, 30 / exp.estimated_duration.days)
            return risk_multiplier * duration_penalty
        
        return sorted(experiments, key=calculate_priority_score, reverse=True)
    
    # ==========================================================================
    # METRICS AND UTILITIES
    # ==========================================================================
    
    def _update_learning_metrics(self, success: bool, updates_count: int) -> None:
        """Update learning performance metrics."""
        self._learning_metrics["total_updates"] += updates_count
        
        if success:
            self._learning_metrics["successful_updates"] += 1
        
        # Update learning accuracy
        if self._learning_metrics["total_updates"] > 0:
            self._learning_metrics["learning_accuracy"] = (
                self._learning_metrics["successful_updates"] / 
                max(1, self._learning_metrics["total_updates"])
            )
        
        # Update model performance metrics
        for model_type, model in self._models.items():
            self._learning_metrics["model_performance"][model_type.value] = {
                "accuracy": model.get("accuracy", 0.5),
                "update_count": model.get("update_count", 0),
                "last_updated": model.get("last_updated", datetime.now()).isoformat()
            }
        
        self._learning_metrics["last_updated"] = datetime.now()
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get comprehensive learning metrics."""
        return {
            **self._learning_metrics,
            "learning_rate": self.learning_rate,
            "active_models": len(self._models),
            "learning_history_size": len(self._learning_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_model_status(self, model_type: Optional[ModelType] = None) -> Dict[str, Any]:
        """Get status of specific model or all models."""
        if model_type:
            model = self._models.get(model_type)
            return model if model else {}
        else:
            return {
                model_type.value: model for model_type, model in self._models.items()
            }
    
    def get_recent_learning_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning events."""
        return list(self._learning_history)[-limit:] if self._learning_history else []
