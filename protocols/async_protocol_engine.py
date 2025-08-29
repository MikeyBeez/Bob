"""
Bob Protocols System - Async Protocol Engine for Intelligent Task Management

This integrates the protocol system into Bob for intelligent workflow management
with async support for background processing and autonomous task execution.

FEATURES:
=========
• Async protocol execution with background task support
• Intelligent protocol selection based on context
• Protocol orchestration through Bob Agent integration
• Autonomous protocol chaining for complex workflows
• Real-time protocol status monitoring
• Protocol learning and optimization

PROTOCOL TYPES:
===============
• Intelligence Protocols: Thinking, reasoning, learning patterns
• Knowledge Protocols: Information gathering, storage, retrieval
• System Protocols: Health monitoring, optimization, maintenance
• User Protocols: Interaction patterns, preference management
• Workflow Protocols: Multi-step task automation

Bob-specific enhancements:
• Integration with BobAgentIntegrated
• Async execution through intelligence loop
• Context-aware protocol selection
• Learning from protocol outcomes
• Autonomous background execution
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Bob-specific imports
try:
    from core.bob_agent_integrated import BobAgentIntegrated
except ImportError:
    BobAgentIntegrated = None


class ProtocolStatus(Enum):
    """Protocol execution status."""
    PENDING = "pending"
    RUNNING = "running" 
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProtocolPriority(Enum):
    """Protocol execution priority."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ProtocolStep:
    """Individual protocol step definition."""
    id: str
    name: str
    description: str
    action: Optional[str] = None
    async_handler: Optional[str] = None  # Name of async method to call
    validation: Optional[Dict[str, Any]] = None
    retry_count: int = 3
    timeout: int = 300  # seconds
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass 
class ProtocolDefinition:
    """Complete protocol definition."""
    id: str
    name: str
    description: str
    version: str
    category: str
    triggers: List[str]
    steps: List[ProtocolStep]
    priority: ProtocolPriority = ProtocolPriority.NORMAL
    async_enabled: bool = True
    background_capable: bool = False
    learning_enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProtocolExecution:
    """Runtime protocol execution state."""
    execution_id: str
    protocol_id: str
    status: ProtocolStatus
    current_step: int
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    step_results: Optional[List[Dict[str, Any]]] = None
    background_task: Optional[asyncio.Task] = None


class BobProtocolEngine:
    """
    Async Protocol Engine integrated with Bob Agent system.
    
    Manages protocol definitions, execution, and learning with full
    async support and Bob Agent integration.
    """
    
    def __init__(self, bob_agent: Optional[BobAgentIntegrated] = None):
        """
        Initialize Bob Protocol Engine.
        
        Args:
            bob_agent: Optional Bob Agent instance for integration
        """
        self.bob_agent = bob_agent
        self.logger = logging.getLogger("BobProtocolEngine")
        
        # Protocol storage
        self.protocols: Dict[str, ProtocolDefinition] = {}
        self.executions: Dict[str, ProtocolExecution] = {}
        
        # Async execution management
        self.background_tasks: Dict[str, asyncio.Task] = {}
        self.execution_lock = asyncio.Lock()
        
        # Protocol handlers - functions that implement protocol actions
        self.handlers: Dict[str, Callable] = {}
        
        # Load built-in protocols
        asyncio.create_task(self._load_builtin_protocols())
    
    async def _load_builtin_protocols(self):
        """Load Bob's built-in protocols."""
        builtin_protocols = [
            self._create_intelligence_protocol(),
            self._create_knowledge_protocol(), 
            self._create_system_health_protocol(),
            self._create_learning_protocol(),
            self._create_reflection_protocol()
        ]
        
        for protocol in builtin_protocols:
            await self.register_protocol(protocol)
    
    def _create_intelligence_protocol(self) -> ProtocolDefinition:
        """Create the core intelligence protocol."""
        return ProtocolDefinition(
            id="bob-intelligence-cycle",
            name="Bob Intelligence Cycle", 
            description="Core intelligence loop: perceive → think → act → reflect → learn",
            version="1.0.0",
            category="intelligence",
            triggers=["think", "reason", "analyze", "intelligence"],
            background_capable=True,
            steps=[
                ProtocolStep(
                    id="perceive",
                    name="Perceive Context",
                    description="Gather and analyze current context",
                    async_handler="perceive_context",
                    timeout=30
                ),
                ProtocolStep(
                    id="think",
                    name="Think and Reason", 
                    description="Process information and generate insights",
                    async_handler="think_and_reason",
                    timeout=120,
                    dependencies=["perceive"]
                ),
                ProtocolStep(
                    id="act",
                    name="Take Action",
                    description="Execute decisions and responses",
                    async_handler="take_action",
                    timeout=60,
                    dependencies=["think"]
                ),
                ProtocolStep(
                    id="reflect", 
                    name="Reflect on Outcome",
                    description="Analyze results and outcomes",
                    async_handler="reflect_on_outcome",
                    timeout=30,
                    dependencies=["act"]
                ),
                ProtocolStep(
                    id="learn",
                    name="Learn and Adapt",
                    description="Update knowledge and mental models",
                    async_handler="learn_and_adapt", 
                    timeout=45,
                    dependencies=["reflect"]
                )
            ]
        )
    
    def _create_knowledge_protocol(self) -> ProtocolDefinition:
        """Create knowledge management protocol."""
        return ProtocolDefinition(
            id="bob-knowledge-management",
            name="Knowledge Management Protocol",
            description="Systematic knowledge acquisition, storage, and retrieval",
            version="1.0.0", 
            category="knowledge",
            triggers=["learn", "store", "retrieve", "knowledge"],
            background_capable=True,
            steps=[
                ProtocolStep(
                    id="identify_knowledge_need",
                    name="Identify Knowledge Need",
                    description="Determine what knowledge is needed",
                    async_handler="identify_knowledge_need",
                    timeout=20
                ),
                ProtocolStep(
                    id="gather_knowledge",
                    name="Gather Information",
                    description="Collect relevant information from sources",
                    async_handler="gather_knowledge",
                    timeout=180,
                    dependencies=["identify_knowledge_need"]
                ),
                ProtocolStep(
                    id="process_knowledge", 
                    name="Process and Structure",
                    description="Structure and validate gathered knowledge",
                    async_handler="process_knowledge",
                    timeout=90,
                    dependencies=["gather_knowledge"]
                ),
                ProtocolStep(
                    id="store_knowledge",
                    name="Store Knowledge",
                    description="Store processed knowledge with indexing",
                    async_handler="store_knowledge",
                    timeout=30,
                    dependencies=["process_knowledge"]
                ),
                ProtocolStep(
                    id="validate_storage",
                    name="Validate Storage", 
                    description="Confirm knowledge was stored correctly",
                    async_handler="validate_storage",
                    timeout=15,
                    dependencies=["store_knowledge"]
                )
            ]
        )
    
    def _create_system_health_protocol(self) -> ProtocolDefinition:
        """Create system health monitoring protocol."""
        return ProtocolDefinition(
            id="bob-system-health",
            name="System Health Protocol",
            description="Continuous system health monitoring and optimization",
            version="1.0.0",
            category="system",
            triggers=["health", "monitor", "optimize", "maintenance"],
            background_capable=True,
            priority=ProtocolPriority.HIGH,
            steps=[
                ProtocolStep(
                    id="check_subsystems",
                    name="Check All Subsystems",
                    description="Verify health of all Bob subsystems",
                    async_handler="check_subsystems",
                    timeout=60
                ),
                ProtocolStep(
                    id="analyze_performance",
                    name="Analyze Performance", 
                    description="Evaluate system performance metrics",
                    async_handler="analyze_performance",
                    timeout=45,
                    dependencies=["check_subsystems"]
                ),
                ProtocolStep(
                    id="identify_issues",
                    name="Identify Issues",
                    description="Detect and prioritize any issues",
                    async_handler="identify_issues", 
                    timeout=30,
                    dependencies=["analyze_performance"]
                ),
                ProtocolStep(
                    id="optimize_systems",
                    name="Optimize Systems",
                    description="Apply optimizations and fixes",
                    async_handler="optimize_systems",
                    timeout=120,
                    dependencies=["identify_issues"]
                ),
                ProtocolStep(
                    id="verify_improvements",
                    name="Verify Improvements",
                    description="Confirm optimizations worked",
                    async_handler="verify_improvements",
                    timeout=30,
                    dependencies=["optimize_systems"]
                )
            ]
        )
    
    def _create_learning_protocol(self) -> ProtocolDefinition:
        """Create adaptive learning protocol.""" 
        return ProtocolDefinition(
            id="bob-adaptive-learning",
            name="Adaptive Learning Protocol",
            description="Continuous learning from interactions and outcomes",
            version="1.0.0",
            category="learning", 
            triggers=["learn", "adapt", "improve", "feedback"],
            background_capable=True,
            steps=[
                ProtocolStep(
                    id="collect_experience",
                    name="Collect Experience Data",
                    description="Gather interaction and outcome data", 
                    async_handler="collect_experience",
                    timeout=30
                ),
                ProtocolStep(
                    id="analyze_patterns",
                    name="Analyze Patterns",
                    description="Identify patterns in experiences",
                    async_handler="analyze_patterns",
                    timeout=90,
                    dependencies=["collect_experience"]
                ),
                ProtocolStep(
                    id="extract_insights",
                    name="Extract Insights", 
                    description="Generate actionable insights from patterns",
                    async_handler="extract_insights",
                    timeout=60,
                    dependencies=["analyze_patterns"]
                ),
                ProtocolStep(
                    id="update_models",
                    name="Update Mental Models",
                    description="Update internal models with new insights",
                    async_handler="update_models",
                    timeout=45,
                    dependencies=["extract_insights"]
                ),
                ProtocolStep(
                    id="test_improvements",
                    name="Test Improvements",
                    description="Validate that updates improve performance",
                    async_handler="test_improvements", 
                    timeout=60,
                    dependencies=["update_models"]
                )
            ]
        )
    
    def _create_reflection_protocol(self) -> ProtocolDefinition:
        """Create self-reflection protocol."""
        return ProtocolDefinition(
            id="bob-self-reflection",
            name="Self-Reflection Protocol",
            description="Deep self-analysis and introspection for improvement",
            version="1.0.0",
            category="reflection",
            triggers=["reflect", "introspect", "analyze_self", "improvement"],
            background_capable=True,
            steps=[
                ProtocolStep(
                    id="review_recent_actions",
                    name="Review Recent Actions",
                    description="Analyze recent decisions and actions",
                    async_handler="review_recent_actions",
                    timeout=60
                ),
                ProtocolStep(
                    id="evaluate_outcomes",
                    name="Evaluate Outcomes",
                    description="Assess the success of recent actions",
                    async_handler="evaluate_outcomes",
                    timeout=45,
                    dependencies=["review_recent_actions"]
                ),
                ProtocolStep(
                    id="identify_improvement_areas",
                    name="Identify Improvement Areas",
                    description="Find areas for potential improvement", 
                    async_handler="identify_improvement_areas",
                    timeout=60,
                    dependencies=["evaluate_outcomes"]
                ),
                ProtocolStep(
                    id="develop_strategies",
                    name="Develop Improvement Strategies",
                    description="Create strategies for identified improvements",
                    async_handler="develop_strategies",
                    timeout=90,
                    dependencies=["identify_improvement_areas"]
                ),
                ProtocolStep(
                    id="implement_changes",
                    name="Implement Changes",
                    description="Apply improvement strategies",
                    async_handler="implement_changes",
                    timeout=120,
                    dependencies=["develop_strategies"]
                )
            ]
        )
    
    # ================================================
    # PROTOCOL MANAGEMENT
    # ================================================
    
    async def register_protocol(self, protocol: ProtocolDefinition):
        """Register a new protocol."""
        async with self.execution_lock:
            self.protocols[protocol.id] = protocol
            self.logger.info(f"✅ Registered protocol: {protocol.id}")
    
    async def get_protocol(self, protocol_id: str) -> Optional[ProtocolDefinition]:
        """Get protocol by ID."""
        return self.protocols.get(protocol_id)
    
    async def list_protocols(self, category: Optional[str] = None) -> List[ProtocolDefinition]:
        """List available protocols, optionally filtered by category."""
        protocols = list(self.protocols.values())
        if category:
            protocols = [p for p in protocols if p.category == category]
        return protocols
    
    async def detect_protocols(self, trigger_text: str, context: Optional[Dict] = None) -> List[str]:
        """Detect which protocols should be triggered by given text."""
        triggered_protocols = []
        
        trigger_lower = trigger_text.lower()
        
        for protocol_id, protocol in self.protocols.items():
            for trigger in protocol.triggers:
                if trigger.lower() in trigger_lower:
                    triggered_protocols.append(protocol_id)
                    break
        
        return triggered_protocols
    
    # ================================================ 
    # PROTOCOL EXECUTION
    # ================================================
    
    async def start_protocol(
        self, 
        protocol_id: str, 
        context: Optional[Dict] = None,
        background: bool = False
    ) -> str:
        """Start protocol execution."""
        protocol = await self.get_protocol(protocol_id)
        if not protocol:
            raise ValueError(f"Protocol not found: {protocol_id}")
        
        execution_id = f"{protocol_id}_{int(datetime.now().timestamp())}"
        
        execution = ProtocolExecution(
            execution_id=execution_id,
            protocol_id=protocol_id,
            status=ProtocolStatus.PENDING,
            current_step=0,
            started_at=datetime.now(),
            updated_at=datetime.now(),
            context=context or {},
            step_results=[]
        )
        
        async with self.execution_lock:
            self.executions[execution_id] = execution
        
        if background and protocol.background_capable:
            # Start background execution
            task = asyncio.create_task(self._execute_protocol_background(execution_id))
            execution.background_task = task
            self.background_tasks[execution_id] = task
            self.logger.info(f"🔄 Started background protocol: {execution_id}")
        else:
            # Start foreground execution
            await self._execute_protocol(execution_id)
            self.logger.info(f"✅ Completed foreground protocol: {execution_id}")
        
        return execution_id
    
    async def _execute_protocol_background(self, execution_id: str):
        """Execute protocol in background."""
        try:
            await self._execute_protocol(execution_id)
            self.logger.info(f"✅ Background protocol completed: {execution_id}")
        except Exception as e:
            self.logger.error(f"❌ Background protocol failed: {execution_id} - {e}")
            await self._update_execution_status(execution_id, ProtocolStatus.FAILED, str(e))
        finally:
            # Clean up background task
            if execution_id in self.background_tasks:
                del self.background_tasks[execution_id]
    
    async def _execute_protocol(self, execution_id: str):
        """Execute protocol steps."""
        execution = self.executions[execution_id]
        protocol = self.protocols[execution.protocol_id]
        
        await self._update_execution_status(execution_id, ProtocolStatus.RUNNING)
        
        try:
            for i, step in enumerate(protocol.steps):
                execution.current_step = i
                
                # Check dependencies
                if step.dependencies:
                    if not self._check_dependencies_met(step.dependencies, execution.step_results):
                        raise ValueError(f"Dependencies not met for step: {step.id}")
                
                self.logger.info(f"🔄 Executing step: {step.id} ({execution_id})")
                
                # Execute step
                step_result = await self._execute_step(step, execution.context)
                
                # Store step result
                execution.step_results.append({
                    "step_id": step.id,
                    "result": step_result,
                    "completed_at": datetime.now().isoformat()
                })
                
                execution.updated_at = datetime.now()
            
            # Mark as completed
            await self._update_execution_status(execution_id, ProtocolStatus.COMPLETED)
            execution.completed_at = datetime.now()
            
        except Exception as e:
            await self._update_execution_status(execution_id, ProtocolStatus.FAILED, str(e))
            raise
    
    async def _execute_step(self, step: ProtocolStep, context: Dict) -> Any:
        """Execute individual protocol step."""
        if step.async_handler:
            # Use async handler
            if hasattr(self, step.async_handler):
                handler = getattr(self, step.async_handler)
                return await handler(step, context)
            else:
                self.logger.warning(f"⚠️ Handler not found: {step.async_handler}")
                return {"status": "handler_not_found", "step": step.id}
        
        elif step.action:
            # Execute action (could be Bob Agent method)
            if self.bob_agent and hasattr(self.bob_agent, step.action):
                method = getattr(self.bob_agent, step.action)
                if asyncio.iscoroutinefunction(method):
                    return await method(context)
                else:
                    return method(context)
            else:
                self.logger.warning(f"⚠️ Action not found: {step.action}")
                return {"status": "action_not_found", "step": step.id}
        
        else:
            # Default step execution
            return {"status": "completed", "step": step.id}
    
    def _check_dependencies_met(self, dependencies: List[str], step_results: List[Dict]) -> bool:
        """Check if step dependencies are met."""
        completed_steps = {result["step_id"] for result in step_results}
        return all(dep in completed_steps for dep in dependencies)
    
    async def _update_execution_status(self, execution_id: str, status: ProtocolStatus, error: Optional[str] = None):
        """Update execution status."""
        execution = self.executions[execution_id]
        execution.status = status
        execution.updated_at = datetime.now()
        if error:
            execution.error = error
    
    # ================================================
    # PROTOCOL HANDLERS (async implementations)
    # ================================================
    
    async def perceive_context(self, step: ProtocolStep, context: Dict) -> Dict:
        """Perceive and analyze current context."""
        if self.bob_agent:
            # Use Bob Agent's context assembly capabilities
            context_data = await self.bob_agent.context_assembler.assemble_context(
                context.get("input", ""), context
            )
            return {"status": "completed", "context_data": context_data}
        return {"status": "completed", "context_data": context}
    
    async def think_and_reason(self, step: ProtocolStep, context: Dict) -> Dict:
        """Think and reason about the context."""
        if self.bob_agent:
            # Use Bob Agent's thinking capabilities
            thought_response = await self.bob_agent.think(
                context.get("input", "Current situation analysis"), context
            )
            return {
                "status": "completed",
                "thought": thought_response.thought,
                "confidence": thought_response.confidence,
                "reasoning": thought_response.reasoning
            }
        return {"status": "completed", "thought": "Basic reasoning completed"}
    
    async def take_action(self, step: ProtocolStep, context: Dict) -> Dict:
        """Take action based on thinking."""
        # This would implement actual action taking
        # For now, return action plan
        return {
            "status": "completed", 
            "action": "action_determined",
            "plan": context.get("action_plan", "No specific action needed")
        }
    
    async def reflect_on_outcome(self, step: ProtocolStep, context: Dict) -> Dict:
        """Reflect on the outcome of actions."""
        if self.bob_agent:
            # Use Bob Agent's reflection capabilities
            reflection_report = await self.bob_agent.reflect_and_adapt()
            return {"status": "completed", "reflection": reflection_report}
        return {"status": "completed", "reflection": "Basic reflection completed"}
    
    async def learn_and_adapt(self, step: ProtocolStep, context: Dict) -> Dict:
        """Learn from the experience and adapt."""
        if self.bob_agent:
            # Use Bob Agent's learning capabilities
            experience = {
                "context": context,
                "outcome": context.get("outcome", "neutral"),
                "timestamp": datetime.now().isoformat()
            }
            learning_update = await self.bob_agent.learn_from_experience(experience)
            return {
                "status": "completed",
                "lessons_learned": learning_update.lessons_learned,
                "model_updates": learning_update.mental_model_updates
            }
        return {"status": "completed", "learning": "Basic learning completed"}
    
    # Additional handlers for other protocols...
    async def check_subsystems(self, step: ProtocolStep, context: Dict) -> Dict:
        """Check health of all subsystems."""
        if self.bob_agent:
            health_status = await self.bob_agent.health_check()
            return {
                "status": "completed",
                "health_score": health_status.overall_health,
                "subsystems": {
                    "database": health_status.database_ready,
                    "filesystem": health_status.filesystem_ready,
                    "ollama": health_status.ollama_ready,
                    "reflection": health_status.reflection_ready
                }
            }
        return {"status": "completed", "health": "basic_check"}
    
    # ================================================
    # PROTOCOL MONITORING AND MANAGEMENT  
    # ================================================
    
    async def get_execution_status(self, execution_id: str) -> Optional[ProtocolExecution]:
        """Get execution status."""
        return self.executions.get(execution_id)
    
    async def list_active_executions(self) -> List[ProtocolExecution]:
        """List all active protocol executions."""
        return [
            exec for exec in self.executions.values() 
            if exec.status in [ProtocolStatus.PENDING, ProtocolStatus.RUNNING, ProtocolStatus.PAUSED]
        ]
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel protocol execution."""
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            await self._update_execution_status(execution_id, ProtocolStatus.CANCELLED)
            
            # Cancel background task if exists
            if execution.background_task:
                execution.background_task.cancel()
                if execution_id in self.background_tasks:
                    del self.background_tasks[execution_id]
            
            return True
        return False
    
    async def cleanup_completed_executions(self, max_age_hours: int = 24):
        """Clean up old completed executions."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for execution_id, execution in self.executions.items():
            if (execution.status in [ProtocolStatus.COMPLETED, ProtocolStatus.FAILED, ProtocolStatus.CANCELLED] 
                and execution.updated_at < cutoff_time):
                to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.executions[execution_id]
        
        self.logger.info(f"🧹 Cleaned up {len(to_remove)} old executions")
    
    # ================================================
    # INTEGRATION WITH BOB AGENT
    # ================================================
    
    async def integrate_with_bob_agent(self, bob_agent: BobAgentIntegrated):
        """Integrate protocol engine with Bob Agent."""
        self.bob_agent = bob_agent
        self.logger.info("🔗 Protocol engine integrated with Bob Agent")
        
        # Start background health monitoring
        await self.start_protocol("bob-system-health", background=True)
    
    async def suggest_protocols(self, context: Dict) -> List[str]:
        """Suggest protocols based on current context."""
        suggestions = []
        
        # Analyze context to suggest relevant protocols
        if "health" in str(context).lower() or "status" in str(context).lower():
            suggestions.append("bob-system-health")
        
        if "learn" in str(context).lower() or "knowledge" in str(context).lower():
            suggestions.extend(["bob-knowledge-management", "bob-adaptive-learning"])
        
        if "think" in str(context).lower() or "analyze" in str(context).lower():
            suggestions.append("bob-intelligence-cycle")
        
        if "reflect" in str(context).lower() or "improve" in str(context).lower():
            suggestions.append("bob-self-reflection")
        
        return suggestions
    
    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get protocol execution statistics."""
        total_executions = len(self.executions)
        active_executions = len([e for e in self.executions.values() 
                               if e.status in [ProtocolStatus.PENDING, ProtocolStatus.RUNNING]])
        completed_executions = len([e for e in self.executions.values() 
                                  if e.status == ProtocolStatus.COMPLETED])
        failed_executions = len([e for e in self.executions.values() 
                               if e.status == ProtocolStatus.FAILED])
        
        return {
            "total_protocols": len(self.protocols),
            "total_executions": total_executions,
            "active_executions": active_executions,
            "completed_executions": completed_executions, 
            "failed_executions": failed_executions,
            "success_rate": completed_executions / total_executions if total_executions > 0 else 0,
            "background_tasks": len(self.background_tasks)
        }


# ================================================
# FACTORY FUNCTION FOR BOB INTEGRATION
# ================================================

def create_bob_protocol_engine(bob_agent: Optional[BobAgentIntegrated] = None) -> BobProtocolEngine:
    """
    Create a Bob Protocol Engine instance.
    
    Args:
        bob_agent: Optional Bob Agent instance for integration
        
    Returns:
        Configured BobProtocolEngine instance
    """
    return BobProtocolEngine(bob_agent=bob_agent)
