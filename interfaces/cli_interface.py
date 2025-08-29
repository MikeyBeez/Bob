"""
cli_interface.py - Interactive Command-Line Interface for Bob Agent

Provides a comprehensive CLI for interacting with the Bob LLM-as-Kernel Intelligence System.
Follows the established modular architecture pattern with clean separation of concerns.

FEATURES:
=========
• Interactive REPL-style interface with command history
• Comprehensive command parsing with argument validation  
• Built-in help system with examples and usage guidance
• Asynchronous operation with proper error handling
• Real-time system status and health monitoring
• Session management with persistence
• Rich output formatting for better user experience
• Command completion and shortcuts
• Batch operation support

AVAILABLE COMMANDS:
==================
Core Intelligence:
  think <prompt>                    - Think about a topic or question
  query <question>                  - Process a user query with full context
  reflect                          - Perform system-wide reflection and adaptation
  learn <experience_json>          - Learn from experience data

Knowledge Management:
  store <knowledge_json>           - Store knowledge with semantic indexing
  retrieve <query>                 - Retrieve relevant knowledge
  knowledge-graph                  - Build and display knowledge graph

System Management:
  status                          - Show system health and status
  metrics                         - Display comprehensive system metrics  
  health                          - Run health check on all subsystems
  init                           - Initialize all systems
  cleanup                        - Clean up system resources

CLI Management:
  help [command]                  - Show help for commands
  history                         - Show command history
  clear                          - Clear screen
  exit/quit                      - Exit the CLI

USAGE EXAMPLES:
==============
$ bob think "What are the implications of quantum computing?"
$ bob query "How does machine learning relate to artificial intelligence?"
$ bob store '{"topic": "AI", "content": "Machine learning is a subset of AI"}'
$ bob retrieve "machine learning"
$ bob status
$ bob help think
"""

import asyncio
import json
import sys
import os
import readline
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
import argparse
import shlex
from contextlib import asynccontextmanager

# Rich formatting for better CLI experience
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import track
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import Bob Agent
try:
    from core.bob_agent_integrated import BobAgentIntegrated, create_bob_agent
    from core.bob_agent_integrated import SystemStatus, SystemMetrics, ThoughtResponse, QueryResponse
except ImportError:
    # Handle relative import for when run as module
    import sys
    from pathlib import Path
    bob_dir = Path(__file__).parent.parent.absolute()
    if str(bob_dir) not in sys.path:
        sys.path.insert(0, str(bob_dir))
    
    from core.bob_agent_integrated import BobAgentIntegrated, create_bob_agent
    from core.bob_agent_integrated import SystemStatus, SystemMetrics, ThoughtResponse, QueryResponse


class BobCLISession:
    """Manages CLI session state and history."""
    
    def __init__(self, session_dir: str = "~/Bob/data/cli_sessions"):
        self.session_dir = Path(session_dir).expanduser()
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = f"session_{int(datetime.now().timestamp())}"
        self.history_file = self.session_dir / f"{self.session_id}_history.json"
        self.command_history: List[Dict[str, Any]] = []
        
        # Load command history for readline
        self.readline_history_file = self.session_dir / "readline_history"
        self._load_readline_history()
    
    def _load_readline_history(self):
        """Load readline command history."""
        if self.readline_history_file.exists():
            try:
                readline.read_history_file(str(self.readline_history_file))
            except Exception:
                pass  # Ignore errors loading history
    
    def save_command(self, command: str, args: List[str], result: Any, success: bool, error: Optional[str] = None):
        """Save command to session history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args,
            "success": success,
            "error": error,
            "result_summary": str(result)[:200] if result else None
        }
        self.command_history.append(entry)
        self._save_history()
    
    def _save_history(self):
        """Save session history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.command_history, f, indent=2)
        except Exception:
            pass  # Ignore save errors
    
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent command history."""
        return self.command_history[-limit:]
    
    def cleanup(self):
        """Clean up session resources."""
        try:
            readline.write_history_file(str(self.readline_history_file))
        except Exception:
            pass


class BobCLI:
    """
    Interactive Command-Line Interface for Bob Agent.
    
    Provides comprehensive CLI functionality with command parsing,
    help system, and rich output formatting.
    """
    
    def __init__(self, 
                 data_path: str = "~/Bob/data",
                 ollama_url: str = "http://localhost:11434",
                 model: str = "llama3.2",
                 debug: bool = False,
                 rich_output: bool = None):
        """
        Initialize Bob CLI.
        
        Args:
            data_path: Path for data storage
            ollama_url: Ollama service URL
            model: Default LLM model
            debug: Enable debug logging
            rich_output: Use rich formatting (auto-detect if None)
        """
        # Configuration
        self.data_path = data_path
        self.ollama_url = ollama_url
        self.model = model
        self.debug = debug
        
        # Rich output setup
        self.rich_output = rich_output if rich_output is not None else RICH_AVAILABLE
        if self.rich_output and RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Bob Agent instance
        self.bob_agent: Optional[BobAgentIntegrated] = None
        
        # CLI session management
        self.session = BobCLISession()
        self.running = False
        
        # Command definitions
        self.commands = self._init_commands()
        
        # Setup command completion
        self._setup_completion()
    
    def _init_commands(self) -> Dict[str, Dict[str, Any]]:
        """Initialize command definitions with metadata."""
        return {
            # Core Intelligence Commands
            "think": {
                "function": self._cmd_think,
                "help": "Think about a topic or question",
                "usage": "think <prompt>",
                "example": 'think "What are the implications of quantum computing?"',
                "async": True
            },
            "query": {
                "function": self._cmd_query,
                "help": "Process a user query with full context",
                "usage": "query <question>",
                "example": 'query "How does machine learning work?"',
                "async": True
            },
            "reflect": {
                "function": self._cmd_reflect,
                "help": "Perform system-wide reflection and adaptation",
                "usage": "reflect",
                "example": "reflect",
                "async": True
            },
            "learn": {
                "function": self._cmd_learn,
                "help": "Learn from experience data",
                "usage": "learn <experience_json>",
                "example": 'learn \'{"outcome": "success", "lesson": "Always validate input"}\'',
                "async": True
            },
            
            # Knowledge Management Commands
            "store": {
                "function": self._cmd_store,
                "help": "Store knowledge with semantic indexing",
                "usage": "store <knowledge_json>",
                "example": 'store \'{"topic": "AI", "content": "Machine learning is a subset"}\'',
                "async": True
            },
            "retrieve": {
                "function": self._cmd_retrieve,
                "help": "Retrieve relevant knowledge",
                "usage": "retrieve <query>",
                "example": 'retrieve "machine learning"',
                "async": True
            },
            "knowledge-graph": {
                "function": self._cmd_knowledge_graph,
                "help": "Build and display knowledge graph",
                "usage": "knowledge-graph",
                "example": "knowledge-graph",
                "async": True
            },
            
            # System Management Commands
            "status": {
                "function": self._cmd_status,
                "help": "Show system health and status",
                "usage": "status",
                "example": "status",
                "async": True
            },
            "metrics": {
                "function": self._cmd_metrics,
                "help": "Display comprehensive system metrics",
                "usage": "metrics",
                "example": "metrics",
                "async": False
            },
            "health": {
                "function": self._cmd_health,
                "help": "Run health check on all subsystems",
                "usage": "health",
                "example": "health",
                "async": True
            },
            "init": {
                "function": self._cmd_init,
                "help": "Initialize all systems",
                "usage": "init",
                "example": "init",
                "async": True
            },
            "cleanup": {
                "function": self._cmd_cleanup,
                "help": "Clean up system resources",
                "usage": "cleanup",
                "example": "cleanup",
                "async": True
            },
            
            # CLI Management Commands
            "help": {
                "function": self._cmd_help,
                "help": "Show help for commands",
                "usage": "help [command]",
                "example": "help think",
                "async": False
            },
            "history": {
                "function": self._cmd_history,
                "help": "Show command history",
                "usage": "history [limit]",
                "example": "history 10",
                "async": False
            },
            "clear": {
                "function": self._cmd_clear,
                "help": "Clear screen",
                "usage": "clear",
                "example": "clear",
                "async": False
            },
            "exit": {
                "function": self._cmd_exit,
                "help": "Exit the CLI",
                "usage": "exit",
                "example": "exit",
                "async": False
            },
            "quit": {
                "function": self._cmd_exit,
                "help": "Exit the CLI",
                "usage": "quit", 
                "example": "quit",
                "async": False
            }
        }
    
    def _setup_completion(self):
        """Setup command completion for readline."""
        def completer(text: str, state: int) -> Optional[str]:
            """Command completion function."""
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
            try:
                return options[state]
            except IndexError:
                return None
        
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
    
    # ================================================
    # MAIN CLI LOOP
    # ================================================
    
    async def start(self):
        """Start the interactive CLI."""
        self._print_welcome()
        
        # Initialize Bob Agent
        self.bob_agent = create_bob_agent(
            data_path=self.data_path,
            ollama_url=self.ollama_url,
            model=self.model,
            debug=self.debug
        )
        
        self.running = True
        
        try:
            while self.running:
                try:
                    # Get user input
                    prompt = self._get_prompt()
                    user_input = input(prompt).strip()
                    
                    # Skip empty input
                    if not user_input:
                        continue
                    
                    # Parse and execute command
                    await self._execute_command(user_input)
                    
                except KeyboardInterrupt:
                    self._print("\n\nUse 'exit' or 'quit' to leave Bob CLI")
                except EOFError:
                    self._print("\nGoodbye!")
                    break
                except Exception as e:
                    self._print_error(f"Unexpected error: {e}")
        
        finally:
            await self._cleanup()
    
    def _get_prompt(self) -> str:
        """Get CLI prompt string."""
        if self.bob_agent and self.bob_agent.initialized:
            status_indicator = "🟢"
        elif self.bob_agent:
            status_indicator = "🟡"
        else:
            status_indicator = "🔴"
        
        return f"{status_indicator} Bob> "
    
    async def _execute_command(self, user_input: str):
        """Parse and execute a command."""
        try:
            # Parse command and arguments
            parts = shlex.split(user_input)
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Check if command exists
            if command not in self.commands:
                self._print_error(f"Unknown command: {command}")
                self._print("Type 'help' to see available commands")
                self.session.save_command(command, args, None, False, "Unknown command")
                return
            
            # Get command info
            cmd_info = self.commands[command]
            
            # Execute command
            start_time = datetime.now()
            try:
                if cmd_info.get("async", False):
                    result = await cmd_info["function"](args)
                else:
                    result = cmd_info["function"](args)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Save successful command
                self.session.save_command(command, args, result, True)
                
                if self.debug:
                    self._print_debug(f"Command executed in {processing_time:.2f}s")
                
            except Exception as e:
                error_msg = str(e)
                self._print_error(f"Command failed: {error_msg}")
                self.session.save_command(command, args, None, False, error_msg)
                
                if self.debug:
                    import traceback
                    self._print_debug(f"Full traceback:\n{traceback.format_exc()}")
        
        except Exception as e:
            self._print_error(f"Failed to parse command: {e}")
    
    # ================================================
    # COMMAND IMPLEMENTATIONS - CORE INTELLIGENCE
    # ================================================
    
    async def _cmd_think(self, args: List[str]) -> str:
        """Think command implementation."""
        if not args:
            self._print_error("Usage: think <prompt>")
            return "Missing prompt"
        
        prompt = " ".join(args)
        
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print(f"🤔 Thinking about: {prompt}")
        
        # Execute thinking
        response = await self.bob_agent.think(prompt)
        
        # Format and display response
        self._display_thought_response(response)
        
        return f"Thought completed with confidence {response.confidence:.2f}"
    
    async def _cmd_query(self, args: List[str]) -> str:
        """Query command implementation."""
        if not args:
            self._print_error("Usage: query <question>")
            return "Missing question"
        
        question = " ".join(args)
        
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print(f"❓ Processing query: {question}")
        
        # Execute query
        response = await self.bob_agent.process_query(question)
        
        # Format and display response
        self._display_query_response(response)
        
        return f"Query processed with confidence {response.confidence:.2f}"
    
    async def _cmd_reflect(self, args: List[str]) -> str:
        """Reflection command implementation."""
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print("🔍 Performing system-wide reflection...")
        
        # Execute reflection
        report = await self.bob_agent.reflect_and_adapt()
        
        # Display reflection report
        self._display_reflection_report(report)
        
        return "Reflection completed"
    
    async def _cmd_learn(self, args: List[str]) -> str:
        """Learn command implementation."""
        if not args:
            self._print_error("Usage: learn <experience_json>")
            return "Missing experience data"
        
        try:
            experience_json = " ".join(args)
            experience = json.loads(experience_json)
        except json.JSONDecodeError as e:
            self._print_error(f"Invalid JSON: {e}")
            return "Invalid JSON format"
        
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print("🧠 Learning from experience...")
        
        # Execute learning
        learning_update = await self.bob_agent.learn_from_experience(experience)
        
        # Display learning results
        self._display_learning_update(learning_update)
        
        return f"Learned {len(learning_update.lessons_learned)} lessons"
    
    # ================================================
    # COMMAND IMPLEMENTATIONS - KNOWLEDGE MANAGEMENT
    # ================================================
    
    async def _cmd_store(self, args: List[str]) -> str:
        """Store knowledge command implementation."""
        if not args:
            self._print_error("Usage: store <knowledge_json>")
            return "Missing knowledge data"
        
        try:
            knowledge_json = " ".join(args)
            knowledge = json.loads(knowledge_json)
        except json.JSONDecodeError as e:
            self._print_error(f"Invalid JSON: {e}")
            return "Invalid JSON format"
        
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print("💾 Storing knowledge...")
        
        # Store knowledge
        success = await self.bob_agent.store_knowledge(knowledge)
        
        if success:
            self._print_success("✅ Knowledge stored successfully")
            return "Knowledge stored"
        else:
            self._print_error("❌ Failed to store knowledge")
            return "Storage failed"
    
    async def _cmd_retrieve(self, args: List[str]) -> str:
        """Retrieve knowledge command implementation."""
        if not args:
            self._print_error("Usage: retrieve <query>")
            return "Missing query"
        
        query = " ".join(args)
        
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print(f"🔍 Retrieving knowledge for: {query}")
        
        # Retrieve knowledge
        results = await self.bob_agent.retrieve_knowledge(query)
        
        # Display results
        self._display_knowledge_results(results)
        
        return f"Found {len(results)} knowledge items"
    
    async def _cmd_knowledge_graph(self, args: List[str]) -> str:
        """Knowledge graph command implementation."""
        # Ensure Bob Agent is initialized
        if not self.bob_agent.initialized:
            self._print("Initializing Bob Agent systems...")
            await self.bob_agent.initialize_systems()
        
        self._print("🕸️ Building knowledge graph...")
        
        # This would be implemented when knowledge graph functionality is added
        self._print_warning("Knowledge graph functionality not yet implemented")
        
        return "Knowledge graph feature pending"
    
    # ================================================
    # COMMAND IMPLEMENTATIONS - SYSTEM MANAGEMENT
    # ================================================
    
    async def _cmd_status(self, args: List[str]) -> str:
        """Status command implementation."""
        if not self.bob_agent:
            self._print_error("Bob Agent not initialized")
            return "Not initialized"
        
        self._print("📊 Checking system status...")
        
        # Get system status
        status = await self.bob_agent.health_check()
        
        # Display status
        self._display_system_status(status)
        
        return f"System health: {status.overall_health:.2f}"
    
    def _cmd_metrics(self, args: List[str]) -> str:
        """Metrics command implementation."""
        if not self.bob_agent:
            self._print_error("Bob Agent not initialized")
            return "Not initialized"
        
        self._print("📈 Collecting system metrics...")
        
        # Get system metrics
        metrics = self.bob_agent.get_system_metrics()
        
        # Display metrics
        self._display_system_metrics(metrics)
        
        return "Metrics displayed"
    
    async def _cmd_health(self, args: List[str]) -> str:
        """Health check command implementation."""
        if not self.bob_agent:
            self._print_error("Bob Agent not initialized")
            return "Not initialized"
        
        self._print("🏥 Running comprehensive health check...")
        
        # Run health check
        health_status = await self.bob_agent.health_check()
        
        # Display detailed health information
        self._display_health_check(health_status)
        
        return f"Health check completed - Score: {health_status.overall_health:.2f}"
    
    async def _cmd_init(self, args: List[str]) -> str:
        """Initialize systems command implementation."""
        if not self.bob_agent:
            self.bob_agent = create_bob_agent(
                data_path=self.data_path,
                ollama_url=self.ollama_url,
                model=self.model,
                debug=self.debug
            )
        
        self._print("🚀 Initializing Bob Agent systems...")
        
        # Initialize systems
        status = await self.bob_agent.initialize_systems()
        
        # Display initialization results
        self._display_system_status(status)
        
        if status.overall_health > 0.8:
            self._print_success("✅ Systems initialized successfully!")
        else:
            self._print_warning("⚠️ Some systems failed to initialize properly")
        
        return f"Initialization completed - Health: {status.overall_health:.2f}"
    
    async def _cmd_cleanup(self, args: List[str]) -> str:
        """Cleanup command implementation."""
        if not self.bob_agent:
            self._print("No systems to clean up")
            return "Nothing to cleanup"
        
        self._print("🧹 Cleaning up system resources...")
        
        # Cleanup Bob Agent
        await self.bob_agent.cleanup()
        
        self._print_success("✅ Cleanup completed")
        
        return "Cleanup completed"
    
    # ================================================
    # COMMAND IMPLEMENTATIONS - CLI MANAGEMENT
    # ================================================
    
    def _cmd_help(self, args: List[str]) -> str:
        """Help command implementation."""
        if not args:
            # Show general help
            self._display_general_help()
        else:
            # Show specific command help
            command = args[0].lower()
            if command in self.commands:
                self._display_command_help(command)
            else:
                self._print_error(f"Unknown command: {command}")
                return "Unknown command"
        
        return "Help displayed"
    
    def _cmd_history(self, args: List[str]) -> str:
        """History command implementation."""
        limit = 20
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                self._print_error("Invalid limit, using default (20)")
        
        history = self.session.get_history(limit)
        self._display_history(history)
        
        return f"Displayed {len(history)} history entries"
    
    def _cmd_clear(self, args: List[str]) -> str:
        """Clear screen command implementation."""
        os.system('clear' if os.name == 'posix' else 'cls')
        return "Screen cleared"
    
    def _cmd_exit(self, args: List[str]) -> str:
        """Exit command implementation."""
        self._print("👋 Goodbye!")
        self.running = False
        return "Exiting"
    
    # ================================================
    # DISPLAY METHODS
    # ================================================
    
    def _display_thought_response(self, response: ThoughtResponse):
        """Display thought response in formatted way."""
        if self.console:
            # Rich formatting
            panel = Panel(
                f"[bold blue]Thought:[/bold blue] {response.thought}\n\n"
                f"[bold green]Confidence:[/bold green] {response.confidence:.2f}\n"
                f"[bold yellow]Processing Time:[/bold yellow] {response.processing_time:.2f}s\n"
                f"[bold purple]Knowledge Used:[/bold purple] {len(response.knowledge_used)} sources\n"
                f"[bold cyan]Reflections:[/bold cyan] {response.reflections_triggered}",
                title="💭 Thought Response",
                border_style="blue"
            )
            self.console.print(panel)
            
            if response.reasoning:
                self.console.print("\n[bold]Reasoning:[/bold]")
                for i, reason in enumerate(response.reasoning, 1):
                    self.console.print(f"  {i}. {reason}")
        
        else:
            # Plain text formatting
            self._print("\n" + "="*50)
            self._print(f"💭 THOUGHT RESPONSE")
            self._print("="*50)
            self._print(f"Thought: {response.thought}")
            self._print(f"Confidence: {response.confidence:.2f}")
            self._print(f"Processing Time: {response.processing_time:.2f}s")
            self._print(f"Knowledge Sources: {len(response.knowledge_used)}")
            self._print(f"Reflections Triggered: {response.reflections_triggered}")
            
            if response.reasoning:
                self._print("\nReasoning:")
                for i, reason in enumerate(response.reasoning, 1):
                    self._print(f"  {i}. {reason}")
            
            self._print("="*50)
    
    def _display_query_response(self, response: QueryResponse):
        """Display query response in formatted way."""
        if self.console:
            # Rich formatting
            panel = Panel(
                f"[bold green]Response:[/bold green] {response.response}\n\n"
                f"[bold blue]Confidence:[/bold blue] {response.confidence:.2f}\n"
                f"[bold yellow]Processing Time:[/bold yellow] {response.processing_time:.2f}s\n"
                f"[bold purple]Sources:[/bold purple] {len(response.sources)}\n"
                f"[bold cyan]Insights:[/bold cyan] {len(response.insights)}",
                title=f"❓ Query: {response.query[:50]}...",
                border_style="green"
            )
            self.console.print(panel)
            
            if response.insights:
                self.console.print("\n[bold]Key Insights:[/bold]")
                for insight in response.insights:
                    self.console.print(f"  • {insight}")
            
            if response.follow_up_suggestions:
                self.console.print("\n[bold]Follow-up Suggestions:[/bold]")
                for suggestion in response.follow_up_suggestions:
                    self.console.print(f"  → {suggestion}")
        
        else:
            # Plain text formatting
            self._print("\n" + "="*50)
            self._print(f"❓ QUERY RESPONSE")
            self._print("="*50)
            self._print(f"Query: {response.query}")
            self._print(f"Response: {response.response}")
            self._print(f"Confidence: {response.confidence:.2f}")
            self._print(f"Sources: {len(response.sources)}")
            
            if response.insights:
                self._print("\nKey Insights:")
                for insight in response.insights:
                    self._print(f"  • {insight}")
            
            if response.follow_up_suggestions:
                self._print("\nFollow-up Suggestions:")
                for suggestion in response.follow_up_suggestions:
                    self._print(f"  → {suggestion}")
            
            self._print("="*50)
    
    def _display_system_status(self, status: SystemStatus):
        """Display system status."""
        if self.console:
            # Create status table
            table = Table(title="🏥 System Health Status")
            table.add_column("Component", style="bold")
            table.add_column("Status", justify="center")
            table.add_column("Health", justify="right")
            
            # Add rows
            components = [
                ("Database", "✅ Ready" if status.database_ready else "❌ Not Ready"),
                ("FileSystem", "✅ Ready" if status.filesystem_ready else "❌ Not Ready"),
                ("Ollama", "✅ Ready" if status.ollama_ready else "❌ Not Ready"),
                ("Reflection", "✅ Ready" if status.reflection_ready else "❌ Not Ready"),
            ]
            
            for name, state in components:
                table.add_row(name, state, "")
            
            table.add_row("Overall", "", f"{status.overall_health:.2f}")
            
            self.console.print(table)
            
            if status.errors:
                self.console.print("\n[bold red]Errors:[/bold red]")
                for error in status.errors:
                    self.console.print(f"  ❌ {error}")
        
        else:
            # Plain text
            self._print("\n🏥 SYSTEM HEALTH STATUS")
            self._print("-" * 30)
            self._print(f"Database: {'✅ Ready' if status.database_ready else '❌ Not Ready'}")
            self._print(f"FileSystem: {'✅ Ready' if status.filesystem_ready else '❌ Not Ready'}")
            self._print(f"Ollama: {'✅ Ready' if status.ollama_ready else '❌ Not Ready'}")
            self._print(f"Reflection: {'✅ Ready' if status.reflection_ready else '❌ Not Ready'}")
            self._print(f"Overall Health: {status.overall_health:.2f}")
            
            if status.errors:
                self._print("\nErrors:")
                for error in status.errors:
                    self._print(f"  ❌ {error}")
    
    def _display_system_metrics(self, metrics: SystemMetrics):
        """Display system metrics."""
        if self.console:
            # Create metrics table
            table = Table(title="📈 System Metrics")
            table.add_column("Metric", style="bold")
            table.add_column("Value", justify="right")
            
            table.add_row("Uptime", f"{metrics.uptime:.1f}s")
            table.add_row("Total Thoughts", str(metrics.total_thoughts))
            table.add_row("Total Queries", str(metrics.total_queries))
            table.add_row("Total Reflections", str(metrics.total_reflections))
            table.add_row("Knowledge Entries", str(metrics.knowledge_entries))
            table.add_row("Learning Updates", str(metrics.learning_updates))
            table.add_row("Avg Response Time", f"{metrics.average_response_time:.2f}s")
            table.add_row("System Efficiency", f"{metrics.system_efficiency:.2f}")
            
            self.console.print(table)
        
        else:
            # Plain text
            self._print("\n📈 SYSTEM METRICS")
            self._print("-" * 25)
            self._print(f"Uptime: {metrics.uptime:.1f}s")
            self._print(f"Total Thoughts: {metrics.total_thoughts}")
            self._print(f"Total Queries: {metrics.total_queries}")
            self._print(f"Total Reflections: {metrics.total_reflections}")
            self._print(f"Knowledge Entries: {metrics.knowledge_entries}")
            self._print(f"Learning Updates: {metrics.learning_updates}")
            self._print(f"Avg Response Time: {metrics.average_response_time:.2f}s")
            self._print(f"System Efficiency: {metrics.system_efficiency:.2f}")
    
    def _display_general_help(self):
        """Display general help information."""
        help_text = """
🤖 Bob LLM-as-Kernel Intelligence System - CLI Help

CORE INTELLIGENCE COMMANDS:
  think <prompt>              - Think about a topic or question
  query <question>            - Process a user query with full context  
  reflect                     - Perform system-wide reflection and adaptation
  learn <experience_json>     - Learn from experience data

KNOWLEDGE MANAGEMENT:
  store <knowledge_json>      - Store knowledge with semantic indexing
  retrieve <query>            - Retrieve relevant knowledge
  knowledge-graph             - Build and display knowledge graph

SYSTEM MANAGEMENT:
  status                      - Show system health and status
  metrics                     - Display comprehensive system metrics
  health                      - Run health check on all subsystems
  init                        - Initialize all systems
  cleanup                     - Clean up system resources

CLI COMMANDS:
  help [command]              - Show help for commands
  history [limit]             - Show command history
  clear                       - Clear screen
  exit/quit                   - Exit the CLI

For detailed help on a specific command, use: help <command>
Example: help think
        """
        
        if self.console:
            self.console.print(Markdown(help_text))
        else:
            self._print(help_text)
    
    def _display_command_help(self, command: str):
        """Display help for a specific command."""
        cmd_info = self.commands[command]
        
        help_text = f"""
Command: {command}
Description: {cmd_info['help']}
Usage: {cmd_info['usage']}
Example: {cmd_info['example']}
        """
        
        if self.console:
            panel = Panel(
                help_text.strip(),
                title=f"Help: {command}",
                border_style="cyan"
            )
            self.console.print(panel)
        else:
            self._print(f"\n📖 HELP: {command.upper()}")
            self._print("-" * 20)
            self._print(f"Description: {cmd_info['help']}")
            self._print(f"Usage: {cmd_info['usage']}")
            self._print(f"Example: {cmd_info['example']}")
    
    def _display_history(self, history: List[Dict[str, Any]]):
        """Display command history."""
        if not history:
            self._print("No command history available")
            return
        
        if self.console:
            table = Table(title="📜 Command History")
            table.add_column("Time", style="dim")
            table.add_column("Command", style="bold")
            table.add_column("Status", justify="center")
            
            for entry in history:
                time_str = entry["timestamp"][:19].replace("T", " ")
                status = "✅" if entry["success"] else "❌"
                full_cmd = f"{entry['command']} {' '.join(entry['args'])}"
                
                table.add_row(time_str, full_cmd, status)
            
            self.console.print(table)
        
        else:
            self._print("\n📜 COMMAND HISTORY")
            self._print("-" * 30)
            for entry in history:
                time_str = entry["timestamp"][:19].replace("T", " ")
                status = "✅" if entry["success"] else "❌"
                full_cmd = f"{entry['command']} {' '.join(entry['args'])}"
                
                self._print(f"{time_str} | {status} | {full_cmd}")
    
    # Additional display methods would be implemented here for:
    # - _display_learning_update()
    # - _display_reflection_report()
    # - _display_knowledge_results()
    # - _display_health_check()
    
    # ================================================
    # UTILITY METHODS
    # ================================================
    
    def _print_welcome(self):
        """Print welcome message."""
        welcome_text = """
🤖 Bob LLM-as-Kernel Intelligence System
========================================

Welcome to the Bob CLI! Type 'help' for available commands.
Type 'init' to initialize all systems, then start with 'think' or 'query'.

Status indicators:
🟢 All systems operational
🟡 Systems initializing
🔴 Systems offline
        """
        
        if self.console:
            self.console.print(welcome_text, style="bold blue")
        else:
            self._print(welcome_text)
    
    def _print(self, message: str):
        """Print message to console."""
        if self.console:
            self.console.print(message)
        else:
            print(message)
    
    def _print_success(self, message: str):
        """Print success message."""
        if self.console:
            self.console.print(message, style="bold green")
        else:
            print(f"✅ {message}")
    
    def _print_error(self, message: str):
        """Print error message."""
        if self.console:
            self.console.print(message, style="bold red")
        else:
            print(f"❌ {message}")
    
    def _print_warning(self, message: str):
        """Print warning message."""
        if self.console:
            self.console.print(message, style="bold yellow")
        else:
            print(f"⚠️ {message}")
    
    def _print_debug(self, message: str):
        """Print debug message."""
        if self.debug:
            if self.console:
                self.console.print(f"[DEBUG] {message}", style="dim")
            else:
                print(f"[DEBUG] {message}")
    
    async def _cleanup(self):
        """Clean up CLI resources."""
        try:
            if self.bob_agent:
                await self.bob_agent.cleanup()
            
            self.session.cleanup()
            
        except Exception as e:
            self._print_error(f"Cleanup error: {e}")


# ================================================
# MAIN CLI ENTRY POINT
# ================================================

async def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bob LLM-as-Kernel Intelligence System CLI"
    )
    parser.add_argument(
        "--data-path",
        default="~/Bob/data",
        help="Path for data storage (default: ~/Bob/data)"
    )
    parser.add_argument(
        "--ollama-url", 
        default="http://localhost:11434",
        help="Ollama service URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--model",
        default="llama3.2", 
        help="Default LLM model (default: llama3.2)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--no-rich",
        action="store_true",
        help="Disable rich formatting"
    )
    
    args = parser.parse_args()
    
    # Create and start CLI
    cli = BobCLI(
        data_path=args.data_path,
        ollama_url=args.ollama_url,
        model=args.model,
        debug=args.debug,
        rich_output=not args.no_rich
    )
    
    await cli.start()


if __name__ == "__main__":
    asyncio.run(main())
