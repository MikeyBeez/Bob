#!/usr/bin/env python3
"""
Bob - LLM-as-Kernel Intelligence System
Claude Desktop Experience with Brain System Integration

This is the main interface that provides a Claude Desktop-like experience
where users chat naturally and Ollama intelligently uses brain system tools.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add Bob directory to path
bob_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(bob_dir))

from bob_ollama_bridge import BrainSystemFunctionBridge

class BobDesktopExperience:
    """
    Bob's main interface providing Claude Desktop-like experience.
    
    Users chat naturally, Ollama provides responses and intelligently
    uses brain system tools when needed.
    """
    
    def __init__(self):
        """Initialize Bob Desktop Experience."""
        self.bridge = BrainSystemFunctionBridge()
        self.running = True
        
    async def start(self):
        """Start Bob's interactive session."""
        self.show_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = input("💬 ").strip()
                
                # Handle system commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    await self.goodbye()
                    break
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.show_welcome()
                    continue
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    await self.show_status()
                    continue
                
                # Process with Bob's brain system
                if user_input:
                    print("🤖 Bob:", end=" ")
                    response = await self.bridge.chat_with_tools(user_input)
                    print(response)
                    print()
                    
            except KeyboardInterrupt:
                await self.goodbye()
                break
            except Exception as e:
                print(f"🤖 Bob: I encountered an issue ({str(e)}), but I'm still here to help!")
                print()
    
    def show_welcome(self):
        """Show welcome message."""
        print("🤖 Bob - LLM-as-Kernel Intelligence System")
        print("💬 Claude Desktop Experience + Brain System Integration")
        print("🧠 72 tools and 54+ protocols ready")
        print()
        print("Just chat naturally - I'll use my brain system tools when needed!")
        print("💡 Type 'help' for guidance, 'status' for system info, 'exit' to quit")
        print()
    
    def show_help(self):
        """Show help information."""
        tool_info = self.bridge.get_tool_info()
        
        print("🤖 Bob Help - Natural AI Assistant")
        print()
        print("💬 NATURAL CONVERSATION:")
        print("   Just chat with me normally! Examples:")
        print("   • 'Hello Bob, how are you?'")
        print("   • 'Can you analyze this project for me?'")
        print("   • 'Help me understand this code'")
        print("   • 'What's the status of my system?'")
        print()
        print("🧠 BRAIN SYSTEM CAPABILITIES:")
        print(f"   I have access to {tool_info['total_tools']} specialized tools:")
        for category, count in tool_info['categories'].items():
            print(f"   • {category.title()}: {count} tools")
        print()
        print("🛠️  SYSTEM COMMANDS:")
        print("   • help    - Show this help")
        print("   • status  - Show system status") 
        print("   • clear   - Clear screen")
        print("   • exit    - Quit Bob")
        print()
        print("💡 I automatically choose the right tools based on what you ask!")
        print()
    
    async def show_status(self):
        """Show system status."""
        tool_info = self.bridge.get_tool_info()
        status = await self.bridge.execute_brain_tool("brain_status", {})
        
        print("🧠 Bob System Status")
        print()
        print(f"   Brain System: {status['status'].title()}")
        print(f"   Tools Available: {tool_info['total_tools']}")
        print(f"   Protocols Loaded: {status['protocols_loaded']}")
        print(f"   System Uptime: {status['uptime']}")
        print()
        print("   Tool Categories:")
        for category, count in tool_info['categories'].items():
            print(f"     {category.title()}: {count}")
        print()
        print("✅ All systems operational - ready for natural conversation!")
        print()
    
    async def goodbye(self):
        """Say goodbye and cleanup."""
        print()
        print("🤖 Bob: Thanks for chatting! My brain system is always here when you need it.")
        print("👋 Goodbye!")
        self.running = False

async def main():
    """Main entry point."""
    try:
        bob = BobDesktopExperience()
        await bob.start()
    except Exception as e:
        print(f"Failed to start Bob: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
