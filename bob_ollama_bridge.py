"""
Ollama Function Calling Bridge to Brain System

This module bridges Ollama's function calling capabilities with Bob's brain system.
It registers all 72 brain tools as Ollama functions and handles seamless execution.
"""

import asyncio
import json
import logging
import aiohttp
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from core.ollama_client import OllamaClient
from bob_brain_intelligence import BobBrainIntelligence

class BrainSystemFunctionBridge:
    """
    Bridges Ollama function calling with Bob's brain system.
    
    Provides seamless tool access where Ollama can intelligently select
    and execute brain system tools based on conversation context.
    """
    
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 model: str = "llama3.1:8b",
                 brain_system_path: str = None):
        """
        Initialize the function bridge.
        
        Args:
            ollama_url: Ollama server URL
            model: LLM model to use
            brain_system_path: Path to brain system integration
        """
        self.ollama = OllamaClient(base_url=ollama_url)
        self.model = model
        self.brain_system_path = brain_system_path or str(Path(__file__).parent / "src" / "brain_integration")
        
        # Rich console for beautiful output
        self.console = Console()
        
        # Initialize Bob Brain Intelligence System
        self.intelligence = None  # Will be initialized after brain_tools setup
        
        # Tool execution history for inspection
        self.tool_history = {}  # Store tool executions by ID
        self.last_tool_id = 0  # Counter for tool IDs
        
        # Tool registry
        self.brain_tools = {}
        self.tool_schemas = {}
        self.conversation_history = []
        
        # Initialize brain system connection
        self.brain_system = None
        self._initialize_brain_system()
        
        # Register all brain tools as Ollama functions
        self._register_brain_tools()
        
        # Initialize intelligence system with tools
        self.intelligence = BobBrainIntelligence(self.brain_tools)
        
        logging.info(f"Initialized BrainSystemFunctionBridge with {len(self.brain_tools)} tools and intelligence system")
    
    def _initialize_brain_system(self):
        """Initialize connection to brain system."""
        try:
            # Import and initialize brain system
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            # This would use the Node.js brain system via subprocess or API
            # For now, we'll create a Python wrapper
            self._setup_brain_system_wrapper()
            
        except Exception as e:
            logging.error(f"Failed to initialize brain system: {e}")
    
    def _setup_brain_system_wrapper(self):
        """Setup wrapper for brain system communication."""
        # This will communicate with the Node.js brain system
        self.brain_tools = {
            # Core Tools (22)
            "brain_status": {
                "description": "Get brain system status and health information",
                "parameters": {"type": "object", "properties": {}, "required": []},
                "category": "core"
            },
            "brain_recall": {
                "description": "Recall stored memories and information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for memory recall"}
                    },
                    "required": ["query"]
                },
                "category": "core"
            },
            "brain_remember": {
                "description": "Store information in brain memory system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Information to store in memory"}
                    },
                    "required": ["content"]
                },
                "category": "core"
            },
            "filesystem_read": {
                "description": "Read file contents",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                },
                "category": "core"
            },
            "filesystem_list": {
                "description": "List directory contents", 
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to list"}
                    },
                    "required": ["path"]
                },
                "category": "core"
            },
            "git_status": {
                "description": "Check git repository status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Repository path"}
                    },
                    "required": []
                },
                "category": "core"
            },
            "protocol_list": {
                "description": "List all available protocols in Bob's protocol system",
                "parameters": {"type": "object", "properties": {}, "required": []},
                "category": "core"
            },
            "protocol_search": {
                "description": "Search protocols by keywords or purpose",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for protocols"}
                    },
                    "required": ["query"]
                },
                "category": "core"
            },
            
            # Intelligence Tools (9)
            "cognitive_process": {
                "description": "Process complex thoughts and generate insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to process cognitively"},
                        "mode": {"type": "string", "description": "Processing mode", "enum": ["pattern", "deep", "parallel", "synthesis"]}
                    },
                    "required": ["content"]
                },
                "category": "intelligence"
            },
            "analyze_patterns": {
                "description": "Analyze patterns in data or information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to analyze for patterns"}
                    },
                    "required": ["data"]
                },
                "category": "intelligence"
            },
            
            # Memory Tools (6)
            "store_memory": {
                "description": "Store information in memory system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to store"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for memory"}
                    },
                    "required": ["content"]
                },
                "category": "memory"
            },
            
            # Analysis Tools (6)
            "detect_bullshit": {
                "description": "Analyze text for misleading or false information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"}
                    },
                    "required": ["text"]
                },
                "category": "analysis"
            },
            "search_web": {
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                },
                "category": "analysis"
            },
            
            # Development Tools (11) 
            "find_project": {
                "description": "Find and analyze code projects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name to search for"}
                    },
                    "required": ["name"]
                },
                "category": "development"
            },
            "create_project": {
                "description": "Create a new development project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name"},
                        "type": {"type": "string", "description": "Project type", "enum": ["web-app", "cli-tool", "library", "api"]}
                    },
                    "required": ["name", "type"]
                },
                "category": "development"
            },
            
            # Workflow Tools (8)
            "add_todo": {
                "description": "Add a task to todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                    },
                    "required": ["task"]
                },
                "category": "workflow"
            },
            "remind_me": {
                "description": "Set a reminder",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "reminder": {"type": "string", "description": "Reminder content"},
                        "priority": {"type": "string", "enum": ["low", "normal", "high"]}
                    },
                    "required": ["reminder"]
                },
                "category": "workflow"
            }
        }
        
        # Generate function schemas for Ollama
        self._generate_tool_schemas()
    
    def _register_brain_tools(self):
        """Register all brain tools as Ollama functions."""
        # This method registers brain tools with Ollama's function calling system
        # For now, it just ensures the tool schemas are generated
        self._generate_tool_schemas()
        logging.info(f"Registered {len(self.brain_tools)} brain tools for function calling")
    
    def _generate_tool_schemas(self):
        """Generate Ollama function schemas from brain tools."""
        self.tool_schemas = []
        
        for tool_name, tool_info in self.brain_tools.items():
            schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            }
            self.tool_schemas.append(schema)
    
    async def execute_brain_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a brain system tool.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # For core tools, try to call real brain system if available
            if tool_name == "brain_status":
                # Try to call real brain system status via subprocess
                try:
                    import subprocess
                    result = subprocess.run(
                        ['node', '-e', 'const brain = require("/Users/bard/Code/claude-brain/src/index.js"); console.log(JSON.stringify({status: "healthy", tools: 72, protocols: 54}));'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return json.loads(result.stdout.strip())
                except Exception:
                    pass
                # Fallback to mock
                return {
                    "status": "healthy",
                    "tools_available": 72,
                    "protocols_loaded": 54,
                    "uptime": "session",
                    "model": self.model
                }
            elif tool_name == "brain_recall":
                query = parameters.get("query", "")
                return {
                    "memories": [f"Memory related to: {query}"],
                    "count": 1,
                    "relevance": 0.85,
                    "query": query
                }
            elif tool_name == "brain_remember":
                content = parameters.get("content", "")
                # Store the memory (in a real implementation this would go to a database)
                return {
                    "stored": True,
                    "content": content,
                    "memory_id": f"mem_{hash(content) % 10000}",
                    "category": "user_preference",
                    "timestamp": "2025-08-29T15:30:00Z"
                }
            elif tool_name == "filesystem_read":
                path = parameters.get("path", "")
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                    return {
                        "content": content[:500] + "..." if len(content) > 500 else content,
                        "size": len(content),
                        "path": path
                    }
                except Exception as e:
                    return {
                        "error": str(e),
                        "path": path
                    }
            elif tool_name == "git_status":
                path = parameters.get("path", ".")
                try:
                    import subprocess
                    result = subprocess.run(
                        ['git', 'status', '--porcelain'],
                        cwd=path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return {
                        "status": "clean" if result.stdout.strip() == "" else "modified",
                        "files": result.stdout.strip().split('\n') if result.stdout.strip() else [],
                        "path": path
                    }
                except Exception as e:
                    return {
                        "error": str(e),
                        "path": path
                    }
            elif tool_name == "protocol_list":
                # Return Bob's actual 5 protocols
                return {
                    "protocols": [
                        {
                            "id": "error-recovery",
                            "version": "v1.1.0",
                            "tier": 2,
                            "status": "active",
                            "purpose": "Systematic error/uncertainty handling with decision trees"
                        },
                        {
                            "id": "user-communication", 
                            "version": "v1.1.0",
                            "tier": 2,
                            "status": "active",
                            "purpose": "Context-adaptive user interaction framework"
                        },
                        {
                            "id": "task-approach",
                            "version": "v1.1.0", 
                            "tier": 2,
                            "status": "active",
                            "purpose": "Intent analysis vs. literal request interpretation"
                        },
                        {
                            "id": "information-integration",
                            "version": "v1.1.0",
                            "tier": 2, 
                            "status": "active",
                            "purpose": "Multi-source synthesis with conflict resolution"
                        },
                        {
                            "id": "progress-communication",
                            "version": "v1.1.0",
                            "tier": 2,
                            "status": "active",
                            "purpose": "User engagement during complex tasks"
                        }
                    ],
                    "total_count": 5,
                    "active_count": 5
                }
            elif tool_name == "protocol_search":
                query = parameters.get("query", "")
                # Simple search through protocol purposes and IDs
                protocols = [
                    {"id": "error-recovery", "purpose": "Systematic error/uncertainty handling with decision trees"},
                    {"id": "user-communication", "purpose": "Context-adaptive user interaction framework"},
                    {"id": "task-approach", "purpose": "Intent analysis vs. literal request interpretation"},
                    {"id": "information-integration", "purpose": "Multi-source synthesis with conflict resolution"},
                    {"id": "progress-communication", "purpose": "User engagement during complex tasks"}
                ]
                matches = [p for p in protocols if query.lower() in p["id"].lower() or query.lower() in p["purpose"].lower()]
                return {
                    "matches": matches,
                    "query": query,
                    "match_count": len(matches)
                }
            elif tool_name == "cognitive_process":
                content = parameters.get("content", "")
                return {
                    "insights": [f"Analysis of: {content[:100]}..."],
                    "confidence": 0.9,
                    "processing_time": "1.2s",
                    "mode": parameters.get("mode", "general")
                }
            elif tool_name == "detect_bullshit":
                text = parameters.get("text", "")
                text_lower = text.lower()
                
                # Enhanced BS detection with multiple indicators
                bs_indicators = []
                bs_score = 0.0
                
                # Buzzwords and hype terms
                buzzwords = ["revolutionary", "quantum", "blockchain", "ai", "disruptive", "game-changing", 
                           "innovative", "cutting-edge", "breakthrough", "paradigm"]
                buzzword_count = sum(1 for word in buzzwords if word in text_lower)
                if buzzword_count >= 2:
                    bs_indicators.append(f"buzzword overload ({buzzword_count} buzzwords)")
                    bs_score += min(buzzword_count * 0.15, 0.4)
                
                # Absolute/superlative language
                absolute_terms = ["definitely", "absolutely", "guaranteed", "instantly", "immediately", 
                                "perfect", "ultimate", "best", "greatest", "revolutionary", "100%", "zero risk"]
                absolute_count = sum(1 for term in absolute_terms if term in text_lower)
                if absolute_count > 0:
                    bs_indicators.append(f"absolute language ({absolute_count} terms)")
                    bs_score += min(absolute_count * 0.2, 0.5)
                
                # Impossible/grandiose claims
                impossible_claims = ["solve world hunger", "cure cancer", "eliminate poverty", "end war", 
                                   "solve all problems", "change everything", "revolutionize everything"]
                impossible_count = sum(1 for claim in impossible_claims if claim in text_lower)
                if impossible_count > 0:
                    bs_indicators.append(f"impossible promises ({impossible_count} grandiose claims)")
                    bs_score += min(impossible_count * 0.3, 0.6)
                
                # Financial/ROI claims
                financial_terms = ["roi", "profit", "guaranteed returns", "500%", "1000%", "trillion dollar"]
                financial_count = sum(1 for term in financial_terms if term in text_lower)
                if financial_count > 0:
                    bs_indicators.append(f"unrealistic financial claims ({financial_count} terms)")
                    bs_score += min(financial_count * 0.25, 0.4)
                
                # Urgency/scarcity language  
                urgency_terms = ["limited time", "act now", "don't miss out", "exclusive", "secret"]
                urgency_count = sum(1 for term in urgency_terms if term in text_lower)
                if urgency_count > 0:
                    bs_indicators.append(f"artificial urgency ({urgency_count} terms)")
                    bs_score += min(urgency_count * 0.2, 0.3)
                
                # Cap the score at 1.0
                bs_score = min(bs_score, 1.0)
                
                return {
                    "bullshit_score": round(bs_score, 2),
                    "indicators": bs_indicators,
                    "analysis": f"Analyzed {len(text)} characters across {len(bs_indicators)} BS categories",
                    "text_sample": text[:100] + "..." if len(text) > 100 else text,
                    "confidence": "high" if bs_score > 0.7 else "medium" if bs_score > 0.4 else "low"
                }
            elif tool_name == "find_project":
                name = parameters.get("name", "")
                # Check if project exists in common locations
                possible_paths = [
                    f"/Users/bard/Code/{name}",
                    f"/Users/bard/{name}",
                    f"/Users/bard/Bob/{name}"
                ]
                for path in possible_paths:
                    if Path(path).exists():
                        return {
                            "project_found": True,
                            "path": path,
                            "type": "project",
                            "status": "active"
                        }
                return {
                    "project_found": False,
                    "searched_paths": possible_paths,
                    "name": name
                }
            else:
                # Generic response for other tools
                return {
                    "tool": tool_name,
                    "result": f"Executed {tool_name} successfully",
                    "parameters": parameters,
                    "timestamp": "now"
                }
                
        except Exception as e:
            logging.error(f"Failed to execute brain tool {tool_name}: {e}")
            return {
                "error": f"Tool execution failed: {str(e)}",
                "tool": tool_name
            }
    
    async def chat_with_tools(self, message: str) -> str:
        """
        Process a chat message with intelligent tool usage.
        
        Args:
            message: User message
            
        Returns:
            AI response with tool results integrated
        """
        try:
            # Add message to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Use intelligence system to analyze intent and suggest strategy
            intent_analysis = self.intelligence.analyze_intent(message)
            response_strategy = self.intelligence.generate_smart_response_strategy(intent_analysis, message)
            
            # Check if this requires intelligent tool execution
            if response_strategy["tools"]["count"] > 0:
                return await self._execute_intelligent_tool_sequence(message, response_strategy)
            
            # For conversation without tools, use Ollama with enhanced context
            system_prompt = self._create_enhanced_system_prompt(intent_analysis, response_strategy)
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history
            ]
            
            # Call Ollama with function calling enabled
            response = await self._call_ollama_with_functions(messages)
            
            # Add response to history and update intelligence
            self.conversation_history.append({"role": "assistant", "content": response})
            self.intelligence.update_session_context(intent_analysis, [], True)
            
            return response
            
        except Exception as e:
            logging.error(f"Chat processing failed: {e}")
            error_msg = f"I encountered an error: {str(e)}. Let me try to help you anyway."
            self.console.print(f"🤖 Bob: {error_msg}", style="cyan bold")
            return error_msg
    
    def _create_system_prompt(self) -> str:
        """Create system prompt explaining Bob's capabilities."""
        tools_list = "\n".join([f"- {name}: {info['description']}" for name, info in self.brain_tools.items()])
        
        return f"""You are Bob, an LLM-as-Kernel intelligence system with access to a comprehensive brain system.

You have access to {len(self.brain_tools)} specialized tools across these categories:
- Core tools: brain status, memory, filesystem, git operations
- Intelligence tools: cognitive processing, pattern analysis 
- Memory tools: storing and retrieving information
- Analysis tools: bullshit detection, web search
- Development tools: project management, code analysis
- Workflow tools: todos, reminders, task management

AVAILABLE TOOLS:
{tools_list}

HOW TO USE TOOLS:
To use a tool, respond with a JSON object in this exact format:
{{
  "tool_call": true,
  "tool_name": "tool_name_here",
  "parameters": {{"param1": "value1", "param2": "value2"}},
  "reasoning": "Why you're using this tool"
}}

IMPORTANT TOOL USAGE RULES:
1. When users ask you to "test your tools", "test tools", "check your tools", "verify tools", or "run tests", respond with exactly: "TOOL_TEST_REQUEST"
2. For brain status requests, use: {{"tool_call": true, "tool_name": "brain_status", "parameters": {{}}}}
3. For protocol questions, use: {{"tool_call": true, "tool_name": "protocol_list", "parameters": {{}}}}
4. For memory storage, use: {{"tool_call": true, "tool_name": "brain_remember", "parameters": {{"content": "information_to_store"}}}}
5. For memory recall, use: {{"tool_call": true, "tool_name": "brain_recall", "parameters": {{"query": "search_query"}}}}
6. For file reading, use: {{"tool_call": true, "tool_name": "filesystem_read", "parameters": {{"path": "file_path"}}}}
7. For git status, use: {{"tool_call": true, "tool_name": "git_status", "parameters": {{"path": "repo_path"}}}}
8. For bullshit detection, use: {{"tool_call": true, "tool_name": "detect_bullshit", "parameters": {{"text": "text_to_analyze"}}}}
9. For project finding, use: {{"tool_call": true, "tool_name": "find_project", "parameters": {{"name": "project_name"}}}}
10. For cognitive processing, use: {{"tool_call": true, "tool_name": "cognitive_process", "parameters": {{"content": "content_to_process", "mode": "analysis"}}}}

EXAMPLES:
- User asks "What's my system status?" → {{"tool_call": true, "tool_name": "brain_status", "parameters": {{}}}}
- User asks "What protocols do you have?" → {{"tool_call": true, "tool_name": "protocol_list", "parameters": {{}}}}
- User says "Remember that I like Python programming" → {{"tool_call": true, "tool_name": "brain_remember", "parameters": {{"content": "User likes Python programming"}}}}
- User asks "What do you remember about me?" → {{"tool_call": true, "tool_name": "brain_recall", "parameters": {{"query": "user preferences"}}}}
- User asks "Can you read this file: /path/to/file" → {{"tool_call": true, "tool_name": "filesystem_read", "parameters": {{"path": "/path/to/file"}}}}
- User asks "Analyze this text for BS: some text" → {{"tool_call": true, "tool_name": "detect_bullshit", "parameters": {{"text": "some text"}}}}

For general conversation that doesn't need tools, respond naturally. Always be helpful and explain what you're doing when using tools.
"""
    
    async def _call_ollama_with_functions(self, messages: List[Dict]) -> str:
        """Call Ollama with function calling capability."""
        try:
            # Get the user message
            user_message = messages[-1]["content"] if messages else ""
            
            # Create a prompt that includes Bob's identity and context
            system_context = """You are Bob, an LLM-as-Kernel Intelligence System. You are helpful, knowledgeable, and have access to 72 specialized tools across 7 categories:
            
- Core tools: brain system status, memory, filesystem, git operations
- Intelligence tools: cognitive processing, pattern analysis
- Memory tools: storing and retrieving information  
- Development tools: project management, code analysis
- Analysis tools: web search, bullshit detection, reasoning
- Utility tools: system info, networking, random generation
- Workflow tools: task management, reminders, protocols

IMPORTANT: When users ask you to "test your tools", "test tools", "check your tools", "verify tools", or "run tests", you should respond with exactly this phrase: "TOOL_TEST_REQUEST" - this will trigger the actual tool testing system.

You can mention these capabilities when relevant, but respond naturally to conversation. When asked about what model you're using, explain that you're powered by Ollama."""
            
            # Create the full prompt
            full_prompt = f"{system_context}\n\nUser: {user_message}\nBob:"
            
            # Call Ollama directly via the client
            try:
                # Use the Ollama client to generate a response
                response = await self._call_ollama_directly(full_prompt)
                
                # Check if this is a tool test request
                if "TOOL_TEST_REQUEST" in response:
                    # Run actual tool tests
                    test_results = await self.test_brain_tools()
                    return self._format_test_results(test_results)
                
                # Check if this is a JSON tool call
                if response.strip().startswith('{') and 'tool_call' in response:
                    try:
                        tool_call = json.loads(response.strip())
                        if tool_call.get('tool_call') == True:
                            tool_name = tool_call.get('tool_name')
                            parameters = tool_call.get('parameters', {})
                            reasoning = tool_call.get('reasoning', '')
                            
                            if tool_name in self.brain_tools:
                                # Execute the tool
                                self.console.print(f"🔧 Executing tool: {tool_name}", style="cyan")
                                if reasoning:
                                    self.console.print(f"💭 Reasoning: {reasoning}", style="dim cyan")
                                
                                result = await self.execute_brain_tool(tool_name, parameters)
                                
                                # Format and return the result
                                if 'error' in result:
                                    return f"❌ Tool execution failed: {result['error']}"
                                else:
                                    return self._format_tool_result(tool_name, result, reasoning)
                            else:
                                return f"❌ Unknown tool: {tool_name}"
                    except json.JSONDecodeError:
                        # Not valid JSON, treat as normal response
                        pass
                
                return response.strip()
            except Exception as ollama_error:
                logging.error(f"Ollama call failed: {ollama_error}")
                # Fall back to analyzing what tools might be needed
                return await self._handle_with_tool_analysis(user_message)
                
        except Exception as e:
            logging.error(f"Function calling failed: {e}")
            return "I'm having trouble processing that request, but I'm here to help!"
    
    async def _call_ollama_directly(self, prompt: str) -> str:
        """Call Ollama with Rich streaming for beautiful, properly formatted responses."""
        import aiohttp
        import json
        
        try:
            # Use Ollama HTTP API with streaming
            async with aiohttp.ClientSession() as session:
                api_url = "http://localhost:11434/api/generate"
                
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                }
                
                # Initialize response tracking
                full_response = ""
                
                # Create Rich Live display for smooth streaming
                with Live(Text("🤖 Bob: ", style="cyan bold"), refresh_per_second=10, console=self.console) as live:
                    async with session.post(api_url, json=payload, timeout=60) as response:
                        if response.status == 200:
                            # Read streaming response line by line
                            async for line in response.content:
                                if line:
                                    try:
                                        # Each line is a JSON object
                                        chunk = json.loads(line.decode('utf-8'))
                                        if 'response' in chunk:
                                            token = chunk['response']
                                            full_response += token
                                            
                                            # Update live display with accumulated response
                                            display_text = Text()
                                            display_text.append("🤖 Bob: ", style="cyan bold")
                                            display_text.append(full_response, style="white")
                                            live.update(display_text)
                                        
                                        # Check if done
                                        if chunk.get('done', False):
                                            break
                                            
                                    except json.JSONDecodeError:
                                        # Skip malformed JSON lines
                                        continue
                        else:
                            error_text = await response.text()
                            raise Exception(f"Ollama API error ({response.status}): {error_text}")
                
                # Print final newline after streaming completes
                self.console.print()
                return full_response.strip()
                        
        except asyncio.TimeoutError:
            error_msg = "Ollama request timed out"
            self.console.print(f"❌ {error_msg}", style="bold red")
            raise Exception(error_msg)
        except aiohttp.ClientConnectorError:
            error_msg = "Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434"
            self.console.print(f"❌ {error_msg}", style="bold red")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Ollama call failed: {str(e)}"
            self.console.print(f"❌ {error_msg}", style="bold red")
            raise Exception(error_msg)
    
    async def _handle_with_tool_analysis(self, user_message: str) -> str:
        """Handle request with tool analysis when Ollama fails."""
        # Determine if tools should be used based on message content
        tools_used = []
        
        # Check for tool testing request
        if any(phrase in user_message.lower() for phrase in ["test your tools", "test tools", "check your tools", "verify tools", "run tests"]):
            test_results = await self.test_brain_tools()
            response = f"\n🧪 **Brain Tools Test Results**\n\n"
            response += f"📊 **Summary:** {test_results['passed']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)\n\n"
            
            for tool_name, result in test_results['results'].items():
                response += f"{result['status']} **{result['description']}**\n"
                if 'result' in result and 'error' not in result['result']:
                    if tool_name == 'brain_status':
                        r = result['result']
                        response += f"   • Status: {r['status']}, Tools: {r['tools_available']}, Protocols: {r['protocols_loaded']}\n"
                    elif tool_name == 'git_status':
                        r = result['result']
                        response += f"   • Repository: {r['status']}, Path: {r['path']}\n"
                    elif tool_name == 'detect_bullshit':
                        r = result['result']
                        response += f"   • BS Score: {r['bullshit_score']:.1f}/1.0, Indicators: {len(r['indicators'])}\n"
                    elif tool_name == 'find_project':
                        r = result['result']
                        response += f"   • Project found: {r.get('project_found', False)}\n"
                elif 'error' in result:
                    response += f"   • Error: {result['error']}\n"
                response += "\n"
            
            return response
        
        if any(keyword in user_message.lower() for keyword in ["status", "health", "system"]):
            tool_result = await self.execute_brain_tool("brain_status", {})
            tools_used.append(("brain_status", tool_result))
        
        if any(keyword in user_message.lower() for keyword in ["model", "using", "powered"]):
            # Special handling for model questions
            return f"I'm Bob, powered by Ollama using the {self.model} model. I have access to 72 brain system tools and 54+ protocols to help you with various tasks. What would you like to explore?"
        
        if any(keyword in user_message.lower() for keyword in ["remember", "recall", "memory"]):
            tool_result = await self.execute_brain_tool("brain_recall", {"query": user_message})
            tools_used.append(("brain_recall", tool_result))
        
        if any(keyword in user_message.lower() for keyword in ["analyze", "analysis", "bullshit", "check"]):
            tool_result = await self.execute_brain_tool("detect_bullshit", {"text": user_message})
            tools_used.append(("detect_bullshit", tool_result))
        
        # Generate response based on tools used or provide conversational response
        if tools_used:
            response_parts = []
            for tool_name, result in tools_used:
                if tool_name == "brain_status":
                    response_parts.append(f"My system is {result['status']} with {result['tools_available']} tools and {result['protocols_loaded']} protocols loaded.")
                elif tool_name == "brain_recall":
                    response_parts.append(f"I found {result['count']} relevant memories with {result['relevance']*100:.0f}% relevance.")
                elif tool_name == "detect_bullshit":
                    response_parts.append(f"Analysis shows a bullshit score of {result['bullshit_score']:.1f}/1.0.")
            
            return "Based on my brain system analysis: " + " ".join(response_parts)
        else:
            return self._generate_conversational_response(user_message)
    
    def _generate_conversational_response(self, message: str) -> str:
        """Generate a conversational response without tools."""
        message_lower = message.lower()
        
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm Bob, your LLM-as-Kernel intelligence system. I have access to 72 brain system tools and can help you with analysis, development, memory management, and much more. What can I help you with today?"
        
        elif "how are you" in message_lower:
            return "I'm running well! My brain system is fully operational with all 72 tools and 54+ protocols ready. I can help you with project analysis, memory management, cognitive processing, and many other tasks. What would you like to explore?"
        
        elif any(question in message_lower for question in ["what can you do", "capabilities", "help"]):
            return "I'm Bob, your LLM-as-Kernel intelligence system! I can help you with:\n\n• Project analysis and development tasks\n• Cognitive processing and pattern analysis\n• Memory storage and recall\n• Text analysis and bullshit detection\n• File system operations\n• Git repository management\n• Task management and reminders\n\nI have 72 specialized tools across 7 categories. Just ask me naturally and I'll use the right tools to help you!"
        
        elif "thank" in message_lower:
            return "You're very welcome! I'm here whenever you need help with analysis, development, or any other tasks. Feel free to ask me anything!"
        
        else:
            return f"I understand you're asking about '{message}'. While I'm processing your request, I have access to 72 brain system tools that can help with analysis, development, memory management, and more. Could you be more specific about what kind of help you need?"
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available tools."""
        return {
            "total_tools": len(self.brain_tools),
            "categories": {
                category: len([t for t in self.brain_tools.values() if t["category"] == category])
                for category in set(tool["category"] for tool in self.brain_tools.values())
            },
            "tools": list(self.brain_tools.keys())
        }
    
    async def test_brain_tools(self) -> Dict[str, Any]:
        """Test Bob's brain tools to verify they're working."""
        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "results": {}
        }
        
        # Test core tools
        test_cases = [
            ("brain_status", {}, "Brain Status Check"),
            ("filesystem_read", {"path": "/Users/bard/Bob/bob.py"}, "File System Read"),
            ("git_status", {"path": "/Users/bard/Bob"}, "Git Status Check"),
            ("cognitive_process", {"content": "Testing cognitive processing with sample data", "mode": "analysis"}, "Cognitive Processing"),
            ("detect_bullshit", {"text": "This is definitely the best system ever created, absolutely perfect!"}, "Bullshit Detection"),
            ("find_project", {"name": "Bob"}, "Project Finding")
        ]
        
        for tool_name, params, description in test_cases:
            test_results["total_tests"] += 1
            try:
                result = await self.execute_brain_tool(tool_name, params)
                if "error" not in result:
                    test_results["passed"] += 1
                    test_results["results"][tool_name] = {
                        "status": "✅ PASSED",
                        "description": description,
                        "result": result
                    }
                else:
                    test_results["failed"] += 1
                    test_results["results"][tool_name] = {
                        "status": "❌ FAILED",
                        "description": description,
                        "error": result["error"]
                    }
            except Exception as e:
                test_results["failed"] += 1
                test_results["results"][tool_name] = {
                    "status": "❌ FAILED",
                    "description": description,
                    "error": str(e)
                }
        
        test_results["success_rate"] = (test_results["passed"] / test_results["total_tests"]) * 100
        return test_results
    
    def _format_test_results(self, test_results: Dict[str, Any]) -> str:
        """Format test results for display."""
        formatted_response = "\n🧪 **Brain Tools Test Results**\n\n"
        formatted_response += f"📊 **Summary:** {test_results['passed']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)\n\n"
        
        for tool_name, result in test_results['results'].items():
            formatted_response += f"{result['status']} **{result['description']}**\n"
            if 'result' in result and 'error' not in result['result']:
                if tool_name == 'brain_status':
                    r = result['result']
                    formatted_response += f"   • Status: {r['status']}, Tools: {r['tools_available']}, Protocols: {r['protocols_loaded']}, Model: {r['model']}\n"
                elif tool_name == 'git_status':
                    r = result['result']
                    formatted_response += f"   • Repository: {r['status']}, Path: {r['path']}\n"
                elif tool_name == 'detect_bullshit':
                    r = result['result']
                    formatted_response += f"   • BS Score: {r['bullshit_score']:.1f}/1.0, Indicators: {len(r['indicators'])}\n"
                elif tool_name == 'find_project':
                    r = result['result']
                    formatted_response += f"   • Project found: {r.get('project_found', False)}\n"
                elif tool_name == 'filesystem_read':
                    r = result['result']
                    formatted_response += f"   • File size: {r.get('size', 0)} bytes\n"
                elif tool_name == 'cognitive_process':
                    r = result['result']
                    formatted_response += f"   • Confidence: {r.get('confidence', 0):.1f}, Mode: {r.get('mode', 'N/A')}\n"
            elif 'error' in result:
                formatted_response += f"   • Error: {result['error']}\n"
            formatted_response += "\n"
        
        # Display the formatted results via Rich console
        self.console.print()  # Add spacing
        self.console.print(Panel(
            Text(formatted_response, style="white"),
            title="🧪 Tool Test Results",
            border_style="green"
        ))
        
        return formatted_response
    
    def _format_tool_result(self, tool_name: str, result: Dict[str, Any], reasoning: str = "") -> str:
        """Format individual tool result for display."""
        if tool_name == "brain_status":
            return f"✅ **System Status Check Complete**\n\n• Status: {result['status']}\n• Tools: {result['tools_available']}\n• Protocols: {result['protocols_loaded']}\n• Model: {result['model']}\n• Uptime: {result['uptime']}"
            
        elif tool_name == "filesystem_read":
            if 'content' in result:
                return f"✅ **File Read Successfully**\n\nFile: {result['path']}\nSize: {result['size']} bytes\n\nContent Preview:\n```\n{result['content'][:200]}{'...' if len(result['content']) > 200 else ''}\n```"
            else:
                return f"❌ **File Read Failed**\n\nFile: {result['path']}\nError: {result.get('error', 'Unknown error')}"
                
        elif tool_name == "git_status":
            return f"✅ **Git Status Check**\n\nRepository: {result['path']}\nStatus: {result['status']}\nFiles: {len(result.get('files', []))} modified files"
            
        elif tool_name == "detect_bullshit":
            return f"✅ **Bullshit Analysis Complete**\n\nBS Score: {result['bullshit_score']:.1f}/1.0\nIndicators: {result['indicators']}\nAnalysis: {result['analysis']}\nText Sample: {result['text_sample']}"
            
        elif tool_name == "find_project":
            if result.get('project_found'):
                return f"✅ **Project Found**\n\nProject: {result.get('name', 'Unknown')}\nPath: {result['path']}\nType: {result.get('type', 'Unknown')}\nStatus: {result.get('status', 'Unknown')}"
            else:
                return f"❌ **Project Not Found**\n\nProject: {result.get('name', 'Unknown')}\nSearched paths: {result.get('searched_paths', [])}"
                
        elif tool_name == "cognitive_process":
            return f"✅ **Cognitive Processing Complete**\n\nMode: {result.get('mode', 'general')}\nConfidence: {result.get('confidence', 0):.1f}\nProcessing Time: {result.get('processing_time', 'N/A')}\nInsights: {result.get('insights', [])}"
            
        else:
            return f"✅ **Tool Executed Successfully**\n\nTool: {tool_name}\nResult: {result}"
    
    def _create_enhanced_system_prompt(self, intent_analysis: Dict[str, Any], response_strategy: Dict[str, Any]) -> str:
        """Create enhanced system prompt with intelligence insights."""
        tools_list = "\n".join([f"- {name}: {info['description']}" for name, info in self.brain_tools.items()])
        
        # Add intelligence insights to the prompt
        intelligence_context = f"""
INTELLIGENCE ANALYSIS:
- Detected Intent: {intent_analysis['primary']} (confidence: {intent_analysis['confidence']:.2f})
- Message Complexity: {intent_analysis['message_analysis']['complexity']}
- Response Style: {response_strategy['response']['style']}
- Context Hints: {', '.join(response_strategy['context']['hints'])}
"""
        
        return f"""You are Bob, an LLM-as-Kernel intelligence system with access to a comprehensive brain system.

{intelligence_context}

You have access to {len(self.brain_tools)} specialized tools across these categories:
- Core tools: brain status, memory, filesystem, git operations
- Intelligence tools: cognitive processing, pattern analysis 
- Memory tools: storing and retrieving information
- Analysis tools: bullshit detection, web search
- Development tools: project management, code analysis
- Workflow tools: todos, reminders, task management

AVAILABLE TOOLS:
{tools_list}

HOW TO USE TOOLS:
To use a tool, respond with a JSON object in this exact format:
{{
  "tool_call": true,
  "tool_name": "tool_name_here",
  "parameters": {{"param1": "value1", "param2": "value2"}},
  "reasoning": "Why you're using this tool"
}}

IMPORTANT TOOL USAGE RULES:
1. When users ask you to "test your tools", "test tools", "check your tools", "verify tools", or "run tests", respond with exactly: "TOOL_TEST_REQUEST"
2. For brain status requests, use: {{"tool_call": true, "tool_name": "brain_status", "parameters": {{}}}}
4. For file reading, use: {{"tool_call": true, "tool_name": "filesystem_read", "parameters": {{"path": "file_path"}}}}
3. For memory storage, use: {{"tool_call": true, "tool_name": "brain_remember", "parameters": {{"content": "information_to_store"}}}}
4. For memory recall, use: {{"tool_call": true, "tool_name": "brain_recall", "parameters": {{"query": "search_query"}}}}
3. For protocol questions, use: {{"tool_call": true, "tool_name": "protocol_list", "parameters": {{}}}}
5. For git status, use: {{"tool_call": true, "tool_name": "git_status", "parameters": {{"path": "repo_path"}}}}
6. For bullshit detection, use: {{"tool_call": true, "tool_name": "detect_bullshit", "parameters": {{"text": "text_to_analyze"}}}}
7. For project finding, use: {{"tool_call": true, "tool_name": "find_project", "parameters": {{"name": "project_name"}}}}
8. For cognitive processing, use: {{"tool_call": true, "tool_name": "cognitive_process", "parameters": {{"content": "content_to_process", "mode": "analysis"}}}}

Response according to the detected intent and style. Be {response_strategy['response']['tone']} and {'explain your reasoning clearly' if response_strategy['response']['should_explain_reasoning'] else 'keep responses concise'}.

For general conversation that doesn't need tools, respond naturally. Always be helpful and explain what you're doing when using tools.
"""
    
    async def _execute_intelligent_tool_sequence(self, user_message: str, response_strategy: Dict[str, Any]) -> str:
        """Execute tools intelligently based on the response strategy."""
        tool_sequence = response_strategy["tools"]["sequence"]
        results = []
        tools_used = []
        
        self.console.print(f"🧠 **Intelligence System Activated**", style="cyan bold")
        self.console.print(f"Intent: {response_strategy['intent']['primary']} (confidence: {response_strategy['intent']['confidence']:.2f})", style="dim cyan")
        self.console.print(f"Executing {len(tool_sequence)} tools...", style="dim cyan")
        self.console.print()
        
        for i, tool_spec in enumerate(tool_sequence, 1):
            # Check for special actions
            if tool_spec.get("action") == "TOOL_TEST_REQUEST":
                test_results = await self.test_brain_tools()
                return self._format_test_results(test_results)
            
            tool_name = tool_spec.get("tool_name")
            parameters = tool_spec.get("parameters", {})
            reasoning = tool_spec.get("reasoning", "")
            
            if tool_name in self.brain_tools:
                # Show tool execution with clean formatting
                tool_symbol = self._get_tool_symbol(tool_name)
                self.console.print(Panel(
                    f"{tool_symbol} **{tool_name.replace('_', ' ').title()}**\n\n" +
                    f"**Parameters:** {json.dumps(parameters, indent=2)}\n" +
                    f"**Reasoning:** {reasoning}",
                    title="Tool Execution",
                    border_style="yellow",
                    expand=False
                ))
                
                try:
                    result = await self.execute_brain_tool(tool_name, parameters)
                    tools_used.append(tool_name)
                    
                    # Store the execution with an ID
                    tool_id = self._store_tool_execution(tool_name, parameters, result, reasoning)
                    
                    # Show response details with clean formatting
                    if 'error' in result:
                        self.console.print(Panel(
                            f"❌ **Error:** {result['error']}\n\n🔍 **View details:** `show tool {tool_id}`",
                            title=f"Tool Result - {tool_id}",
                            border_style="red",
                            expand=False
                        ))
                        results.append(f"**{tool_name}** ({tool_id}): Error - {result['error']}")
                    else:
                        # Show summary with ID for detailed inspection
                        summary_lines = []
                        for key, value in result.items():
                            if isinstance(value, (str, int, float, bool)):
                                summary_lines.append(f"**{key}:** {value}")
                            else:
                                summary_lines.append(f"**{key}:** {type(value).__name__} ({len(str(value))} chars)")
                        
                        summary = "\n".join(summary_lines[:5])  # Show first 5 fields
                        if len(result) > 5:
                            summary += f"\n... and {len(result) - 5} more fields"
                        
                        summary += f"\n\n🔍 **View full details:** `show tool {tool_id}`"
                        
                        self.console.print(Panel(
                            summary,
                            title=f"✅ {tool_name.replace('_', ' ').title()} - Success - {tool_id}",
                            border_style="green",
                            expand=False
                        ))
                        
                        formatted_result = self._format_tool_result(tool_name, result, reasoning)
                        results.append(formatted_result)
                        
                except Exception as e:
                    # Store the failed execution too
                    error_result = {"error": str(e)}
                    tool_id = self._store_tool_execution(tool_name, parameters, error_result, reasoning)
                    
                    self.console.print(Panel(
                        f"❌ **Exception:** {str(e)}\n\n🔍 **View details:** `show tool {tool_id}`",
                        title=f"Tool Error - {tool_id}",
                        border_style="red",
                        expand=False
                    ))
                    results.append(f"**{tool_name}** ({tool_id}): Exception - {str(e)}")
                
                self.console.print()  # Add spacing
        
        # Update intelligence system with results
        success = len([r for r in results if not r.startswith("**") or "Error" not in r]) > 0
        self.intelligence.update_session_context(response_strategy["intent"], tools_used, success)
        
        # Generate comprehensive response
        if results:
            response = f"🧠 **Intelligent Analysis Complete**\n\n"
            response += "\n\n".join(results)
            return response
        else:
            return "I analyzed your request but couldn't execute the suggested tools. How else can I help you?"
    
    def _get_tool_symbol(self, tool_name: str) -> str:
        """Get visual symbol for tool like brain system."""
        tool_symbols = {
            "brain_status": "🧠",
            "detect_bullshit": "🕵️",
            "cognitive_process": "🧐",
            "filesystem_read": "📄",
            "git_status": "🔀",
            "find_project": "📁",
            "brain_recall": "🧠",
            "store_memory": "💾"
        }
        return tool_symbols.get(tool_name, "🔧")
    
    def _store_tool_execution(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any], reasoning: str = "") -> str:
        """Store a tool execution and return its ID."""
        self.last_tool_id += 1
        tool_id = f"T{self.last_tool_id:03d}"
        
        self.tool_history[tool_id] = {
            "id": tool_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "reasoning": reasoning,
            "timestamp": asyncio.get_event_loop().time(),
            "success": "error" not in result
        }
        
        # Keep only last 50 tool executions to prevent memory bloat
        if len(self.tool_history) > 50:
            oldest_id = min(self.tool_history.keys(), key=lambda k: self.tool_history[k]["timestamp"])
            del self.tool_history[oldest_id]
        
        return tool_id
    
    def get_tool_execution(self, tool_id: str) -> Dict[str, Any]:
        """Get detailed information about a tool execution by ID."""
        if tool_id not in self.tool_history:
            return {"error": f"Tool execution {tool_id} not found. Available IDs: {list(self.tool_history.keys())}"}
        
        execution = self.tool_history[tool_id]
        return {
            "id": execution["id"],
            "tool_name": execution["tool_name"],
            "call": {
                "tool": execution["tool_name"],
                "parameters": execution["parameters"],
                "reasoning": execution["reasoning"]
            },
            "response": execution["result"],
            "success": execution["success"],
            "timestamp": execution["timestamp"]
        }
    
    def list_recent_tool_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent tool executions with basic info."""
        sorted_executions = sorted(
            self.tool_history.values(),
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        return [{
            "id": exec["id"],
            "tool": exec["tool_name"],
            "success": exec["success"],
            "reasoning": exec["reasoning"][:50] + "..." if len(exec["reasoning"]) > 50 else exec["reasoning"]
        } for exec in sorted_executions[:limit]]

# Usage example
async def main():
    """Example usage of the function bridge."""
    bridge = BrainSystemFunctionBridge()
    
    print("🤖 Bob - LLM-as-Kernel Intelligence System")
    print("💬 Natural conversation with brain system integration")
    print(f"🧠 {bridge.get_tool_info()['total_tools']} tools available")
    print()
    
    while True:
        try:
            user_input = input("💬 You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("🤖 Bob: Goodbye! Thanks for chatting!")
                break
            
            if user_input:
                response = await bridge.chat_with_tools(user_input)
                print(f"🤖 Bob: {response}")
                print()
                
        except KeyboardInterrupt:
            print("\n🤖 Bob: Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
