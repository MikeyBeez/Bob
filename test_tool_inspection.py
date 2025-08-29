#!/usr/bin/env python3
"""Test Bob's tool inspection system"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob import BobDesktopExperience

async def test_tool_inspection():
    """Test Bob's tool tracking and inspection capabilities."""
    bob = BobDesktopExperience()
    
    print("🧪 Testing Bob's Tool Inspection System")
    print("=" * 50)
    
    # First, trigger some tool executions
    print("\n1. Executing tools to generate history...")
    await bob.bridge.chat_with_tools("What's my system status?")
    await bob.bridge.chat_with_tools("Analyze this for BS: This is amazing!")
    
    # Test listing recent tools
    print("\n2. Testing 'list tools' command...")
    bob.show_recent_tools()
    
    # Test showing specific tool details
    print("\n3. Testing 'show tool T001' command...")
    await bob.show_tool_execution("T001")
    
    print("\n4. Testing 'show tool T002' command...")
    await bob.show_tool_execution("T002")
    
    # Test invalid tool ID
    print("\n5. Testing invalid tool ID...")
    await bob.show_tool_execution("T999")

if __name__ == "__main__":
    asyncio.run(test_tool_inspection())
