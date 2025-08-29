#!/usr/bin/env python3
"""
Test Bob's memory tool integration
"""

import sys
from pathlib import Path

# Add Bob to path
sys.path.append(str(Path(__file__).parent))

from bob_brain_intelligence import BobBrainIntelligence

def test_memory_intent():
    """Test memory intent detection and tool routing."""
    
    print("🧪 Testing Bob's Memory Tool Integration")
    print("=" * 50)
    
    # Create intelligence system
    intelligence = BobBrainIntelligence({})
    
    test_cases = [
        {
            "message": "Remember that I like Python programming",
            "expected_intent": "memory",
            "expected_tool": "brain_remember",
            "description": "Memory storage request"
        },
        {
            "message": "What do you remember about me?",
            "expected_intent": "memory", 
            "expected_tool": "brain_recall",
            "description": "Memory recall request"
        },
        {
            "message": "Do you remember what I told you about Python?",
            "expected_intent": "memory",
            "expected_tool": "brain_recall", 
            "description": "Specific memory recall"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: '{test['message']}'")
        
        result = intelligence.analyze_intent(test['message'])
        tools = intelligence.suggest_tool_sequence(result, test['message'])
        
        print(f"Expected: {test['expected_intent']} intent → {test['expected_tool']} tool")
        print(f"Got: {result['primary']} (confidence: {result['confidence']:.2f}) → {[tool.get('tool_name') for tool in tools]}")
        
        intent_correct = result['primary'] == test['expected_intent']
        tools_correct = any(test['expected_tool'] in str(tool) for tool in tools)
        
        if intent_correct and tools_correct:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
            if not intent_correct:
                print(f"   Intent issue: expected {test['expected_intent']}, got {result['primary']}")
            if not tools_correct:
                print(f"   Tool issue: expected {test['expected_tool']}, got {[tool.get('tool_name') for tool in tools]}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Memory tool integration FIXED! Bob should now call actual memory tools.")
    else:
        print("❌ Some memory tests failed. Need further investigation.")
    
    return all_passed

if __name__ == "__main__":
    test_memory_intent()
