#!/usr/bin/env python3
"""Test intent analysis specifically"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob_brain_intelligence import BobBrainIntelligence

def test_intent_analysis():
    """Test intent analysis for various messages."""
    # Mock brain_tools for testing
    intelligence = BobBrainIntelligence({})
    
    test_messages = [
        "What's my system status?",
        "Analyze this for BS: This is the greatest thing ever!",
        "Can you analyze this text for bullshit: This is amazing!",
        "Please detect bullshit in this: Best product ever!",
        "Check this for analysis: Perfect solution!"
    ]
    
    print("🧠 Intent Analysis Test")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔍 Test {i}: \"{message}\"")
        
        intent = intelligence.analyze_intent(message)
        strategy = intelligence.generate_smart_response_strategy(intent, message)
        
        print(f"   Intent: {intent['primary']} (confidence: {intent['confidence']:.2f})")
        print(f"   Tools: {len(strategy['tools']['sequence'])}")
        for tool in strategy['tools']['sequence']:
            print(f"     - {tool.get('tool_name', tool.get('action', 'Unknown'))}")
        print(f"   All detected intents: {list(intent['all_scores'].keys())}")

if __name__ == "__main__":
    test_intent_analysis()
