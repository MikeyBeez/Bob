"""
Bob Brain Intelligence System
Enhanced context discovery and smart tool selection for Bob

This provides the 'smarts' that Bob needs to intelligently select tools,
understand context, and provide sophisticated responses like brain_init_v5_working.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class BobBrainIntelligence:
    """
    Intelligent context discovery and tool selection system for Bob.
    
    Provides similar 'smarts' to brain_init_v5_working:
    - Intent analysis from user messages
    - Smart tool selection based on context
    - Protocol detection and activation
    - Intelligent context loading
    """
    
    def __init__(self, brain_tools: Dict[str, Any]):
        self.brain_tools = brain_tools
        self.session_context = {
            "intent_history": [],
            "tool_usage_patterns": {},
            "successful_contexts": [],
            "project_context": None
        }
        
        # Intent patterns for smart analysis
        self.intent_patterns = {
            "testing": {
                "patterns": [r"test", r"check.*tools", r"verify", r"validate", r"run tests"],
                "confidence_boost": 0.9,
                "preferred_tools": ["brain_status", "git_status", "detect_bullshit"],
                "context_hints": ["system health", "validation", "quality assurance"]
            },
            "development": {
                "patterns": [r"code", r"build", r"create", r"develop", r"implement", r"project", r"git.*status", r"git", r"repo", r"repository", r"commit", r"branch", r"check.*git", r"git.*project"],
                "confidence_boost": 1.1,  # Higher boost for development
                "preferred_tools": ["find_project", "filesystem_read", "git_status"],
                "context_hints": ["software development", "coding", "project management", "version control"]
            },
            "analysis": {
                "patterns": [r"analyz", r"analysis", r"examine", r"investigate", r"study", r"bullshit", r"\bbs\b", r"detect.*bs", r"check.*bs"],
                "confidence_boost": 1.2,  # Higher boost for analysis
                "preferred_tools": ["cognitive_process", "detect_bullshit", "analyze_patterns"],
                "context_hints": ["data analysis", "investigation", "research", "bullshit detection"]
            },
            "system": {
                "patterns": [r"brain.*status", r"system.*status", r"health", r"system.*health", r"info", r"information", r"brain.*info"],
                "confidence_boost": 0.9,
                "preferred_tools": ["brain_status", "filesystem_read"],
                "context_hints": ["system administration", "monitoring", "diagnostics"]
            },
            "file_operations": {
                "patterns": [r"read", r"file", r"directory", r"folder", r"content"],
                "confidence_boost": 0.8,
                "preferred_tools": ["filesystem_read", "filesystem_list", "find_project"],
                "context_hints": ["file management", "content access", "navigation"]
            },
            "memory": {
                "patterns": [r"remember", r"recall", r"memory", r"store", r"forget"],
                "confidence_boost": 0.8,
                "preferred_tools": ["brain_recall", "store_memory"],
                "context_hints": ["memory management", "information storage", "recall"]
            },
            "conversation": {
                "patterns": [r"hello", r"hi\b", r"help\b", r"what can you do", r"capabilities"],
                "confidence_boost": 0.5,  # Lower boost for conversation
                "preferred_tools": ["brain_status"],
                "context_hints": ["general conversation", "introduction", "help"]
            }
        }
    
    def analyze_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Analyze user intent from message with confidence scoring.
        
        Returns:
            Dictionary with primary intent, confidence, and suggested tools
        """
        message_lower = user_message.lower()
        intent_scores = {}
        
        for intent_name, intent_data in self.intent_patterns.items():
            score = 0.0
            matched_patterns = []
            
            for pattern in intent_data["patterns"]:
                matches = re.findall(pattern, message_lower)
                if matches:
                    score += len(matches) * 0.2
                    matched_patterns.extend(matches)
            
            if matched_patterns:
                score *= intent_data["confidence_boost"]
                intent_scores[intent_name] = {
                    "score": min(score, 1.0),  # Cap at 1.0
                    "matched_patterns": matched_patterns,
                    "preferred_tools": intent_data["preferred_tools"],
                    "context_hints": intent_data["context_hints"]
                }
        
        # Find primary intent
        if not intent_scores:
            primary_intent = "conversation"
            confidence = 0.3
            suggested_tools = ["brain_status"]
        else:
            primary_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k]["score"])
            confidence = intent_scores[primary_intent]["score"]
            suggested_tools = intent_scores[primary_intent]["preferred_tools"]
        
        return {
            "primary": primary_intent,
            "confidence": confidence,
            "all_scores": intent_scores,
            "suggested_tools": suggested_tools,
            "message_analysis": {
                "length": len(user_message),
                "complexity": self._assess_complexity(user_message),
                "contains_questions": "?" in user_message,
                "contains_commands": any(cmd in message_lower for cmd in ["please", "can you", "help me"])
            }
        }
    
    def _assess_complexity(self, message: str) -> str:
        """Assess message complexity for better tool selection."""
        word_count = len(message.split())
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "moderate"
        else:
            return "complex"
    
    def suggest_tool_sequence(self, intent_analysis: Dict[str, Any], user_message: str) -> List[Dict[str, Any]]:
        """
        Suggest a sequence of tools to execute based on intent analysis.
        
        Returns:
            List of tool suggestions with parameters and reasoning
        """
        primary_intent = intent_analysis["primary"]
        confidence = intent_analysis["confidence"]
        
        tool_sequence = []
        
        # Special handling for testing requests
        if primary_intent == "testing" and any(phrase in user_message.lower() for phrase in ["test your tools", "test tools"]):
            return [{
                "action": "TOOL_TEST_REQUEST",
                "reasoning": "User explicitly requested tool testing"
            }]
        
        # System status requests
        if primary_intent == "system":
            tool_sequence.append({
                "tool_name": "brain_status",
                "parameters": {},
                "reasoning": f"User asking about system status (confidence: {confidence:.2f})",
                "priority": "high"
            })
        
        # Analysis requests
        elif primary_intent == "analysis":
            # Check for bullshit detection specifically
            if any(term in user_message.lower() for term in ["bullshit", "bs", "detect bs", "check bs"]):
                tool_sequence.append({
                    "tool_name": "detect_bullshit",
                    "parameters": {"text": user_message.split(":", 1)[1].strip() if ":" in user_message else user_message},
                    "reasoning": "User specifically requested bullshit detection",
                    "priority": "high"
                })
            else:
                # General analysis request
                if len(user_message.split()) > 10:
                    tool_sequence.append({
                        "tool_name": "detect_bullshit",
                        "parameters": {"text": user_message},
                        "reasoning": "Analyzing message content for patterns",
                        "priority": "medium"
                    })
                
                tool_sequence.append({
                    "tool_name": "cognitive_process",
                    "parameters": {
                        "content": user_message,
                        "mode": "analysis"
                    },
                    "reasoning": "User requested analysis - using cognitive processing",
                    "priority": "high"
                })
        
        # Development context
        elif primary_intent == "development":
            # Handle git-specific requests with high priority
            if any(term in user_message.lower() for term in ["git", "repo", "repository", "commit", "status"]) and "git" in user_message.lower():
                tool_sequence.append({
                    "tool_name": "git_status",
                    "parameters": {"path": "/Users/bard/Bob"},
                    "reasoning": "User requested git/repository status",
                    "priority": "high"
                })
            
            # Look for project names
            if "bob" in user_message.lower():
                tool_sequence.append({
                    "tool_name": "find_project",
                    "parameters": {"name": "Bob"},
                    "reasoning": "User mentioned Bob project",
                    "priority": "high"
                })
            
            # If no git-specific request and no specific project, do general development check
            if not tool_sequence:
                tool_sequence.append({
                    "tool_name": "git_status",
                    "parameters": {"path": "/Users/bard/Bob"},
                    "reasoning": "Development context - checking git status",
                    "priority": "medium"
                })
        
        return tool_sequence
    
    def generate_smart_response_strategy(self, intent_analysis: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """
        Generate a comprehensive response strategy based on intent analysis.
        
        This is the main 'smarts' function that decides how Bob should respond.
        """
        primary_intent = intent_analysis["primary"]
        confidence = intent_analysis["confidence"]
        
        # Get suggested tool sequence
        tool_sequence = self.suggest_tool_sequence(intent_analysis, user_message)
        
        # Determine response style
        response_style = self._determine_response_style(intent_analysis, user_message)
        
        # Generate context hints for better responses
        context_hints = self._generate_context_hints(intent_analysis, user_message)
        
        strategy = {
            "intent": {
                "primary": primary_intent,
                "confidence": confidence,
                "complexity": intent_analysis["message_analysis"]["complexity"]
            },
            "tools": {
                "sequence": tool_sequence,
                "count": len(tool_sequence),
                "execution_strategy": "sequential" if len(tool_sequence) > 1 else "single"
            },
            "response": {
                "style": response_style,
                "should_explain_reasoning": confidence > 0.7,
                "should_show_tool_usage": len(tool_sequence) > 0,
                "tone": "professional" if primary_intent in ["testing", "analysis"] else "conversational"
            },
            "context": {
                "hints": context_hints,
                "requires_memory": primary_intent == "memory",
                "requires_files": primary_intent == "file_operations",
                "requires_system": primary_intent in ["system", "testing"]
            },
            "session_updates": {
                "update_intent_history": True,
                "track_tool_usage": len(tool_sequence) > 0,
                "update_context": confidence > 0.5
            }
        }
        
        return strategy
    
    def _determine_response_style(self, intent_analysis: Dict[str, Any], user_message: str) -> str:
        """Determine the appropriate response style."""
        primary_intent = intent_analysis["primary"]
        confidence = intent_analysis["confidence"]
        
        if primary_intent == "testing":
            return "technical_detailed"
        elif primary_intent == "analysis":
            return "analytical_structured"
        elif primary_intent == "development":
            return "technical_focused"
        elif confidence < 0.5:
            return "helpful_exploratory"
        else:
            return "conversational_informative"
    
    def _generate_context_hints(self, intent_analysis: Dict[str, Any], user_message: str) -> List[str]:
        """Generate context hints to improve response quality."""
        hints = []
        primary_intent = intent_analysis["primary"]
        
        # Add intent-specific context
        if primary_intent in self.intent_patterns:
            hints.extend(self.intent_patterns[primary_intent]["context_hints"])
        
        # Add message-specific hints
        if "?" in user_message:
            hints.append("user asking question")
        
        if any(word in user_message.lower() for word in ["please", "can you", "help"]):
            hints.append("polite request for assistance")
        
        if len(user_message.split()) > 20:
            hints.append("complex detailed request")
        
        return hints
    
    def update_session_context(self, intent_analysis: Dict[str, Any], tools_used: List[str], success: bool):
        """Update session context based on interaction results."""
        # Track intent history
        self.session_context["intent_history"].append({
            "intent": intent_analysis["primary"],
            "confidence": intent_analysis["confidence"],
            "timestamp": "now",
            "success": success
        })
        
        # Track tool usage patterns
        for tool in tools_used:
            if tool not in self.session_context["tool_usage_patterns"]:
                self.session_context["tool_usage_patterns"][tool] = {"count": 0, "success_rate": 0}
            
            self.session_context["tool_usage_patterns"][tool]["count"] += 1
            if success:
                self.session_context["tool_usage_patterns"][tool]["success_rate"] += 0.1
        
        # Keep history manageable
        if len(self.session_context["intent_history"]) > 10:
            self.session_context["intent_history"] = self.session_context["intent_history"][-10:]
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get a summary of the intelligence system's current state."""
        return {
            "system": "Bob Brain Intelligence System",
            "capabilities": {
                "intent_patterns": len(self.intent_patterns),
                "available_tools": len(self.brain_tools),
                "session_interactions": len(self.session_context["intent_history"])
            },
            "session_context": self.session_context,
            "intelligence_features": [
                "Intent analysis with confidence scoring",
                "Smart tool sequence generation", 
                "Context-aware response strategies",
                "Session continuity tracking",
                "Adaptive tool selection"
            ]
        }
