"""
intelligence_loop.py - Canonical intelligence loop implementation

Implements the core intelligence loop that coordinates thinking, acting, and learning.
This is the heart of the LLM-as-Kernel architecture.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class LoopPhase(Enum):
    """Phases of the intelligence loop."""
    PERCEIVE = "perceive"
    THINK = "think"  
    ACT = "act"
    REFLECT = "reflect"
    LEARN = "learn"


@dataclass
class LoopIteration:
    """A single iteration of the intelligence loop."""
    id: str
    phase: LoopPhase
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration: float
    success: bool
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class LoopMetrics:
    """Metrics for intelligence loop performance."""
    total_iterations: int
    successful_iterations: int
    average_duration: float
    phase_durations: Dict[str, float]
    success_rate: float
    learning_rate: float
    timestamp: datetime


class IntelligenceLoop:
    """
    Implements the canonical intelligence loop for Bob.
    
    The loop consists of:
    1. PERCEIVE - Gather input and context
    2. THINK - Process information and generate responses
    3. ACT - Execute actions or generate outputs
    4. REFLECT - Analyze outcomes and performance
    5. LEARN - Update mental models and improve
    """
    
    def __init__(self, orchestrator, reflection_engine):
        """
        Initialize intelligence loop.
        
        Args:
            orchestrator: SystemOrchestrator instance
            reflection_engine: ReflectionEngine instance
        """
        self.orchestrator = orchestrator
        self.reflection_engine = reflection_engine
        
        self.logger = logging.getLogger("IntelligenceLoop")
        self.active = False
        self.iterations = []
        self.current_phase = None
        self.loop_metrics = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "phase_times": {}
        }
    
    async def run_single_iteration(self, input_data: Dict[str, Any]) -> LoopIteration:
        """
        Run a single iteration of the intelligence loop.
        
        Args:
            input_data: Input data for the iteration
            
        Returns:
            LoopIteration with results
        """
        iteration_id = f"loop_{int(datetime.now().timestamp())}"
        start_time = datetime.now()
        
        self.logger.info(f"🔄 Starting intelligence loop iteration: {iteration_id}")
        
        try:
            # Phase 1: PERCEIVE
            perception_data = await self._perceive_phase(input_data)
            
            # Phase 2: THINK
            thinking_data = await self._think_phase(perception_data)
            
            # Phase 3: ACT
            action_data = await self._act_phase(thinking_data)
            
            # Phase 4: REFLECT
            reflection_data = await self._reflect_phase(action_data)
            
            # Phase 5: LEARN
            learning_data = await self._learn_phase(reflection_data)
            
            # Compile results
            duration = (datetime.now() - start_time).total_seconds()
            
            iteration = LoopIteration(
                id=iteration_id,
                phase=LoopPhase.LEARN,  # Final phase
                input_data=input_data,
                output_data={
                    "perception": perception_data,
                    "thinking": thinking_data,
                    "action": action_data,
                    "reflection": reflection_data,
                    "learning": learning_data
                },
                duration=duration,
                success=True,
                timestamp=start_time,
                metadata={
                    "phases_completed": 5,
                    "total_duration": duration
                }
            )
            
            self.iterations.append(iteration)
            self.loop_metrics["total_cycles"] += 1
            self.loop_metrics["successful_cycles"] += 1
            
            self.logger.info(f"✅ Intelligence loop iteration completed in {duration:.2f}s")
            return iteration
            
        except Exception as e:
            self.logger.error(f"Intelligence loop iteration failed: {e}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            iteration = LoopIteration(
                id=iteration_id,
                phase=self.current_phase or LoopPhase.PERCEIVE,
                input_data=input_data,
                output_data={"error": str(e)},
                duration=duration,
                success=False,
                timestamp=start_time,
                metadata={"error": str(e)}
            )
            
            self.iterations.append(iteration)
            self.loop_metrics["total_cycles"] += 1
            
            return iteration
    
    async def _perceive_phase(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PERCEIVE phase: Gather and organize input information.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Organized perception data
        """
        self.current_phase = LoopPhase.PERCEIVE
        start_time = datetime.now()
        
        try:
            # Coordinate with orchestrator for context gathering
            coordination = await self.orchestrator.coordinate_systems("perception", input_data)
            
            # Organize perception data
            perception_data = {
                "raw_input": input_data,
                "context": input_data.get("context", {}),
                "timestamp": start_time.isoformat(),
                "coordination_score": coordination.coordination_score,
                "available_subsystems": coordination.subsystems_active
            }
            
            # Track phase timing
            duration = (datetime.now() - start_time).total_seconds()
            self.loop_metrics["phase_times"]["perceive"] = duration
            
            return perception_data
            
        except Exception as e:
            self.logger.error(f"Perception phase failed: {e}")
            return {"error": str(e), "phase": "perceive"}
    
    async def _think_phase(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        THINK phase: Process information and generate responses.
        
        Args:
            perception_data: Data from perception phase
            
        Returns:
            Thinking results
        """
        self.current_phase = LoopPhase.THINK
        start_time = datetime.now()
        
        try:
            # Extract key information for thinking
            raw_input = perception_data.get("raw_input", {})
            context = perception_data.get("context", {})
            
            # Coordinate thinking across subsystems
            coordination = await self.orchestrator.coordinate_systems("thinking", {
                "input": raw_input,
                "context": context
            })
            
            # Generate thinking output
            thinking_data = {
                "processed_input": raw_input,
                "enhanced_context": context,
                "reasoning_steps": [
                    "Analyzed input data",
                    "Gathered relevant context", 
                    "Coordinated subsystems",
                    "Generated response plan"
                ],
                "confidence": 0.8,
                "coordination_score": coordination.coordination_score,
                "timestamp": start_time.isoformat()
            }
            
            # Track phase timing
            duration = (datetime.now() - start_time).total_seconds()
            self.loop_metrics["phase_times"]["think"] = duration
            
            return thinking_data
            
        except Exception as e:
            self.logger.error(f"Thinking phase failed: {e}")
            return {"error": str(e), "phase": "think"}
    
    async def _act_phase(self, thinking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT phase: Execute actions or generate outputs.
        
        Args:
            thinking_data: Data from thinking phase
            
        Returns:
            Action results
        """
        self.current_phase = LoopPhase.ACT
        start_time = datetime.now()
        
        try:
            # Determine actions based on thinking data
            processed_input = thinking_data.get("processed_input", {})
            reasoning = thinking_data.get("reasoning_steps", [])
            
            # Execute actions (in this case, generate response)
            action_data = {
                "action_type": "response_generation",
                "input_processed": processed_input,
                "reasoning_applied": reasoning,
                "output_generated": True,
                "response": processed_input.get("query", "No query provided"),
                "confidence": thinking_data.get("confidence", 0.5),
                "timestamp": start_time.isoformat()
            }
            
            # Track phase timing
            duration = (datetime.now() - start_time).total_seconds()
            self.loop_metrics["phase_times"]["act"] = duration
            
            return action_data
            
        except Exception as e:
            self.logger.error(f"Action phase failed: {e}")
            return {"error": str(e), "phase": "act"}
    
    async def _reflect_phase(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        REFLECT phase: Analyze outcomes and performance.
        
        Args:
            action_data: Data from action phase
            
        Returns:
            Reflection results
        """
        self.current_phase = LoopPhase.REFLECT
        start_time = datetime.now()
        
        try:
            # Use reflection engine to analyze the iteration
            from ..intelligence.reflection_engine import ActionData
            
            reflection_input = ActionData(
                id=f"loop_action_{int(start_time.timestamp())}",
                type="intelligence_loop",
                description="Intelligence loop iteration",
                context=action_data,
                timestamp=start_time,
                duration=action_data.get("duration", 0),
                success=action_data.get("output_generated", False),
                error=action_data.get("error"),
                metadata={"phase": "reflection"}
            )
            
            # Generate reflection
            reflection = await self.reflection_engine.reflect_on_action(reflection_input)
            
            reflection_data = {
                "reflection_id": reflection.id,
                "analysis": reflection.analysis,
                "insights": reflection.insights,
                "confidence_score": reflection.confidence_score,
                "learning_value": reflection.learning_value,
                "timestamp": start_time.isoformat()
            }
            
            # Track phase timing
            duration = (datetime.now() - start_time).total_seconds()
            self.loop_metrics["phase_times"]["reflect"] = duration
            
            return reflection_data
            
        except Exception as e:
            self.logger.error(f"Reflection phase failed: {e}")
            return {"error": str(e), "phase": "reflect"}
    
    async def _learn_phase(self, reflection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        LEARN phase: Update mental models and improve.
        
        Args:
            reflection_data: Data from reflection phase
            
        Returns:
            Learning results
        """
        self.current_phase = LoopPhase.LEARN
        start_time = datetime.now()
        
        try:
            # Extract learning from reflection
            insights = reflection_data.get("insights", [])
            learning_value = reflection_data.get("learning_value", 0)
            
            # Generate learning data
            learning_data = {
                "lessons_learned": insights,
                "learning_value": learning_value,
                "model_updates": 1 if learning_value > 0.5 else 0,
                "improvement_areas": [
                    "Response quality",
                    "Context understanding",
                    "System coordination"
                ],
                "timestamp": start_time.isoformat()
            }
            
            # Track phase timing
            duration = (datetime.now() - start_time).total_seconds()
            self.loop_metrics["phase_times"]["learn"] = duration
            
            return learning_data
            
        except Exception as e:
            self.logger.error(f"Learning phase failed: {e}")
            return {"error": str(e), "phase": "learn"}
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize loop performance based on historical data."""
        try:
            # Analyze recent iterations
            recent_iterations = self.iterations[-10:] if len(self.iterations) >= 10 else self.iterations
            
            if not recent_iterations:
                return {"message": "No iterations to analyze"}
            
            # Calculate performance metrics
            successful_iterations = [i for i in recent_iterations if i.success]
            success_rate = len(successful_iterations) / len(recent_iterations)
            avg_duration = sum(i.duration for i in recent_iterations) / len(recent_iterations)
            
            # Identify bottlenecks
            bottlenecks = []
            phase_times = self.loop_metrics.get("phase_times", {})
            
            if phase_times:
                slowest_phase = max(phase_times.items(), key=lambda x: x[1])
                if slowest_phase[1] > 1.0:  # More than 1 second
                    bottlenecks.append(f"Slow {slowest_phase[0]} phase: {slowest_phase[1]:.2f}s")
            
            optimization_results = {
                "success_rate": success_rate,
                "average_duration": avg_duration,
                "bottlenecks": bottlenecks,
                "recommendations": self._generate_optimization_recommendations(
                    success_rate, avg_duration, bottlenecks
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            return {"error": str(e)}
    
    def _generate_optimization_recommendations(self, success_rate: float, 
                                            avg_duration: float,
                                            bottlenecks: List[str]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append("Improve error handling and recovery mechanisms")
        
        if avg_duration > 5.0:
            recommendations.append("Optimize phase processing for better performance")
        
        if bottlenecks:
            recommendations.append("Address identified bottlenecks in slow phases")
        
        if not recommendations:
            recommendations.append("System is performing well, continue monitoring")
        
        return recommendations
    
    def get_loop_metrics(self) -> LoopMetrics:
        """Get comprehensive loop performance metrics."""
        total = self.loop_metrics["total_cycles"]
        successful = self.loop_metrics["successful_cycles"]
        
        # Calculate phase durations
        phase_durations = self.loop_metrics.get("phase_times", {})
        
        # Calculate averages
        if self.iterations:
            avg_duration = sum(i.duration for i in self.iterations) / len(self.iterations)
            success_rate = successful / total if total > 0 else 0.0
        else:
            avg_duration = 0.0
            success_rate = 0.0
        
        return LoopMetrics(
            total_iterations=total,
            successful_iterations=successful,
            average_duration=avg_duration,
            phase_durations=phase_durations,
            success_rate=success_rate,
            learning_rate=0.0,  # TODO: Calculate actual learning rate
            timestamp=datetime.now()
        )
