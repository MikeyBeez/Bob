#!/usr/bin/env python3
"""Debug Bob's tool execution to see where results are lost"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob_ollama_bridge import BrainSystemFunctionBridge

async def debug_bob_intelligence():
    """Debug Bob's intelligence system step by step."""
    bridge = BrainSystemFunctionBridge()
    
    test_message = "What's my system status?"
    
    print("🔍 Step 1: Analyzing Intent...")
    intent_analysis = bridge.intelligence.analyze_intent(test_message)
    print(f"   Intent: {intent_analysis['primary']} (confidence: {intent_analysis['confidence']:.2f})")
    
    print("\n🔍 Step 2: Generating Strategy...")
    strategy = bridge.intelligence.generate_smart_response_strategy(intent_analysis, test_message)
    print(f"   Tools to execute: {len(strategy['tools']['sequence'])}")
    for tool in strategy['tools']['sequence']:
        print(f"   - {tool['tool_name']}: {tool['reasoning']}")
    
    print("\n🔍 Step 3: Executing Tool Directly...")
    tool_name = strategy['tools']['sequence'][0]['tool_name']
    parameters = strategy['tools']['sequence'][0]['parameters']
    result = await bridge.execute_brain_tool(tool_name, parameters)
    print(f"   Raw result: {result}")
    
    print("\n🔍 Step 4: Formatting Result...")
    formatted = bridge._format_tool_result(tool_name, result, "Test execution")
    print(f"   Formatted result:")
    print(formatted)
    
    print("\n🔍 Step 5: Testing Full Intelligence Pipeline...")
    response = await bridge._execute_intelligent_tool_sequence(test_message, strategy)
    print(f"   Final response: {response}")

if __name__ == "__main__":
    asyncio.run(debug_bob_intelligence())
