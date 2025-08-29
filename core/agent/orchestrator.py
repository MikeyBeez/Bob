"""
orchestrator.py - System orchestration and coordination

Coordinates all subsystems and manages their interactions.
Follows the proven modular pattern from Phases 1 & 2.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SystemCoordination:
    """Result of system coordination operations."""
    subsystems_active: int
    coordination_score: float
    bottlenecks: List[str]
    performance_metrics: Dict[str, float]
    timestamp: datetime


class SystemOrchestrator:
    """
    Orchestrates coordination between all Bob subsystems.
    
    Manages:
    - Inter-subsystem communication
    - Resource allocation
    - Performance monitoring
    - Error recovery
    """
    
    def __init__(self, db_core, fs_core, ollama_client, reflection_engine):
        """
        Initialize system orchestrator.
        
        Args:
            db_core: DatabaseCore instance
            fs_core: FileSystemCore instance  
            ollama_client: OllamaClient instance
            reflection_engine: ReflectionEngine instance
        """
        self.db_core = db_core
        self.fs_core = fs_core
        self.ollama_client = ollama_client
        self.reflection_engine = reflection_engine
        
        self.logger = logging.getLogger("SystemOrchestrator")
        self.active_operations = {}
        self.performance_history = []
        
    async def coordinate_systems(self, operation_type: str, context: Dict[str, Any]) -> SystemCoordination:
        """
        Coordinate subsystems for a specific operation.
        
        Args:
            operation_type: Type of operation to coordinate
            context: Context information for coordination
            
        Returns:
            SystemCoordination with coordination results
        """
        self.logger.info(f"🔄 Coordinating systems for: {operation_type}")
        
        start_time = datetime.now()
        bottlenecks = []
        metrics = {}
        
        try:
            # Check subsystem availability
            subsystems_ready = await self._check_subsystem_readiness()
            
            # Coordinate based on operation type
            if operation_type == "thinking":
                coordination = await self._coordinate_thinking(context)
            elif operation_type == "learning":
                coordination = await self._coordinate_learning(context)
            elif operation_type == "knowledge_retrieval":
                coordination = await self._coordinate_knowledge(context)
            else:
                coordination = await self._coordinate_generic(context)
            
            # Calculate performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            metrics["processing_time"] = processing_time
            metrics["subsystems_ready"] = len(subsystems_ready)
            
            # Calculate coordination score
            coordination_score = self._calculate_coordination_score(
                subsystems_ready, bottlenecks, processing_time
            )
            
            return SystemCoordination(
                subsystems_active=len(subsystems_ready),
                coordination_score=coordination_score,
                bottlenecks=bottlenecks,
                performance_metrics=metrics,
                timestamp=start_time
            )
            
        except Exception as e:
            self.logger.error(f"System coordination failed: {e}")
            return SystemCoordination(
                subsystems_active=0,
                coordination_score=0.0,
                bottlenecks=[str(e)],
                performance_metrics={},
                timestamp=start_time
            )
    
    async def _check_subsystem_readiness(self) -> List[str]:
        """Check which subsystems are ready for operations."""
        ready_systems = []
        
        # Check database
        if self.db_core:
            ready_systems.append("database")
        
        # Check filesystem
        if self.fs_core:
            ready_systems.append("filesystem")
        
        # Check Ollama
        if self.ollama_client:
            try:
                if await self.ollama_client.health_check():
                    ready_systems.append("ollama")
            except:
                pass
        
        # Check reflection engine
        if self.reflection_engine:
            ready_systems.append("reflection")
        
        return ready_systems
    
    async def _coordinate_thinking(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate subsystems for thinking operations."""
        # Thinking requires: ollama + reflection + optional knowledge
        coordination = {
            "primary_subsystem": "ollama",
            "supporting_subsystems": ["reflection"],
            "optional_subsystems": ["database", "filesystem"]
        }
        return coordination
    
    async def _coordinate_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate subsystems for learning operations."""
        # Learning requires: reflection + database + optional ollama
        coordination = {
            "primary_subsystem": "reflection", 
            "supporting_subsystems": ["database"],
            "optional_subsystems": ["ollama", "filesystem"]
        }
        return coordination
    
    async def _coordinate_knowledge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate subsystems for knowledge operations."""
        # Knowledge requires: database + filesystem + optional ollama
        coordination = {
            "primary_subsystem": "database",
            "supporting_subsystems": ["filesystem"],
            "optional_subsystems": ["ollama", "reflection"]
        }
        return coordination
    
    async def _coordinate_generic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generic coordination for unknown operations."""
        coordination = {
            "primary_subsystem": "database",
            "supporting_subsystems": [],
            "optional_subsystems": ["filesystem", "ollama", "reflection"]
        }
        return coordination
    
    def _calculate_coordination_score(self, ready_systems: List[str], 
                                    bottlenecks: List[str], 
                                    processing_time: float) -> float:
        """Calculate overall coordination effectiveness score."""
        base_score = len(ready_systems) / 4.0  # 4 total subsystems
        
        # Penalize for bottlenecks
        bottleneck_penalty = len(bottlenecks) * 0.1
        
        # Penalize for slow processing
        time_penalty = min(processing_time / 10.0, 0.3)  # Max 30% penalty
        
        score = max(0.0, base_score - bottleneck_penalty - time_penalty)
        return min(1.0, score)
    
    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor overall system performance."""
        # Collect metrics from all subsystems
        metrics = {
            "database_metrics": {},
            "filesystem_metrics": self.fs_core.get_metrics() if self.fs_core else {},
            "ollama_metrics": self.ollama_client.get_metrics() if self.ollama_client else {},
            "reflection_metrics": {}
        }
        
        if self.reflection_engine:
            try:
                metrics["reflection_metrics"] = await self.reflection_engine.get_learning_metrics()
            except:
                metrics["reflection_metrics"] = {}
        
        return metrics
    
    async def recover_from_errors(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Implement error recovery strategies."""
        recovery_actions = []
        
        # Analyze error context and determine recovery actions
        if "subsystem_failure" in error_context:
            failed_system = error_context["subsystem_failure"]
            recovery_actions.append(f"Attempting to reinitialize {failed_system}")
            
        if "timeout" in error_context:
            recovery_actions.append("Implementing timeout recovery")
            
        return {
            "recovery_actions": recovery_actions,
            "recovery_timestamp": datetime.now().isoformat(),
            "context": error_context
        }
