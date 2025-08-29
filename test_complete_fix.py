#!/usr/bin/env python3
"""Test the complete fixed system"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from bob import BobDesktopExperience

async def simulate_user_session():
    """Simulate a complete user session with the BS test and tool inspection."""
    bob = BobDesktopExperience()
    
    print("🧪 Simulating User Session with Fixed BS Detection")
    print("=" * 60)
    
    # Step 1: Test the BS prompt
    print("\\n1. User asks: 'Can you analyze this for BS: This revolutionary quantum AI blockchain will solve world hunger and cure cancer instantly!'")
    response = await bob.bridge.chat_with_tools("Can you analyze this for BS: This revolutionary quantum AI blockchain will solve world hunger and cure cancer instantly!")
    print(f"   ✅ Response generated: {len(response)} characters")
    
    # Step 2: List recent tools
    print("\\n2. User types: 'list tools'")
    bob.show_recent_tools()
    
    # Step 3: Show specific tool details
    print("\\n3. User types: 'show tool T001'")
    await bob.show_tool_execution("T001")
    
    print("\\n✅ Session complete! Both BS detection and tool inspection should be working.")

if __name__ == "__main__":
    asyncio.run(simulate_user_session())
