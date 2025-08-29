#!/usr/bin/env python3
"""
Test Bob's protocol handling intelligence
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob_brain_intelligence import BobBrainIntelligence

def test_protocol_intent():
    """Test that protocol requests are correctly classified"""
    
    mock_brain_tools = {}
    intelligence = BobBrainIntelligence(mock_brain_tools)
    
    test_cases = [
        {
            "message": "what protocols can you see?",
            "expected_intent": "protocol",
            "expected_tools": ["protocol_list"],
            "description": "Protocol listing request"
        },
        {
            "message": "I want a list of all your protocols",
            "expected_intent": "protocol", 
            "expected_tools": ["protocol_list"],
            "description": "Direct protocol list request"
        },
        {
            "message": "show me available protocols",
            "expected_intent": "protocol",
            "expected_tools": ["protocol_list"],
            "description": "Show protocols request"
        },
        {
            "message": "what protocols are available?",
            "expected_intent": "protocol",
            "expected_tools": ["protocol_list"],
            "description": "Available protocols query"
        }
    ]
    
    print("🤖 Testing Bob's Protocol Intent Recognition")
    print("=" * 50)
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: '{test['message']}'")
        
        result = intelligence.analyze_intent(test['message'])
        
        print(f"Expected: {test['expected_intent']}")
        print(f"Got: {result['primary']} (confidence: {result['confidence']:.2f})")
        
        intent_correct = result['primary'] == test['expected_intent']
        
        tools = intelligence.suggest_tool_sequence(result, test['message'])
        suggested_tool_names = [tool.get('tool_name', 'unknown') for tool in tools]
        
        print(f"Expected tools: {test['expected_tools']}")
        print(f"Suggested tools: {suggested_tool_names}")
        
        tools_correct = any(expected in suggested_tool_names for expected in test['expected_tools'])
        
        if intent_correct and tools_correct:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            if not intent_correct:
                print(f"   Intent mismatch: expected {test['expected_intent']}, got {result['primary']}")
            if not tools_correct:
                print(f"   Tool mismatch: expected {test['expected_tools']}, got {suggested_tool_names}")
            all_passed = False
        
        if result.get('all_scores'):
            print("   All scores:", {k: f"{v['score']:.2f}" for k, v in result['all_scores'].items()})
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Bob will now use real protocols.")
    else:
        print("❌ Some tests FAILED. Need further fixes.")
    
    return all_passed

if __name__ == "__main__":
    test_protocol_intent()
