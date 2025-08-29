"""
Agent submodules for Bob system orchestration.

This package contains the Phase 3 agent integration components:
- SystemOrchestrator: Coordinates all subsystems  
- KnowledgeManager: Manages knowledge storage and retrieval
- IntelligenceLoop: Implements canonical intelligence loop
- ContextAssembler: Assembles context from multiple sources
- ResponseGenerator: Generates responses using LLM integration
"""

from .orchestrator import SystemOrchestrator
from .knowledge_manager import KnowledgeManager
from .intelligence_loop import IntelligenceLoop
from .context_assembler import ContextAssembler
from .response_generator import ResponseGenerator

__all__ = [
    "SystemOrchestrator",
    "KnowledgeManager", 
    "IntelligenceLoop",
    "ContextAssembler",
    "ResponseGenerator"
]
