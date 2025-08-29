"""
confidence_calibrator.py - Calibrate confidence levels based on historical accuracy

This module adjusts confidence levels based on historical performance,
ensuring that confidence scores accurately reflect actual prediction accuracy.
It implements various calibration techniques and tracks calibration metrics.
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging
import math
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CalibrationType(Enum):
    """Types of confidence calibration."""
    PLATT_SCALING = "platt_scaling"
    ISOTONIC_REGRESSION = "isotonic_regression"
    TEMPERATURE_SCALING = "temperature_scaling"
    BAYESIAN_CALIBRATION = "bayesian_calibration"
    HISTORICAL_FREQUENCY = "historical_frequency"


@dataclass
class CalibrationData:
    """Data point for calibration analysis."""
    predicted_confidence: float
    actual_outcome: bool  # True if prediction was correct
    domain: Optional[str] = None
    timestamp: datetime = None
    prediction_type: Optional[str] = None


@dataclass
class CalibrationResult:
    """Result of confidence calibration."""
    original_confidence: float
    calibrated_confidence: float
    calibration_method: CalibrationType
    improvement_score: float
    reliability_diagram_data: Dict[str, Any]
    timestamp: datetime


class ConfidenceCalibrator:
    """
    Calibrates confidence levels based on historical accuracy.
    
    This class analyzes the relationship between predicted confidence and
    actual accuracy to improve the reliability of confidence scores.
    It implements various calibration techniques and provides metrics
    to track calibration quality over time.
    """
    
    def __init__(self, default_method: CalibrationType = CalibrationType.HISTORICAL_FREQUENCY):
        """
        Initialize ConfidenceCalibrator.
        
        Args:
            default_method: Default calibration method to use
        """
        self.default_method = default_method
        self._calibration_data = deque(maxlen=10000)  # Store recent calibration data
        self._domain_calibrators = {}  # Domain-specific calibration parameters
        self._calibration_metrics = {
            "total_calibrations": 0,
            "accuracy_improvements": 0,
            "avg_improvement": 0.0,
            "calibration_error": 0.0,
            "reliability_score": 0.0,
            "last_updated": datetime.now()
        }
        
        # Calibration parameters
        self._min_samples_for_calibration = 10
        self._confidence_bins = 10  # Number of bins for reliability diagrams
        self._smoothing_factor = 0.1
        
    # ==========================================================================
    # CORE CALIBRATION METHODS
    # ==========================================================================
    
    def calibrate_domain_confidence(self,
                                  domain: str,
                                  domain_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Adjust confidence levels based on historical accuracy.
        
        Args:
            domain: Domain to calibrate confidence for
            domain_history: Historical data for the domain
            
        Returns:
            Confidence calibration results
        """
        try:
            if not domain_history or len(domain_history) < self._min_samples_for_calibration:
                return {"error": "insufficient_data", "samples": len(domain_history)}
            
            # Extract calibration data from history
            calibration_data = self._extract_calibration_data(domain_history, domain)
            
            if len(calibration_data) < self._min_samples_for_calibration:
                return {"error": "insufficient_calibration_data", "samples": len(calibration_data)}
            
            # Calculate calibration metrics
            calibration_error = self._calculate_calibration_error(calibration_data)
            reliability_score = self._calculate_reliability_score(calibration_data)
            
            # Generate calibration mapping
            calibration_mapping = self._generate_calibration_mapping(
                calibration_data, self.default_method
            )
            
            # Calculate improvement metrics
            before_accuracy = self._calculate_raw_accuracy(calibration_data)
            after_accuracy = self._estimate_calibrated_accuracy(calibration_data, calibration_mapping)
            improvement = after_accuracy - before_accuracy
            
            # Store domain calibration parameters
            self._domain_calibrators[domain] = {
                "mapping": calibration_mapping,
                "method": self.default_method,
                "samples": len(calibration_data),
                "calibration_error": calibration_error,
                "reliability_score": reliability_score,
                "improvement": improvement,
                "last_updated": datetime.now()
            }
            
            # Update global metrics
            self._update_calibration_metrics(improvement > 0, improvement)
            
            result = {
                "domain": domain,
                "calibration_error": calibration_error,
                "reliability_score": reliability_score,
                "accuracy_improvement": improvement,
                "samples_used": len(calibration_data),
                "calibration_method": self.default_method.value,
                "confidence_mapping": calibration_mapping,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Calibrated confidence for domain {domain}: {improvement:.3f} accuracy improvement")
            return result
            
        except Exception as e:
            logger.error(f"Error calibrating domain confidence: {str(e)}")
            return {"error": str(e), "domain": domain}
    
    def calibrate_confidence_value(self,
                                  confidence: float,
                                  domain: Optional[str] = None,
                                  context: Optional[Dict[str, Any]] = None) -> float:
        """Calibrate a single confidence value based on domain calibration."""
        try:
            # Use domain-specific calibration if available
            if domain and domain in self._domain_calibrators:
                calibrator = self._domain_calibrators[domain]
                mapping = calibrator["mapping"]
                
                # Apply calibration mapping
                calibrated = self._apply_calibration_mapping(confidence, mapping)
                
                logger.debug(f"Calibrated confidence {confidence:.3f} -> {calibrated:.3f} for domain {domain}")
                return calibrated
            
            # Fallback to global calibration
            global_mapping = self._get_global_calibration_mapping()
            if global_mapping:
                return self._apply_calibration_mapping(confidence, global_mapping)
            
            # No calibration available - return original
            return confidence
            
        except Exception as e:
            logger.error(f"Error calibrating confidence value: {str(e)}")
            return confidence  # Return original on error
    
    def identify_uncertainty_areas(self) -> List[str]:
        """Identify areas with high uncertainty or low confidence."""
        try:
            uncertainty_areas = []
            
            # Analyze domain-specific calibration quality
            for domain, calibrator in self._domain_calibrators.items():
                calibration_error = calibrator.get("calibration_error", 0)
                reliability_score = calibrator.get("reliability_score", 1.0)
                
                # High calibration error or low reliability indicates uncertainty
                if calibration_error > 0.15 or reliability_score < 0.7:
                    uncertainty_areas.append(domain)
            
            # Add general areas if overall performance is poor
            overall_error = self._calibration_metrics.get("calibration_error", 0)
            if overall_error > 0.2:
                uncertainty_areas.append("overall_prediction_accuracy")
            
            return list(set(uncertainty_areas))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error identifying uncertainty areas: {str(e)}")
            return []
    
    def calculate_accuracy_improvement(self, timeframe: timedelta) -> float:
        """Calculate accuracy improvement over timeframe."""
        try:
            # Get calibration data within timeframe
            recent_data = self._filter_calibration_data(time_window=timeframe)
            
            if len(recent_data) < 5:  # Need minimum data
                return 0.0
            
            # Calculate improvement based on calibration error reduction
            calibration_error = self._calculate_calibration_error(recent_data)
            
            # Convert calibration error to improvement score
            # Lower error = higher improvement
            max_possible_error = 0.5  # Theoretical maximum for random predictions
            improvement = max(0, (max_possible_error - calibration_error) / max_possible_error)
            
            return improvement
            
        except Exception as e:
            logger.error(f"Error calculating accuracy improvement: {str(e)}")
            return 0.0
    
    # ==========================================================================
    # CALIBRATION CALCULATION METHODS
    # ==========================================================================
    
    def _extract_calibration_data(self,
                                domain_history: List[Dict[str, Any]],
                                domain: str) -> List[CalibrationData]:
        """Extract calibration data points from domain history."""
        calibration_data = []
        
        try:
            for item in domain_history:
                # Look for prediction/outcome pairs
                predicted_conf = None
                actual_outcome = None
                
                # Try different formats for confidence and outcome
                if 'predicted_confidence' in item and 'actual_outcome' in item:
                    predicted_conf = item['predicted_confidence']
                    actual_outcome = item['actual_outcome']
                elif 'confidence' in item and 'success' in item:
                    predicted_conf = item['confidence']
                    actual_outcome = item['success']
                elif 'confidence' in item and 'outcome_type' in item:
                    predicted_conf = item['confidence']
                    actual_outcome = item['outcome_type'] in ['success', 'SUCCESS']
                
                if predicted_conf is not None and actual_outcome is not None:
                    # Validate confidence value
                    if isinstance(predicted_conf, (int, float)) and 0 <= predicted_conf <= 1:
                        calibration_point = CalibrationData(
                            predicted_confidence=float(predicted_conf),
                            actual_outcome=bool(actual_outcome),
                            domain=domain,
                            timestamp=item.get('timestamp', datetime.now()),
                            prediction_type=item.get('prediction_type')
                        )
                        calibration_data.append(calibration_point)
            
        except Exception as e:
            logger.error(f"Error extracting calibration data: {str(e)}")
        
        return calibration_data
    
    def _calculate_calibration_error(self, data_points: List[CalibrationData]) -> float:
        """Calculate Expected Calibration Error (ECE)."""
        try:
            if not data_points:
                return 0.0
            
            # Create confidence bins
            bin_size = 1.0 / self._confidence_bins
            total_error = 0.0
            total_samples = len(data_points)
            
            for i in range(self._confidence_bins):
                bin_start = i * bin_size
                bin_end = (i + 1) * bin_size
                
                # Get points in this bin
                bin_points = [
                    point for point in data_points
                    if bin_start <= point.predicted_confidence < bin_end or 
                    (i == self._confidence_bins - 1 and point.predicted_confidence == 1.0)
                ]
                
                if bin_points:
                    # Calculate average confidence and accuracy in bin
                    avg_confidence = sum(p.predicted_confidence for p in bin_points) / len(bin_points)
                    accuracy = sum(1 for p in bin_points if p.actual_outcome) / len(bin_points)
                    
                    # Weight by bin size
                    bin_weight = len(bin_points) / total_samples
                    bin_error = abs(avg_confidence - accuracy)
                    
                    total_error += bin_weight * bin_error
            
            return total_error
            
        except Exception as e:
            logger.error(f"Error calculating calibration error: {str(e)}")
            return 1.0  # Return maximum error on failure
    
    def _calculate_reliability_score(self, data_points: List[CalibrationData]) -> float:
        """Calculate overall reliability score (1 - calibration_error)."""
        calibration_error = self._calculate_calibration_error(data_points)
        return max(0.0, 1.0 - calibration_error)
    
    def _generate_calibration_mapping(self,
                                    data_points: List[CalibrationData],
                                    method: CalibrationType) -> Dict[str, Any]:
        """Generate confidence calibration mapping using specified method."""
        try:
            if method == CalibrationType.HISTORICAL_FREQUENCY:
                return self._generate_frequency_mapping(data_points)
            else:
                # Fallback to historical frequency
                return self._generate_frequency_mapping(data_points)
                
        except Exception as e:
            logger.error(f"Error generating calibration mapping: {str(e)}")
            return {"type": "identity"}  # Identity mapping on error
    
    def _generate_frequency_mapping(self, data_points: List[CalibrationData]) -> Dict[str, Any]:
        """Generate calibration mapping based on historical frequencies."""
        mapping = {"type": "frequency", "bins": []}
        
        try:
            bin_size = 1.0 / self._confidence_bins
            
            for i in range(self._confidence_bins):
                bin_start = i * bin_size
                bin_end = (i + 1) * bin_size
                bin_center = (bin_start + bin_end) / 2
                
                # Get points in this bin
                bin_points = [
                    point for point in data_points
                    if bin_start <= point.predicted_confidence < bin_end or 
                    (i == self._confidence_bins - 1 and point.predicted_confidence == 1.0)
                ]
                
                if bin_points:
                    # Calculate empirical accuracy for this confidence range
                    accuracy = sum(1 for p in bin_points if p.actual_outcome) / len(bin_points)
                    
                    # Apply smoothing to avoid overfitting
                    smoothed_accuracy = (
                        accuracy * len(bin_points) + bin_center * self._smoothing_factor
                    ) / (len(bin_points) + self._smoothing_factor)
                    
                    mapping["bins"].append({
                        "range": [bin_start, bin_end],
                        "input_center": bin_center,
                        "output_confidence": smoothed_accuracy,
                        "sample_count": len(bin_points)
                    })
                else:
                    # No data in bin - use linear interpolation
                    mapping["bins"].append({
                        "range": [bin_start, bin_end],
                        "input_center": bin_center,
                        "output_confidence": bin_center,  # Identity mapping
                        "sample_count": 0
                    })
            
        except Exception as e:
            logger.error(f"Error generating frequency mapping: {str(e)}")
            mapping = {"type": "identity"}  # Fallback
        
        return mapping
    
    def _apply_calibration_mapping(self, confidence: float, mapping: Dict[str, Any]) -> float:
        """Apply calibration mapping to a confidence value."""
        try:
            mapping_type = mapping.get("type", "identity")
            
            if mapping_type == "identity":
                return confidence
            
            elif mapping_type == "frequency":
                # Find appropriate bin and return calibrated confidence
                bins = mapping.get("bins", [])
                
                for bin_data in bins:
                    bin_range = bin_data["range"]
                    if bin_range[0] <= confidence < bin_range[1] or \
                       (confidence == 1.0 and bin_range[1] == 1.0):
                        return bin_data["output_confidence"]
                
                # Fallback - return original confidence
                return confidence
            
            else:
                return confidence  # Unknown type - return original
                
        except Exception as e:
            logger.error(f"Error applying calibration mapping: {str(e)}")
            return confidence
    
    # ==========================================================================
    # SUPPORTING METHODS
    # ==========================================================================
    
    def _calculate_raw_accuracy(self, data_points: List[CalibrationData]) -> float:
        """Calculate raw prediction accuracy."""
        if not data_points:
            return 0.0
        
        correct_predictions = sum(1 for p in data_points if p.actual_outcome)
        return correct_predictions / len(data_points)
    
    def _estimate_calibrated_accuracy(self,
                                    data_points: List[CalibrationData],
                                    calibration_mapping: Dict[str, Any]) -> float:
        """Estimate accuracy after applying calibration."""
        if not data_points:
            return 0.0
        
        try:
            # Apply calibration to each point and calculate new accuracy estimate
            calibrated_confidences = []
            
            for point in data_points:
                calibrated_conf = self._apply_calibration_mapping(
                    point.predicted_confidence, calibration_mapping
                )
                calibrated_confidences.append(calibrated_conf)
            
            # Simple accuracy estimate based on average calibrated confidence
            # (This is a simplification - proper evaluation would need separate test set)
            avg_calibrated_confidence = sum(calibrated_confidences) / len(calibrated_confidences)
            return avg_calibrated_confidence
            
        except Exception as e:
            logger.error(f"Error estimating calibrated accuracy: {str(e)}")
            return self._calculate_raw_accuracy(data_points)
    
    def _filter_calibration_data(self,
                               domain: Optional[str] = None,
                               time_window: Optional[timedelta] = None) -> List[CalibrationData]:
        """Filter calibration data by domain and/or time window."""
        filtered_data = list(self._calibration_data)
        
        # Filter by domain
        if domain:
            filtered_data = [p for p in filtered_data if p.domain == domain]
        
        # Filter by time window
        if time_window:
            cutoff_time = datetime.now() - time_window
            filtered_data = [p for p in filtered_data if p.timestamp and p.timestamp >= cutoff_time]
        
        return filtered_data
    
    def _get_global_calibration_mapping(self) -> Optional[Dict[str, Any]]:
        """Get global calibration mapping if available."""
        if len(self._calibration_data) >= self._min_samples_for_calibration:
            # Generate global calibration mapping
            global_data = list(self._calibration_data)
            return self._generate_calibration_mapping(global_data, self.default_method)
        
        return None
    
    def _update_calibration_metrics(self, improved: bool, improvement_value: float) -> None:
        """Update calibration performance metrics."""
        self._calibration_metrics["total_calibrations"] += 1
        
        if improved:
            self._calibration_metrics["accuracy_improvements"] += 1
        
        # Update average improvement
        current_avg = self._calibration_metrics["avg_improvement"]
        total_calibrations = self._calibration_metrics["total_calibrations"]
        
        new_avg = ((current_avg * (total_calibrations - 1)) + improvement_value) / total_calibrations
        self._calibration_metrics["avg_improvement"] = new_avg
        
        self._calibration_metrics["last_updated"] = datetime.now()
    
    # ==========================================================================
    # METRICS AND REPORTING
    # ==========================================================================
    
    def get_calibration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive calibration metrics."""
        return {
            **self._calibration_metrics,
            "total_calibration_samples": len(self._calibration_data),
            "domains_calibrated": len(self._domain_calibrators),
            "default_method": self.default_method.value,
            "improvement_rate": (
                self._calibration_metrics["accuracy_improvements"] / 
                max(1, self._calibration_metrics["total_calibrations"])
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_domain_calibration_status(self, domain: str) -> Dict[str, Any]:
        """Get calibration status for a specific domain."""
        if domain in self._domain_calibrators:
            calibrator = self._domain_calibrators[domain].copy()
            calibrator["last_updated"] = calibrator["last_updated"].isoformat()
            return calibrator
        else:
            return {
                "domain": domain,
                "status": "not_calibrated",
                "reason": "insufficient_data"
            }
