"""
bob_agent_integrated.py - Clean API for integrated Bob agent system

This is the main orchestration module that brings together all Bob components:
- DatabaseCore: Persistent storage and state management
- FileSystemCore: Safe file operations and knowledge storage
- OllamaClient: LLM communication and reasoning
- ReflectionEngine: Intelligent learning and adaptation

Following the proven modular architecture pattern established in Phases 1 & 2.
Implementation details are delegated to specialized submodules for clean API surface.

API DOCUMENTATION:
==================

Core Intelligence Methods:
--------------------------
• think(prompt, context) -> ThoughtResponse
    Primary thinking function that orchestrates all subsystems
    
• process_query(query, context) -> QueryResponse  
    Process user queries with full system integration
    
• learn_from_experience(experience) -> LearningUpdate
    Learn from interactions and update mental models
    
• reflect_and_adapt() -> ReflectionReport
    Perform system-wide reflection and adaptation

Knowledge Management:
--------------------
• store_knowledge(knowledge) -> bool
    Store knowledge with semantic indexing and relationships
    
• retrieve_knowledge(query, context) -> KnowledgeResults
    Retrieve relevant knowledge for current context
    
• build_knowledge_graph() -> KnowledgeGraph
    Construct semantic knowledge graph from stored information

System Orchestration:
--------------------
• initialize_systems() -> SystemStatus
    Initialize all subsystems with dependency management
    
• health_check() -> HealthStatus
    Check health of all subsystems and report status
    
• get_system_metrics() -> SystemMetrics
    Collect comprehensive metrics from all subsystems
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# Import all our Phase 1 and Phase 2 modules
from .database_core import DatabaseCore, create_database_core
from .filesystem_core import FileSystemCore, create_filesystem_core  
from .ollama_client import OllamaClient
from ..intelligence.reflection_engine import ReflectionEngine, ActionData, OutcomeData

# Import agent submodules (to be implemented)
from .agent.orchestrator import SystemOrchestrator
from .agent.knowledge_manager import KnowledgeManager
from .agent.intelligence_loop import IntelligenceLoop
from .agent.context_assembler import ContextAssembler
from .agent.response_generator import ResponseGenerator

# Import protocols system
try:
    from ..protocols.async_protocol_engine import BobProtocolEngine, create_bob_protocol_engine
except ImportError:
    # Handle relative import issues
    import sys
    from pathlib import Path
    bob_dir = Path(__file__).parent.parent.absolute()
    if str(bob_dir) not in sys.path:
        sys.path.insert(0, str(bob_dir))
    from protocols.async_protocol_engine import BobProtocolEngine, create_bob_protocol_engine


@dataclass
class ThoughtResponse:
    """Response from the thinking process."""
    id: str
    thought: str
    confidence: float
    reasoning: List[str]
    knowledge_used: List[str]
    reflections_triggered: int
    timestamp: datetime
    processing_time: float


@dataclass 
class QueryResponse:
    """Response to user queries."""
    id: str
    query: str
    response: str
    confidence: float
    sources: List[str]
    insights: List[str]
    follow_up_suggestions: List[str]
    timestamp: datetime
    processing_time: float


@dataclass
class LearningUpdate:
    """Result of learning from experience."""
    experience_id: str
    lessons_learned: List[str]
    mental_model_updates: int
    confidence_adjustments: Dict[str, float]
    new_patterns_discovered: int
    timestamp: datetime


@dataclass
class SystemStatus:
    """System initialization and health status."""
    database_ready: bool
    filesystem_ready: bool
    ollama_ready: bool
    reflection_ready: bool
    overall_health: float
    initialization_time: float
    last_check: datetime
    errors: List[str]


@dataclass
class SystemMetrics:
    """Comprehensive system metrics."""
    uptime: float
    total_thoughts: int
    total_queries: int
    total_reflections: int
    knowledge_entries: int
    learning_updates: int
    average_response_time: float
    system_efficiency: float
    subsystem_metrics: Dict[str, Any]
    timestamp: datetime


class BobAgentIntegrated:
    """
    Main Bob Agent that orchestrates all intelligence subsystems.
    
    This is the clean API surface for the complete Bob system.
    All complexity is hidden in submodules, exposing only essential methods.
    """
    
    def __init__(self, 
                 data_path: str = "~/Bob/data",
                 ollama_url: str = "http://localhost:11434",
                 model: str = "llama3.2",
                 debug: bool = False):
        """
        Initialize Bob Agent with configuration.
        
        Args:
            data_path: Path for data storage
            ollama_url: Ollama service URL
            model: Default LLM model to use
            debug: Enable debug logging
        """
        # Configuration
        self.data_path = Path(data_path).expanduser()
        self.ollama_url = ollama_url
        self.model = model
        self.debug = debug
        
        # Core subsystems (Phase 1 & 2 modules)
        self.db_core: Optional[DatabaseCore] = None
        self.fs_core: Optional[FileSystemCore] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.reflection_engine: Optional[ReflectionEngine] = None
        
        # Agent subsystems (Phase 3 modules)
        self.orchestrator: Optional[SystemOrchestrator] = None
        self.knowledge_manager: Optional[KnowledgeManager] = None
        self.intelligence_loop: Optional[IntelligenceLoop] = None
        self.context_assembler: Optional[ContextAssembler] = None
        self.response_generator: Optional[ResponseGenerator] = None
        
        # Protocol engine (Phase 4 addition)
        self.protocol_engine: Optional[BobProtocolEngine] = None
        
        # System state
        self.initialized = False
        self.start_time = datetime.now()
        self.metrics = {
            "thoughts": 0,
            "queries": 0, 
            "reflections": 0,
            "learning_updates": 0
        }
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("BobAgent")
    
    # ================================================
    # SYSTEM INITIALIZATION AND MANAGEMENT
    # ================================================
    
    async def initialize_systems(self) -> SystemStatus:
        """
        Initialize all subsystems with proper dependency management.
        
        Returns:
            SystemStatus with initialization results
        """
        self.logger.info("🚀 Initializing Bob Agent systems...")
        start_time = datetime.now()
        errors = []
        
        try:
            # Phase 1: Initialize core subsystems
            await self._initialize_core_systems()
            
            # Phase 2: Initialize intelligence systems
            await self._initialize_intelligence_systems()
            
            # Phase 3: Initialize agent orchestration
            await self._initialize_agent_systems()
            
            self.initialized = True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            errors.append(str(e))
        
        # Create status report
        initialization_time = (datetime.now() - start_time).total_seconds()
        status = SystemStatus(
            database_ready=self.db_core is not None,
            filesystem_ready=self.fs_core is not None,
            ollama_ready=self.ollama_client is not None,
            reflection_ready=self.reflection_engine is not None,
            overall_health=self._calculate_health_score(),
            initialization_time=initialization_time,
            last_check=datetime.now(),
            errors=errors
        )
        
        self.logger.info(f"✅ Bob Agent initialized - Health: {status.overall_health:.2f}")
        return status
    
    async def _initialize_core_systems(self):
        """Initialize Phase 1 core subsystems."""
        self.logger.info("📦 Initializing core subsystems...")
        
        # Initialize database
        db_path = self.data_path / "bob.db"
        self.db_core = create_database_core(str(db_path))
        
        # Initialize filesystem
        self.fs_core = create_filesystem_core(
            db_core=self.db_core,
            base_path=str(self.data_path)
        )
        
        # Initialize Ollama client
        self.ollama_client = OllamaClient(
            base_url=self.ollama_url,
            timeout=60,
            max_retries=3
        )
        
        # Test Ollama connection
        if not await self.ollama_client.health_check():
            self.logger.warning("⚠️ Ollama service not available")
    
    async def _initialize_intelligence_systems(self):
        """Initialize Phase 2 intelligence subsystems."""
        self.logger.info("🧠 Initializing intelligence subsystems...")
        
        # Initialize reflection engine
        self.reflection_engine = ReflectionEngine(
            db_core=self.db_core,
            fs_core=self.fs_core,
            ollama_client=self.ollama_client
        )
        await self.reflection_engine.initialize()
    
    async def _initialize_agent_systems(self):
        """Initialize Phase 3 agent orchestration subsystems."""
        self.logger.info("🤖 Initializing agent orchestration...")
        
        # Initialize orchestrator
        self.orchestrator = SystemOrchestrator(
            db_core=self.db_core,
            fs_core=self.fs_core,
            ollama_client=self.ollama_client,
            reflection_engine=self.reflection_engine
        )
        
        # Initialize knowledge manager
        self.knowledge_manager = KnowledgeManager(
            db_core=self.db_core,
            fs_core=self.fs_core,
            ollama_client=self.ollama_client
        )
        
        # Initialize intelligence loop
        self.intelligence_loop = IntelligenceLoop(
            orchestrator=self.orchestrator,
            reflection_engine=self.reflection_engine
        )
        
        # Initialize context assembler
        self.context_assembler = ContextAssembler(
            knowledge_manager=self.knowledge_manager,
            db_core=self.db_core
        )
        
        # Initialize response generator
        self.response_generator = ResponseGenerator(
            ollama_client=self.ollama_client,
            context_assembler=self.context_assembler
        )
        
        # Initialize protocol engine (Phase 4)
        self.protocol_engine = create_bob_protocol_engine(bob_agent=self)
        await self.protocol_engine.integrate_with_bob_agent(self)
    
    async def health_check(self) -> SystemStatus:
        """
        Check health of all subsystems.
        
        Returns:
            Current system health status
        """
        errors = []
        
        # Check each subsystem
        db_ready = self.db_core is not None
        fs_ready = self.fs_core is not None
        ollama_ready = False
        reflection_ready = self.reflection_engine is not None
        
        if self.ollama_client:
            try:
                ollama_ready = await self.ollama_client.health_check()
            except Exception as e:
                errors.append(f"Ollama health check failed: {e}")
        
        return SystemStatus(
            database_ready=db_ready,
            filesystem_ready=fs_ready,
            ollama_ready=ollama_ready,
            reflection_ready=reflection_ready,
            overall_health=self._calculate_health_score(),
            initialization_time=0.0,
            last_check=datetime.now(),
            errors=errors
        )
    
    def _calculate_health_score(self) -> float:
        """Calculate overall system health score."""
        scores = []
        
        if self.db_core is not None:
            scores.append(1.0)
        if self.fs_core is not None:
            scores.append(1.0)
        if self.ollama_client is not None:
            scores.append(1.0)  # Could add actual health check here
        if self.reflection_engine is not None:
            scores.append(1.0)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    # ================================================
    # CORE INTELLIGENCE METHODS
    # ================================================
    
    async def think(self, prompt: str, context: Optional[Dict] = None) -> ThoughtResponse:
        """
        Primary thinking function that orchestrates all subsystems.
        
        Args:
            prompt: Input to think about
            context: Optional context information
            
        Returns:
            ThoughtResponse with complete thinking results
        """
        if not self.initialized:
            await self.initialize_systems()
        
        start_time = datetime.now()
        thought_id = f"thought_{int(start_time.timestamp())}"
        
        self.logger.info(f"🤔 Thinking about: {prompt[:100]}...")
        
        try:
            # Assemble context from knowledge and memories
            assembled_context = await self.context_assembler.assemble_context(
                prompt, context or {}
            )
            
            # Generate response using orchestrated systems
            response = await self.response_generator.generate_response(
                prompt, assembled_context
            )
            
            # Reflect on the thinking process
            action_data = ActionData(
                id=thought_id,
                type="thinking",
                description=prompt,
                context=assembled_context,
                timestamp=start_time,
                duration=(datetime.now() - start_time).total_seconds(),
                success=True,
                error=None,
                metadata={"model": self.model}
            )
            
            reflection = await self.reflection_engine.reflect_on_action(action_data)
            
            # Update metrics
            self.metrics["thoughts"] += 1
            
            # Create response
            processing_time = (datetime.now() - start_time).total_seconds()
            return ThoughtResponse(
                id=thought_id,
                thought=response["response"],
                confidence=response.get("confidence", 0.8),
                reasoning=response.get("reasoning", []),
                knowledge_used=response.get("knowledge_sources", []),
                reflections_triggered=1,
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Thinking failed: {e}")
            return ThoughtResponse(
                id=thought_id,
                thought=f"I encountered an error while thinking: {e}",
                confidence=0.0,
                reasoning=[],
                knowledge_used=[],
                reflections_triggered=0,
                timestamp=start_time,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def process_query(self, query: str, context: Optional[Dict] = None) -> QueryResponse:
        """
        Process user queries with full system integration.
        
        Args:
            query: User query to process
            context: Optional context information
            
        Returns:
            QueryResponse with comprehensive results
        """
        if not self.initialized:
            await self.initialize_systems()
        
        start_time = datetime.now()
        query_id = f"query_{int(start_time.timestamp())}"
        
        self.logger.info(f"❓ Processing query: {query[:100]}...")
        
        try:
            # Get knowledge and insights
            knowledge_results = await self.knowledge_manager.retrieve_knowledge(
                query, context or {}
            )
            
            # Think about the query
            thought_response = await self.think(
                f"Answer this query: {query}",
                {**(context or {}), **knowledge_results}
            )
            
            # Generate insights and suggestions
            insights = await self.reflection_engine.generate_insights({
                "domain": "query_processing",
                "query": query,
                "context": context
            })
            
            # Update metrics
            self.metrics["queries"] += 1
            
            # Create response
            processing_time = (datetime.now() - start_time).total_seconds()
            return QueryResponse(
                id=query_id,
                query=query,
                response=thought_response.thought,
                confidence=thought_response.confidence,
                sources=thought_response.knowledge_used,
                insights=[insight.description for insight in insights[:3]],
                follow_up_suggestions=self._generate_follow_ups(query, thought_response),
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            return QueryResponse(
                id=query_id,
                query=query,
                response=f"I encountered an error processing your query: {e}",
                confidence=0.0,
                sources=[],
                insights=[],
                follow_up_suggestions=[],
                timestamp=start_time,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def learn_from_experience(self, experience: Dict[str, Any]) -> LearningUpdate:
        """
        Learn from interactions and update mental models.
        
        Args:
            experience: Experience data to learn from
            
        Returns:
            LearningUpdate with learning results
        """
        experience_id = f"exp_{int(datetime.now().timestamp())}"
        
        try:
            # Use reflection engine for learning
            learning_result = await self.reflection_engine.learn_from_feedback(experience)
            
            # Update metrics
            self.metrics["learning_updates"] += 1
            
            return LearningUpdate(
                experience_id=experience_id,
                lessons_learned=learning_result.lessons_learned,
                mental_model_updates=learning_result.model_updates,
                confidence_adjustments=learning_result.confidence_changes,
                new_patterns_discovered=learning_result.new_patterns,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Learning from experience failed: {e}")
            return LearningUpdate(
                experience_id=experience_id,
                lessons_learned=[f"Error in learning: {e}"],
                mental_model_updates=0,
                confidence_adjustments={},
                new_patterns_discovered=0,
                timestamp=datetime.now()
            )
    
    async def reflect_and_adapt(self) -> Dict[str, Any]:
        """
        Perform system-wide reflection and adaptation.
        
        Returns:
            Reflection report with adaptation recommendations
        """
        try:
            # Generate comprehensive reflection report
            report = await self.reflection_engine.generate_reflection_report("24h")
            
            # Run intelligence loop optimization
            if self.intelligence_loop:
                optimization_results = await self.intelligence_loop.optimize_performance()
                report["optimization"] = optimization_results
            
            # Update metrics
            self.metrics["reflections"] += 1
            
            return report
            
        except Exception as e:
            self.logger.error(f"Reflection and adaptation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    # ================================================
    # KNOWLEDGE MANAGEMENT
    # ================================================
    
    async def store_knowledge(self, knowledge: Dict[str, Any]) -> bool:
        """
        Store knowledge with semantic indexing.
        
        Args:
            knowledge: Knowledge to store
            
        Returns:
            Success status
        """
        try:
            if not self.knowledge_manager:
                return False
                
            return await self.knowledge_manager.store_knowledge(knowledge)
            
        except Exception as e:
            self.logger.error(f"Knowledge storage failed: {e}")
            return False
    
    async def retrieve_knowledge(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge for current context.
        
        Args:
            query: Query to search for
            context: Optional context information
            
        Returns:
            Relevant knowledge results
        """
        try:
            if not self.knowledge_manager:
                return {}
                
            return await self.knowledge_manager.retrieve_knowledge(query, context or {})
            
        except Exception as e:
            self.logger.error(f"Knowledge retrieval failed: {e}")
            return {}
    
    # ================================================
    # SYSTEM METRICS AND STATUS
    # ================================================
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        Collect comprehensive metrics from all subsystems.
        
        Returns:
            SystemMetrics with complete system statistics
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Collect subsystem metrics
        subsystem_metrics = {}
        
        if self.fs_core:
            subsystem_metrics["filesystem"] = self.fs_core.get_metrics()
        
        if self.ollama_client:
            subsystem_metrics["ollama"] = self.ollama_client.get_metrics()
        
        if self.reflection_engine:
            subsystem_metrics["reflection"] = asyncio.create_task(
                self.reflection_engine.get_learning_metrics()
            )
        
        # Calculate efficiency
        total_operations = sum(self.metrics.values())
        efficiency = total_operations / uptime if uptime > 0 else 0
        
        return SystemMetrics(
            uptime=uptime,
            total_thoughts=self.metrics["thoughts"],
            total_queries=self.metrics["queries"],
            total_reflections=self.metrics["reflections"],
            knowledge_entries=0,  # TODO: Get from knowledge manager
            learning_updates=self.metrics["learning_updates"],
            average_response_time=0.0,  # TODO: Track response times
            system_efficiency=efficiency,
            subsystem_metrics=subsystem_metrics,
            timestamp=datetime.now()
        )
    
    # ================================================
    # PROTOCOL MANAGEMENT METHODS
    # ================================================
    
    async def start_protocol(self, protocol_id: str, context: Optional[Dict] = None, background: bool = False) -> str:
        """
        Start a protocol execution.
        
        Args:
            protocol_id: ID of the protocol to start
            context: Optional context for the protocol
            background: Whether to run in background
            
        Returns:
            Execution ID for tracking
        """
        if not self.protocol_engine:
            raise RuntimeError("Protocol engine not initialized")
        
        return await self.protocol_engine.start_protocol(protocol_id, context, background)
    
    async def get_protocol_status(self, execution_id: str) -> Optional[Dict]:
        """
        Get status of a protocol execution.
        
        Args:
            execution_id: Execution ID to check
            
        Returns:
            Protocol execution status
        """
        if not self.protocol_engine:
            return None
            
        execution = await self.protocol_engine.get_execution_status(execution_id)
        if execution:
            return {
                "execution_id": execution.execution_id,
                "protocol_id": execution.protocol_id,
                "status": execution.status.value,
                "current_step": execution.current_step,
                "started_at": execution.started_at.isoformat(),
                "updated_at": execution.updated_at.isoformat(),
                "error": execution.error
            }
        return None
    
    async def list_available_protocols(self, category: Optional[str] = None) -> List[Dict]:
        """
        List available protocols.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of available protocols
        """
        if not self.protocol_engine:
            return []
        
        protocols = await self.protocol_engine.list_protocols(category)
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "triggers": p.triggers,
                "background_capable": p.background_capable
            }
            for p in protocols
        ]
    
    async def suggest_protocols(self, context: Optional[Dict] = None) -> List[str]:
        """
        Get protocol suggestions based on context.
        
        Args:
            context: Context to analyze
            
        Returns:
            List of suggested protocol IDs
        """
        if not self.protocol_engine:
            return []
        
        return await self.protocol_engine.suggest_protocols(context or {})
    
    async def detect_protocols_from_text(self, text: str) -> List[str]:
        """
        Detect protocols that should be triggered by text.
        
        Args:
            text: Text to analyze for protocol triggers
            
        Returns:
            List of protocol IDs that should be triggered
        """
        if not self.protocol_engine:
            return []
        
        return await self.protocol_engine.detect_protocols(text)
    
    def get_protocol_stats(self) -> Dict[str, Any]:
        """
        Get protocol execution statistics.
        
        Returns:
            Protocol statistics
        """
        if not self.protocol_engine:
            return {}
        
        return self.protocol_engine.get_protocol_stats()

    # ================================================
    # HELPER METHODS
    # ================================================
    
    def _generate_follow_ups(self, query: str, response: ThoughtResponse) -> List[str]:
        """Generate follow-up suggestions based on query and response."""
        # Simple follow-up generation - could be enhanced with LLM
        return [
            "Would you like me to elaborate on any part of this response?",
            "Do you have any related questions?",
            "Would you like me to find more specific information about this topic?"
        ]
    
    async def cleanup(self):
        """Clean up system resources."""
        self.logger.info("🧹 Cleaning up Bob Agent systems...")
        
        if self.ollama_client:
            await self.ollama_client.close()
        
        # Additional cleanup for other subsystems as needed
        
        self.logger.info("✅ Bob Agent cleanup complete")


# ================================================
# FACTORY FUNCTION
# ================================================

def create_bob_agent(data_path: str = "~/Bob/data",
                    ollama_url: str = "http://localhost:11434", 
                    model: str = "llama3.2",
                    debug: bool = False) -> BobAgentIntegrated:
    """
    Factory function to create a Bob Agent instance.
    
    Args:
        data_path: Path for data storage
        ollama_url: Ollama service URL  
        model: Default LLM model
        debug: Enable debug logging
        
    Returns:
        Configured BobAgentIntegrated instance
    """
    return BobAgentIntegrated(
        data_path=data_path,
        ollama_url=ollama_url,
        model=model,
        debug=debug
    )
