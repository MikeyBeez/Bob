"""
Bob Protocols Module - Async Protocol System Integration

Provides Bob-specific protocol management with async execution,
background processing, and intelligent workflow orchestration.
"""

from .async_protocol_engine import (
    BobProtocolEngine,
    ProtocolDefinition,
    ProtocolStep,
    ProtocolExecution,
    ProtocolStatus,
    ProtocolPriority,
    create_bob_protocol_engine
)

__all__ = [
    "BobProtocolEngine",
    "ProtocolDefinition", 
    "ProtocolStep",
    "ProtocolExecution",
    "ProtocolStatus",
    "ProtocolPriority",
    "create_bob_protocol_engine"
]

__version__ = "1.0.0"
__description__ = "Bob LLM-as-Kernel Intelligence System - Async Protocol Engine"
