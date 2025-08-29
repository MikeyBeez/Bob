#!/usr/bin/env python3
"""
Bob Brain Init MCP Tool
Provides bob_brain_init as an MCP tool for integration with Claude Desktop
"""

import sys
import json
from pathlib import Path

# Add Bob to path
bob_path = Path(__file__).parent.parent  # Go up one level from tools/
sys.path.append(str(bob_path))

from bob_brain_init import bob_brain_init as brain_init_func


def bob_brain_init_tool(user_message: str = "", context_budget: float = 0.35, verbose: bool = True) -> dict:
    """
    MCP Tool: Initialize Bob's brain system with protocol loading and intelligent routing.
    
    This is Bob's equivalent to brain_init_v5_working:
    - Loads Master Protocol Index with 5 active protocols
    - Analyzes user intent and provides protocol guidance
    - Sets up intelligent tool routing to prevent hallucination
    - Provides task-appropriate protocol recommendations
    
    Args:
        user_message: User's message for context analysis and protocol selection
        context_budget: Context budget to use (default: 0.35 = 35%)
        verbose: Include detailed initialization information
        
    Returns:
        dict: Comprehensive initialization results including:
        - Protocol system status (5 protocols loaded)
        - Intelligence system configuration  
        - User-specific protocol guidance
        - Tool routing recommendations
        - Anti-hallucination safeguards
    """
    
    try:
        # Call the main brain init function
        results = brain_init_func(
            user_message=user_message,
            context_budget=context_budget, 
            verbose=False  # Handle verbose output in MCP layer
        )
        
        # Add MCP-specific information
        results["mcp_integration"] = {
            "tool_name": "bob_brain_init",
            "available_via_mcp": True,
            "bob_location": str(bob_path),
            "master_protocol_index": str(bob_path / "protocols" / "MASTER_PROTOCOL_INDEX.md")
        }
        
        # Add verbose information if requested
        if verbose:
            results["verbose_info"] = {
                "initialization_summary": f"Loaded {results['protocol_system']['total_protocols']} protocols",
                "intelligence_status": f"{results['intelligence_system']['pattern_count']} intent patterns active",
                "session_ready": results['session_info']['ready_for_interaction'],
                "context_efficiency": f"{results['context_loading']['budget_used']*100:.1f}% context used"
            }
            
            if 'user_analysis' in results:
                results["verbose_info"]["user_guidance"] = {
                    "detected_intent": results['user_analysis']['detected_intent'],
                    "confidence": results['user_analysis']['confidence'],
                    "primary_protocols": results['user_analysis']['suggested_protocols']['primary'],
                    "recommended_tools": [tool.get('tool_name', 'unknown') for tool in results['user_analysis']['tool_sequence']],
                    "key_guidance": results['user_analysis']['guidance']
                }
        
        return results
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Bob brain initialization failed: {str(e)}",
            "error_type": type(e).__name__,
            "fallback_advice": "Try running with simpler parameters or check Bob system status"
        }


if __name__ == "__main__":
    # Test the MCP tool
    test_message = "what protocols can you see?"
    
    print("🧪 Testing Bob Brain Init MCP Tool")
    print("=" * 50)
    
    results = bob_brain_init_tool(user_message=test_message, verbose=True)
    
    print(json.dumps(results, indent=2))
