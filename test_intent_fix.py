#!/usr/bin/env python3
"""
Test script to verify Bob's intent analysis correctly classifies git requests
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob_brain_intelligence import BobBrainIntelligence

def test_git_intent_classification():
    """Test that git-related requests are correctly classified as development intent"""
    
    # Mock brain_tools (not used in intent analysis)
    mock_brain_tools = {}
    
    # Initialize intelligence system
    intelligence = BobBrainIntelligence(mock_brain_tools)
    
    # Test cases
    test_cases = [
        {
            "message": "Check the git status of this project",
            "expected_intent": "development",
            "expected_tools": ["git_status"],
            "description": "Git status request should be development intent"
        },
        {
            "message": "What's the repository status?",
            "expected_intent": "development", 
            "expected_tools": ["git_status"],
            "description": "Repository status should be development intent"
        },
        {
            "message": "Show me the brain status",
            "expected_intent": "system",
            "expected_tools": ["brain_status"],
            "description": "Brain status should remain system intent"
        },
        {
            "message": "Check system health",
            "expected_intent": "system",
            "expected_tools": ["brain_status"],
            "description": "System health should be system intent"
        },
        {
            "message": "git commit the changes",
            "expected_intent": "development",
            "expected_tools": ["git_status"],
            "description": "Git commit should be development intent"
        }
    ]
    
    print("🧠 Testing Bob's Intent Analysis Fix")
    print("=" * 50)
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: '{test['message']}'")
        
        # Analyze intent
        result = intelligence.analyze_intent(test['message'])
        
        print(f"Expected: {test['expected_intent']}")
        print(f"Got: {result['primary']} (confidence: {result['confidence']:.2f})")
        
        # Check if intent is correct
        intent_correct = result['primary'] == test['expected_intent']
        
        # Get tool suggestions
        tools = intelligence.suggest_tool_sequence(result, test['message'])
        suggested_tool_names = [tool.get('tool_name', 'unknown') for tool in tools]
        
        print(f"Expected tools: {test['expected_tools']}")
        print(f"Suggested tools: {suggested_tool_names}")
        
        # Check if at least one expected tool is suggested
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
        
        # Show all intent scores for debugging
        if result.get('all_scores'):
            print("   All scores:", {k: f"{v['score']:.2f}" for k, v in result['all_scores'].items()})
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Bob's intent analysis is fixed.")
    else:
        print("❌ Some tests FAILED. Need further fixes.")
    
    return all_passed

if __name__ == "__main__":
    test_git_intent_classification()
