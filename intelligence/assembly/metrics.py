"""
metrics.py - Assembly metrics and performance tracking module

Handles comprehensive metrics collection for context assembly
performance, quality, and usage patterns. Clean API for analytics
and optimization insights.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import json


class MetricType(Enum):
    """Types of metrics collected."""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    USAGE = "usage"
    CACHE = "cache"
    SOURCE = "source"
    GRAPH = "graph"


@dataclass
class MetricEvent:
    """Represents a single metric event."""
    timestamp: datetime
    metric_type: MetricType
    metric_name: str
    value: float
    metadata: Dict[str, Any]
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_type': self.metric_type.value,
            'metric_name': self.metric_name,
            'value': self.value,
            'metadata': self.metadata,
            'session_id': self.session_id
        }


class AssemblyMetrics:
    """
    Comprehensive metrics collection for context assembly.
    
    Public API for tracking performance, quality, and usage metrics
    with analytics and reporting capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuration
        self.retention_days = self.config.get('retention_days', 30)
        self.max_events = self.config.get('max_events', 10000)
        self.enable_detailed_tracking = self.config.get('detailed_tracking', True)
        
        # Storage
        self.events: List[MetricEvent] = []
        self.session_metrics: Dict[str, Dict[str, Any]] = {}
        self.aggregated_metrics: Dict[str, Dict[str, float]] = {}
        
        # Current session
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        
        # Initialize aggregated metrics
        self._initialize_aggregated_metrics()
    
    def start_session(self, session_id: str) -> None:
        """
        Start a new metrics session.
        
        Args:
            session_id: Unique identifier for the session
        """
        self.current_session_id = session_id
        self.session_start_time = datetime.now()
        
        self.session_metrics[session_id] = {
            'start_time': self.session_start_time,
            'end_time': None,
            'events': [],
            'performance_metrics': {},
            'quality_metrics': {},
            'usage_metrics': {}
        }
        
        self._record_event(
            MetricType.USAGE,
            'session_start',
            1.0,
            {'session_id': session_id}
        )
    
    def end_session(self) -> Dict[str, Any]:
        """
        End current session and return summary.
        
        Returns:
            Session summary with key metrics
        """
        if not self.current_session_id:
            return {}
        
        session_data = self.session_metrics[self.current_session_id]
        session_data['end_time'] = datetime.now()
        
        # Calculate session duration
        duration = (session_data['end_time'] - session_data['start_time']).total_seconds()
        
        self._record_event(
            MetricType.USAGE,
            'session_end',
            duration,
            {'session_id': self.current_session_id, 'duration_seconds': duration}
        )
        
        # Generate session summary
        summary = self._generate_session_summary(self.current_session_id)
        
        # Reset current session
        self.current_session_id = None
        self.session_start_time = None
        
        return summary
    
    def record_performance_metric(self, metric_name: str, value: float, 
                                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric (e.g., 'assembly_time_ms')
            value: Metric value
            metadata: Additional metadata
        """
        self._record_event(MetricType.PERFORMANCE, metric_name, value, metadata or {})
        
        # Update session metrics
        if self.current_session_id:
            session_data = self.session_metrics[self.current_session_id]
            perf_metrics = session_data['performance_metrics']
            
            if metric_name not in perf_metrics:
                perf_metrics[metric_name] = []
            perf_metrics[metric_name].append(value)
    
    def record_quality_metric(self, metric_name: str, value: float,
                             metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a quality metric.
        
        Args:
            metric_name: Name of the metric (e.g., 'relevance_score')
            value: Metric value (0.0-1.0)
            metadata: Additional metadata
        """
        self._record_event(MetricType.QUALITY, metric_name, value, metadata or {})
        
        # Update session metrics
        if self.current_session_id:
            session_data = self.session_metrics[self.current_session_id]
            quality_metrics = session_data['quality_metrics']
            
            if metric_name not in quality_metrics:
                quality_metrics[metric_name] = []
            quality_metrics[metric_name].append(value)
    
    def record_usage_metric(self, metric_name: str, value: float,
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a usage metric.
        
        Args:
            metric_name: Name of the metric (e.g., 'context_requests')
            value: Metric value
            metadata: Additional metadata
        """
        self._record_event(MetricType.USAGE, metric_name, value, metadata or {})
        
        # Update session metrics
        if self.current_session_id:
            session_data = self.session_metrics[self.current_session_id]
            usage_metrics = session_data['usage_metrics']
            
            if metric_name not in usage_metrics:
                usage_metrics[metric_name] = []
            usage_metrics[metric_name].append(value)
    
    def record_cache_metrics(self, cache_stats: Dict[str, Any]) -> None:
        """Record cache performance metrics."""
        for metric_name, value in cache_stats.items():
            if isinstance(value, (int, float)):
                self._record_event(
                    MetricType.CACHE,
                    f'cache_{metric_name}',
                    float(value),
                    {'source': 'cache_manager'}
                )
    
    def record_source_metrics(self, source_stats: Dict[str, Any]) -> None:
        """Record source performance metrics."""
        for metric_name, value in source_stats.items():
            if isinstance(value, (int, float)):
                self._record_event(
                    MetricType.SOURCE,
                    f'source_{metric_name}',
                    float(value),
                    {'source': 'source_manager'}
                )
    
    def record_graph_metrics(self, graph_stats: Dict[str, Any]) -> None:
        """Record graph traversal metrics."""
        for metric_name, value in graph_stats.items():
            if isinstance(value, (int, float)):
                self._record_event(
                    MetricType.GRAPH,
                    f'graph_{metric_name}',
                    float(value),
                    {'source': 'graph_builder'}
                )
    
    def get_performance_summary(self, time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get performance metrics summary.
        
        Args:
            time_window_hours: Time window for analysis (None = all time)
            
        Returns:
            Performance summary with statistics
        """
        events = self._filter_events_by_time(MetricType.PERFORMANCE, time_window_hours)
        
        if not events:
            return {'message': 'No performance data available'}
        
        # Group by metric name
        metrics_by_name = {}
        for event in events:
            if event.metric_name not in metrics_by_name:
                metrics_by_name[event.metric_name] = []
            metrics_by_name[event.metric_name].append(event.value)
        
        # Calculate statistics
        summary = {}
        for metric_name, values in metrics_by_name.items():
            summary[metric_name] = {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
            }
        
        return {
            'time_window_hours': time_window_hours,
            'total_events': len(events),
            'metrics': summary,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_quality_trends(self, time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get quality metrics trends.
        
        Args:
            time_window_hours: Time window for analysis
            
        Returns:
            Quality trends and analysis
        """
        events = self._filter_events_by_time(MetricType.QUALITY, time_window_hours)
        
        if not events:
            return {'message': 'No quality data available'}
        
        # Sort by timestamp
        events.sort(key=lambda x: x.timestamp)
        
        # Calculate trends
        trends = {}
        for event in events:
            if event.metric_name not in trends:
                trends[event.metric_name] = {
                    'values': [],
                    'timestamps': []
                }
            
            trends[event.metric_name]['values'].append(event.value)
            trends[event.metric_name]['timestamps'].append(event.timestamp)
        
        # Calculate trend direction
        trend_analysis = {}
        for metric_name, data in trends.items():
            values = data['values']
            if len(values) >= 2:
                # Simple linear trend
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                trend_direction = 'improving' if statistics.mean(second_half) > statistics.mean(first_half) else 'declining'
                trend_magnitude = abs(statistics.mean(second_half) - statistics.mean(first_half))
            else:
                trend_direction = 'insufficient_data'
                trend_magnitude = 0.0
            
            trend_analysis[metric_name] = {
                'current_value': values[-1],
                'trend_direction': trend_direction,
                'trend_magnitude': trend_magnitude,
                'sample_count': len(values)
            }
        
        return {
            'time_window_hours': time_window_hours,
            'trend_analysis': trend_analysis,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_usage_analytics(self, time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get usage analytics and patterns.
        
        Args:
            time_window_hours: Time window for analysis
            
        Returns:
            Usage analytics with patterns and insights
        """
        events = self._filter_events_by_time(MetricType.USAGE, time_window_hours)
        
        if not events:
            return {'message': 'No usage data available'}
        
        # Calculate usage patterns
        hourly_usage = {}
        daily_usage = {}
        session_count = 0
        
        for event in events:
            hour = event.timestamp.hour
            day = event.timestamp.date()
            
            if hour not in hourly_usage:
                hourly_usage[hour] = 0
            hourly_usage[hour] += 1
            
            if day not in daily_usage:
                daily_usage[day] = 0
            daily_usage[day] += 1
            
            if event.metric_name == 'session_start':
                session_count += 1
        
        # Find peak usage hours
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else (0, 0)
        
        return {
            'time_window_hours': time_window_hours,
            'total_events': len(events),
            'session_count': session_count,
            'peak_usage_hour': peak_hour[0],
            'peak_usage_events': peak_hour[1],
            'hourly_distribution': dict(sorted(hourly_usage.items())),
            'daily_usage': {str(k): v for k, v in sorted(daily_usage.items())},
            'average_events_per_day': sum(daily_usage.values()) / max(1, len(daily_usage)),
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report.
        
        Returns:
            Health report with status and recommendations
        """
        # Get recent performance data
        perf_summary = self.get_performance_summary(time_window_hours=24)
        quality_trends = self.get_quality_trends(time_window_hours=24)
        usage_analytics = self.get_usage_analytics(time_window_hours=24)
        
        # Analyze health indicators
        health_score = 100.0
        warnings = []
        recommendations = []
        
        # Check performance indicators
        if 'metrics' in perf_summary:
            for metric_name, stats in perf_summary['metrics'].items():
                if 'time_ms' in metric_name and stats['mean'] > 1000:  # >1 second
                    health_score -= 10
                    warnings.append(f"Slow performance: {metric_name} averaging {stats['mean']:.1f}ms")
                    recommendations.append(f"Optimize {metric_name.replace('_', ' ')}")
        
        # Check quality trends
        if 'trend_analysis' in quality_trends:
            for metric_name, trend in quality_trends['trend_analysis'].items():
                if trend['trend_direction'] == 'declining' and trend['trend_magnitude'] > 0.1:
                    health_score -= 15
                    warnings.append(f"Quality declining: {metric_name}")
                    recommendations.append(f"Investigate {metric_name.replace('_', ' ')} degradation")
        
        # Check usage patterns
        if usage_analytics.get('session_count', 0) == 0:
            health_score -= 20
            warnings.append("No recent usage detected")
            recommendations.append("Check system availability")
        
        # Determine health status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 60:
            status = "fair"
        else:
            status = "poor"
        
        return {
            'health_score': health_score,
            'status': status,
            'warnings': warnings,
            'recommendations': recommendations,
            'performance_summary': perf_summary,
            'quality_trends': quality_trends,
            'usage_analytics': usage_analytics,
            'generated_at': datetime.now().isoformat()
        }
    
    def cleanup_old_events(self) -> int:
        """
        Clean up old events based on retention policy.
        
        Returns:
            Number of events removed
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        old_events_count = len([e for e in self.events if e.timestamp < cutoff_date])
        self.events = [e for e in self.events if e.timestamp >= cutoff_date]
        
        # Also cleanup old sessions
        old_sessions = [
            session_id for session_id, data in self.session_metrics.items()
            if data['start_time'] < cutoff_date
        ]
        
        for session_id in old_sessions:
            del self.session_metrics[session_id]
        
        return old_events_count + len(old_sessions)
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """
        Export metrics data.
        
        Args:
            format_type: Export format ('json' or 'csv')
            
        Returns:
            Formatted metrics data
        """
        if format_type.lower() == 'json':
            return json.dumps({
                'events': [event.to_dict() for event in self.events],
                'session_metrics': {
                    k: {**v, 'start_time': v['start_time'].isoformat(),
                        'end_time': v['end_time'].isoformat() if v['end_time'] else None}
                    for k, v in self.session_metrics.items()
                },
                'aggregated_metrics': self.aggregated_metrics,
                'export_timestamp': datetime.now().isoformat()
            }, indent=2)
        
        # CSV format would be implemented here
        return "CSV export not implemented yet"
    
    def _record_event(self, metric_type: MetricType, metric_name: str, 
                     value: float, metadata: Dict[str, Any]) -> None:
        """Record a metric event."""
        event = MetricEvent(
            timestamp=datetime.now(),
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            metadata=metadata,
            session_id=self.current_session_id
        )
        
        self.events.append(event)
        
        # Add to session if active
        if self.current_session_id and self.current_session_id in self.session_metrics:
            self.session_metrics[self.current_session_id]['events'].append(event)
        
        # Update aggregated metrics
        self._update_aggregated_metrics(metric_type, metric_name, value)
        
        # Cleanup if too many events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def _filter_events_by_time(self, metric_type: MetricType, 
                              hours: Optional[int]) -> List[MetricEvent]:
        """Filter events by type and time window."""
        events = [e for e in self.events if e.metric_type == metric_type]
        
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            events = [e for e in events if e.timestamp >= cutoff]
        
        return events
    
    def _generate_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate summary for a session."""
        session_data = self.session_metrics.get(session_id, {})
        
        if not session_data:
            return {}
        
        duration = 0
        if session_data.get('end_time') and session_data.get('start_time'):
            duration = (session_data['end_time'] - session_data['start_time']).total_seconds()
        
        return {
            'session_id': session_id,
            'duration_seconds': duration,
            'events_count': len(session_data.get('events', [])),
            'performance_summary': {
                name: {
                    'mean': statistics.mean(values),
                    'max': max(values)
                } for name, values in session_data.get('performance_metrics', {}).items()
            },
            'quality_summary': {
                name: {
                    'mean': statistics.mean(values),
                    'min': min(values)
                } for name, values in session_data.get('quality_metrics', {}).items()
            }
        }
    
    def _initialize_aggregated_metrics(self) -> None:
        """Initialize aggregated metrics structure."""
        for metric_type in MetricType:
            self.aggregated_metrics[metric_type.value] = {}
    
    def _update_aggregated_metrics(self, metric_type: MetricType, 
                                  metric_name: str, value: float) -> None:
        """Update aggregated metrics with new value."""
        type_key = metric_type.value
        
        if metric_name not in self.aggregated_metrics[type_key]:
            self.aggregated_metrics[type_key][metric_name] = {
                'count': 0,
                'sum': 0.0,
                'min': float('inf'),
                'max': float('-inf')
            }
        
        metrics = self.aggregated_metrics[type_key][metric_name]
        metrics['count'] += 1
        metrics['sum'] += value
        metrics['min'] = min(metrics['min'], value)
        metrics['max'] = max(metrics['max'], value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics overview."""
        return {
            'total_events': len(self.events),
            'active_session': self.current_session_id,
            'session_count': len(self.session_metrics),
            'aggregated_metrics': self.aggregated_metrics,
            'retention_days': self.retention_days,
            'max_events': self.max_events
        }
