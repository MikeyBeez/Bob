"""
Bob Brain Init Integration
Adds bob_brain_init to Bob's available MCP tools
"""

import sys
from pathlib import Path

# Ensure we can import Bob's tools
bob_path = Path(__file__).parent.parent.parent
sys.path.append(str(bob_path))

from tools.bob_brain_init_mcp import bob_brain_init_tool


def register_bob_brain_init():
    """Register bob_brain_init as an available MCP tool for Bob."""
    
    return {
        "name": "bob_brain_init",
        "description": "Initialize Bob's brain system with protocol loading and intelligent routing",
        "function": bob_brain_init_tool,
        "parameters": {
            "user_message": {
                "type": "string",
                "description": "User's message for context analysis and protocol selection",
                "required": False,
                "default": ""
            },
            "context_budget": {
                "type": "number", 
                "description": "Context budget to use (0.0-1.0, default: 0.35)",
                "required": False,
                "default": 0.35
            },
            "verbose": {
                "type": "boolean",
                "description": "Include detailed initialization information",
                "required": False,
                "default": True
            }
        },
        "category": "intelligence",
        "priority": "critical",
        "usage": "Always run first in each session to load protocols and prevent hallucination"
    }


# Auto-register when imported
BOB_BRAIN_INIT_TOOL = register_bob_brain_init()
