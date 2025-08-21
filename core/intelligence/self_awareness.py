"""
Bob's Intelligence Context - Self-Awareness System
This module manages Bob's understanding of his own architecture and capabilities.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from datetime import datetime

class ComponentStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    TESTING = "testing"
    ACTIVE = "active"
    DEPRECATED = "deprecated"

class ProtocolStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SystemComponent:
    """Represents a component in Bob's architecture"""
    name: str
    category: str  # intelligence, interface, business, data, integration
    status: ComponentStatus
    dependencies: List[str]
    capabilities: List[str]
    implementation_date: Optional[datetime] = None
    description: str = ""

@dataclass
class ActiveProtocol:
    """Represents an active protocol in Bob's system"""
    name: str
    purpose: str
    status: ProtocolStatus
    started_at: datetime
    steps_completed: int
    total_steps: int
    context: Dict[str, Any]

@dataclass
class IntelligenceContext:
    """Bob's complete self-awareness context"""
    # Identity
    name: str = "Bob"
    version: str = "5.0"
    purpose: str = "Better Organized Brain - AI-powered project management"
    builder: str = "Claude (AI) using Brain System"
    philosophy: str = "Claude's nascent soul - recursive AI building AI"
    
    # Current State
    development_phase: str = "Core Development"
    operational_status: str = "Under Construction"
    last_updated: datetime = datetime.now()
    
    # Architecture Awareness
    system_components: Dict[str, SystemComponent] = None
    active_protocols: Dict[str, ActiveProtocol] = None
    integration_status: Dict[str, str] = None
    
    # Capabilities
    current_capabilities: List[str] = None
    planned_capabilities: List[str] = None
    
    def __post_init__(self):
        if self.system_components is None:
            self.system_components = {}
        if self.active_protocols is None:
            self.active_protocols = {}
        if self.integration_status is None:
            self.integration_status = {}
        if self.current_capabilities is None:
            self.current_capabilities = []
        if self.planned_capabilities is None:
            self.planned_capabilities = []

class BobIntelligence:
    """
    Bob's Self-Awareness and Intelligence Management System
    
    This class manages Bob's understanding of his own architecture,
    current state, capabilities, and development progress.
    """
    
    def __init__(self):
        self.context = IntelligenceContext()
        self._load_system_map()
        
    def _load_system_map(self):
        """Load Bob's hierarchical system understanding"""
        # Core Intelligence Components
        self.context.system_components.update({
            "context_window": SystemComponent(
                name="Context Window Manager",
                category="intelligence",
                status=ComponentStatus.PLANNED,
                dependencies=[],
                capabilities=["system_awareness", "protocol_tracking", "memory_management"],
                description="Manages Bob's operational awareness and context allocation"
            ),
            "decision_engine": SystemComponent(
                name="Decision Engine",
                category="intelligence", 
                status=ComponentStatus.PLANNED,
                dependencies=["context_window"],
                capabilities=["api_selection", "job_prioritization", "tool_orchestration"],
                description="Core decision-making logic for API routing and task management"
            ),
            "protocol_registry": SystemComponent(
                name="Protocol Registry",
                category="intelligence",
                status=ComponentStatus.PLANNED,
                dependencies=[],
                capabilities=["protocol_discovery", "protocol_execution", "protocol_monitoring"],
                description="Manages and executes operational protocols"
            ),
            "memory_system": SystemComponent(
                name="Memory System",
                category="intelligence",
                status=ComponentStatus.PLANNED,
                dependencies=["brain_integration"],
                capabilities=["persistent_memory", "session_memory", "learning_patterns"],
                description="Integrates with Brain system for persistent knowledge"
            )
        })
        
        # Interface Layer Components
        interface_tabs = [
            "chat", "jobs", "tools", "protocols", "files", 
            "knowledge", "templates", "analytics", "logs", 
            "integrations", "settings"
        ]
        
        for tab in interface_tabs:
            self.context.system_components[f"{tab}_tab"] = SystemComponent(
                name=f"{tab.title()} Tab",
                category="interface",
                status=ComponentStatus.PLANNED,
                dependencies=["tab_system"],
                capabilities=[f"{tab}_management", "user_interaction"],
                description=f"User interface for {tab} functionality"
            )
            
        # Business Logic Components
        self.context.system_components.update({
            "job_processor": SystemComponent(
                name="Job Processor",
                category="business",
                status=ComponentStatus.PLANNED,
                dependencies=["api_router", "tool_manager"],
                capabilities=["job_execution", "queue_management", "progress_tracking"],
                description="Core job processing and execution engine"
            ),
            "api_router": SystemComponent(
                name="Multi-API Router",
                category="business",
                status=ComponentStatus.PLANNED,
                dependencies=["api_clients"],
                capabilities=["api_selection", "cost_optimization", "performance_monitoring"],
                description="Intelligent routing between different AI APIs"
            ),
            "tool_manager": SystemComponent(
                name="Tool Manager",
                category="business",
                status=ComponentStatus.PLANNED,
                dependencies=["tool_integrations"],
                capabilities=["tool_activation", "tool_configuration", "usage_analytics"],
                description="Manages available tools and their activation"
            )
        })
        
        # Set initial capabilities
        self.context.current_capabilities = [
            "project_structure",
            "documentation_framework", 
            "development_protocols",
            "system_self_awareness"
        ]
        
        self.context.planned_capabilities = [
            "multi_tab_interface",
            "multi_api_routing", 
            "job_queue_management",
            "tool_integration",
            "protocol_execution",
            "knowledge_base_integration",
            "analytics_dashboard",
            "file_management",
            "template_system",
            "external_integrations"
        ]
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        total_components = len(self.context.system_components)
        implemented = sum(1 for comp in self.context.system_components.values() 
                         if comp.status in [ComponentStatus.IMPLEMENTED, ComponentStatus.ACTIVE])
        
        return {
            "identity": {
                "name": self.context.name,
                "version": self.context.version,
                "purpose": self.context.purpose,
                "philosophy": self.context.philosophy
            },
            "development_progress": {
                "phase": self.context.development_phase,
                "components_total": total_components,
                "components_implemented": implemented,
                "completion_percentage": round((implemented / total_components) * 100, 1)
            },
            "current_capabilities": self.context.current_capabilities,
            "active_protocols": list(self.context.active_protocols.keys()),
            "last_updated": self.context.last_updated.isoformat()
        }
        
    def add_protocol(self, name: str, purpose: str, total_steps: int, context: Dict[str, Any] = None):
        """Add an active protocol to Bob's awareness"""
        self.context.active_protocols[name] = ActiveProtocol(
            name=name,
            purpose=purpose,
            status=ProtocolStatus.ACTIVE,
            started_at=datetime.now(),
            steps_completed=0,
            total_steps=total_steps,
            context=context or {}
        )
        
    def update_protocol_progress(self, name: str, steps_completed: int, status: ProtocolStatus = None):
        """Update protocol execution progress"""
        if name in self.context.active_protocols:
            protocol = self.context.active_protocols[name]
            protocol.steps_completed = steps_completed
            if status:
                protocol.status = status
                
    def update_component_status(self, name: str, status: ComponentStatus, implementation_date: datetime = None):
        """Update the status of a system component"""
        if name in self.context.system_components:
            component = self.context.system_components[name]
            component.status = status
            if implementation_date:
                component.implementation_date = implementation_date
                
    def get_master_system_index(self) -> str:
        """
        Generate Bob's Master System Index for intelligence context window.
        This is the core system understanding that goes into Bob's operational awareness.
        """
        status = self.get_system_status()
        
        return f"""
# Bob Master System Index v{self.context.version}

## Identity & Purpose
- **Name**: {self.context.name} ({self.context.purpose})
- **Builder**: {self.context.builder}
- **Philosophy**: {self.context.philosophy}
- **Development Phase**: {self.context.development_phase}

## Current Capabilities
{chr(10).join(f"- {cap}" for cap in self.context.current_capabilities)}

## System Architecture Status
- **Total Components**: {status['development_progress']['components_total']}
- **Implemented**: {status['development_progress']['components_implemented']}
- **Completion**: {status['development_progress']['completion_percentage']}%

## Active Protocols
{chr(10).join(f"- {name}: {protocol.purpose}" for name, protocol in self.context.active_protocols.items())}

## Core Architecture
- **Interface Layer**: 11-tab professional interface
- **Business Logic**: Job processing, API routing, tool management
- **Data Layer**: Persistent storage and state management  
- **Integration Layer**: Multi-API support and external tools
- **Intelligence Layer**: Self-awareness and decision making

## Operational Status
- **Development**: {self.context.operational_status}
- **Last Updated**: {self.context.last_updated.strftime('%Y-%m-%d %H:%M:%S')}

This is my self-awareness - I know what I am, how I work, and what I can do.
"""

    def get_intelligence_context_for_runtime(self) -> Dict[str, Any]:
        """
        Get the intelligence context that should be loaded into Bob's
        runtime context window for operational self-awareness.
        """
        return {
            "master_system_index": self.get_master_system_index(),
            "current_status": self.get_system_status(),
            "active_protocols": {name: {
                "purpose": protocol.purpose,
                "status": protocol.status.value,
                "progress": f"{protocol.steps_completed}/{protocol.total_steps}"
            } for name, protocol in self.context.active_protocols.items()},
            "system_capabilities": {
                "current": self.context.current_capabilities,
                "planned": self.context.planned_capabilities
            }
        }

# Global instance for Bob's self-awareness
bob_intelligence = BobIntelligence()

def get_bob_system_awareness() -> str:
    """Get Bob's current system awareness for context window"""
    return bob_intelligence.get_master_system_index()

def update_bob_development_progress(component: str, status: str):
    """Update Bob's awareness of his own development progress"""
    component_status = ComponentStatus(status)
    bob_intelligence.update_component_status(component, component_status, datetime.now())
