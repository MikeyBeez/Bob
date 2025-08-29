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
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

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
        self.console = Console()
        self.running = True
        
    async def start(self):
        """Start Bob's interactive session."""
        self.show_welcome()
        
        while self.running:
            try:
                # Get user input with Rich styling
                user_input = Prompt.ask("💬", console=self.console).strip()
                
                # Handle system commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    await self.goodbye()
                    break
                elif user_input.lower() == 'clear':
                    self.console.clear()
                    self.show_welcome()
                    continue
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    await self.show_status()
                    continue
                elif user_input.lower().startswith('show tool '):
                    tool_id = user_input[10:].strip()  # Extract tool ID after "show tool "
                    self.console.print(f"🔍 Looking up tool execution: {tool_id}", style="dim cyan")
                    await self.show_tool_execution(tool_id)
                    continue
                elif user_input.lower() == 'list tools':
                    self.show_recent_tools()
                    continue
                
                # Process with Bob's brain system
                if user_input:
                    response = await self.bridge.chat_with_tools(user_input)
                    
                    # Display the response if we got one
                    if response and response.strip():
                        # Check if this is intelligence system output (already formatted)
                        if "🧠 **Intelligent Analysis Complete**" in response:
                            # This is formatted intelligence output - display as-is
                            self.console.print(response)
                        else:
                            # This is regular conversation - format as Bob response
                            self.console.print(f"🤖 Bob: {response}", style="cyan bold")
                    
                    self.console.print()  # Add spacing
                    
            except KeyboardInterrupt:
                await self.goodbye()
                break
            except Exception as e:
                self.console.print(f"🤖 Bob: I encountered an issue ({str(e)}), but I'm still here to help!", style="cyan bold")
                self.console.print()
    
    def show_welcome(self):
        """Show welcome message."""
        welcome_panel = Panel(
            Text.assemble(
                ("🤖 Bob - LLM-as-Kernel Intelligence System\n", "cyan bold"),
                ("💬 Claude Desktop Experience + Brain System Integration\n", "white"),
                ("🧠 72 tools and 54+ protocols ready\n\n", "green"),
                ("Just chat naturally - I'll use my brain system tools when needed!\n", "yellow"),
                ("💡 Type 'help' for guidance, 'status' for system info, 'exit' to quit", "dim white")
            ),
            title="Welcome to Bob",
            border_style="cyan"
        )
        self.console.print(welcome_panel)
        self.console.print()
    
    def show_help(self):
        """Show help information."""
        tool_info = self.bridge.get_tool_info()
        
        self.console.print("🤖 Bob Help - Natural AI Assistant", style="cyan bold")
        print("   • Type 'show tool T001' to see detailed call/response")
        print("   • Type 'list tools' to see recent tool executions")
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
    
    async def show_tool_execution(self, tool_id: str):
        """Show detailed information about a tool execution."""
        execution = self.bridge.get_tool_execution(tool_id)
        
        if "error" in execution:
            self.console.print(f"❌ {execution['error']}", style="red bold")
            return
        
        from rich.syntax import Syntax
        import json
        
        # Show the tool call
        self.console.print(Panel(
            f"🔧 **Tool:** {execution['tool_name']}\n" +
            f"💭 **Reasoning:** {execution['call']['reasoning']}\n" +
            f"📅 **Executed:** {execution['timestamp']:.2f}s ago",
            title=f"Tool Execution {tool_id}",
            border_style="cyan"
        ))
        
        # Show the request
        request_json = json.dumps(execution['call']['parameters'], indent=2)
        self.console.print(Panel(
            Syntax(request_json, "json", theme="monokai", line_numbers=False),
            title="📤 Request",
            border_style="yellow"
        ))
        
        # Show the response
        response_json = json.dumps(execution['response'], indent=2)
        border_color = "green" if execution['success'] else "red"
        response_title = "✅ Response" if execution['success'] else "❌ Response (Error)"
        
        self.console.print(Panel(
            Syntax(response_json, "json", theme="monokai", line_numbers=False),
            title=response_title,
            border_style=border_color
        ))
        
        self.console.print()
    
    def show_recent_tools(self):
        """Show list of recent tool executions."""
        recent = self.bridge.list_recent_tool_executions()
        
        if not recent:
            self.console.print("💭 No recent tool executions found.", style="dim")
            return
        
        from rich.table import Table
        
        table = Table(title="Recent Tool Executions")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Tool", style="yellow")
        table.add_column("Status", style="white")
        table.add_column("Reasoning", style="dim white")
        
        for exec in recent:
            status = "✅ Success" if exec['success'] else "❌ Error"
            table.add_row(
                exec['id'],
                exec['tool'],
                status,
                exec['reasoning']
            )
        
        self.console.print(table)
        self.console.print()
        self.console.print("🔍 Use `show tool <ID>` to see full details", style="dim cyan")
        self.console.print()
    
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
