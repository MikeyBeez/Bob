#!/usr/bin/env python3
"""Test the fixed Bob interface"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob_ollama_bridge import BrainSystemFunctionBridge

async def test_fixed_bob():
    """Test that Bob now properly displays intelligence results."""
    bridge = BrainSystemFunctionBridge()
    
    print("🧪 Testing Bob's Fixed Intelligence Display...")
    print("=" * 50)
    
    # Test 1: System status
    print("\n🔍 Test 1: System Status Request")
    response = await bridge.chat_with_tools("What's my system status?")
    print(f"Response type: {type(response)}")
    print(f"Response length: {len(response) if response else 0}")
    print(f"Contains intelligence marker: {'🧠 **Intelligent Analysis Complete**' in str(response)}")
    
    if response and response.strip():
        print("FULL RESPONSE:")
        print("-" * 30)
        print(response)
        print("-" * 30)
    else:
        print("❌ No response received!")
    
    # Test 2: Analysis request
    print("\n🔍 Test 2: BS Analysis Request")
    response2 = await bridge.chat_with_tools("Analyze this for BS: This is the greatest thing ever!")
    print(f"Response 2 type: {type(response2)}")
    print(f"Response 2 length: {len(response2) if response2 else 0}")
    
    if response2 and response2.strip():
        print("FULL RESPONSE 2:")
        print("-" * 30)
        print(response2)
        print("-" * 30)
    else:
        print("❌ No response 2 received!")

if __name__ == "__main__":
    asyncio.run(test_fixed_bob())
