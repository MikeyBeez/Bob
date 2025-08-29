#!/usr/bin/env python3
"""Test improved BS detection"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob_ollama_bridge import BrainSystemFunctionBridge

async def test_improved_bs_detection():
    """Test the improved bullshit detection."""
    bridge = BrainSystemFunctionBridge()
    
    test_texts = [
        "This revolutionary quantum AI blockchain will solve world hunger and cure cancer instantly!",
        "Our product offers a 500% guaranteed ROI with zero risk and unlimited potential!",
        "This is a simple product that might help with some tasks.",
        "We have developed a new approach to data processing that shows promising results in early testing."
    ]
    
    print("🕵️ Testing Improved BS Detection")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n🔍 Test {i}: \"{text[:50]}...\"")
        result = await bridge.execute_brain_tool("detect_bullshit", {"text": text})
        
        print(f"   BS Score: {result['bullshit_score']:.2f}/1.0")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Indicators: {result['indicators']}")

if __name__ == "__main__":
    asyncio.run(test_improved_bs_detection())
