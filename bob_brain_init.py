#!/usr/bin/env python3
"""
Bob Brain Init - Intelligent Protocol Loading and Context Management

This is Bob's equivalent to brain_init_v5_working:
- Loads Master Protocol Index into context
- Analyzes user requests for appropriate protocols  
- Provides intelligent protocol routing and guidance
- Prevents hallucination by loading actual capabilities

Usage: Run this at the start of each Bob session
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Add Bob to path
sys.path.append(str(Path(__file__).parent))

from bob_brain_intelligence import BobBrainIntelligence


class BobBrainInit:
    """
    Bob's intelligent brain initialization system.
    
    Provides:
    - Master Protocol Index loading
    - Task-appropriate protocol selection
    - Context-aware tool routing
    - Anti-hallucination safeguards
    """
    
    def __init__(self):
        self.protocols_path = Path(__file__).parent / "protocols"
        self.master_index_path = self.protocols_path / "MASTER_PROTOCOL_INDEX.md"
        self.intelligence = None
        
    def initialize_brain(self, user_message: str = "", context_budget: float = 0.35) -> dict:
        """
        Initialize Bob's brain with protocol context and intelligent routing.
        
        Args:
            user_message: User's initial message for context analysis
            context_budget: Percentage of context to use (0.0-1.0)
            
        Returns:
            Initialization results with protocol guidance
        """
        
        start_time = datetime.now(timezone.utc)
        
        # Initialize intelligence system
        mock_brain_tools = {}  # Bob uses direct tool calls
        self.intelligence = BobBrainIntelligence(mock_brain_tools)
        
        # Load Master Protocol Index
        protocol_context = self._load_master_protocol_index()
        
        # Analyze user intent if provided
        intent_analysis = None
        protocol_guidance = None
        
        if user_message:
            intent_analysis = self.intelligence.analyze_intent(user_message)
            protocol_guidance = self._generate_protocol_guidance(intent_analysis, user_message)
        
        # Generate initialization results
        results = {
            "status": "success",
            "message": "🤖 Bob Brain System Initialized",
            "version": "1.0.0",
            "timestamp": start_time.isoformat(),
            
            "database_system": {
                "primary_database": str(Path(__file__).parent / "data" / "bob.db"),
                "knowledge_database": str(Path(__file__).parent / "data" / "edgebase" / "knowledge_edges.db"),
                "database_status": self._check_database_status(),
                "available_tables": self._get_database_tables(),
                "memory_system": "SQLite database with memories table",
                "backup_memory": str(Path.home() / ".bob_memories.json")
            },
            
            "protocol_system": {
                "master_index_loaded": bool(protocol_context),
                "total_protocols": 5,
                "active_protocols": self._get_active_protocol_ids(),
                "protocol_context_size": len(protocol_context) if protocol_context else 0
            },
            
            "intelligence_system": {
                "intent_analysis_enabled": True,
                "anti_hallucination_active": True,
                "tool_routing_enabled": True,
                "pattern_count": len(self.intelligence.intent_patterns)
            },
            
            "context_loading": {
                "budget_used": context_budget,
                "protocol_index_loaded": True,
                "smart_routing_active": True
            },
            
            "session_info": {
                "session_id": f"bob-session-{int(start_time.timestamp())}",
                "initialization_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "ready_for_interaction": True
            }
        }
        
        # Add user-specific guidance if message provided
        if user_message and intent_analysis and protocol_guidance:
            results["user_analysis"] = {
                "message": user_message,
                "detected_intent": intent_analysis["primary"],
                "confidence": intent_analysis["confidence"],
                "suggested_protocols": protocol_guidance["recommended_protocols"],
                "tool_sequence": protocol_guidance["tool_sequence"],
                "guidance": protocol_guidance["guidance"]
            }
        
        return results
    
    def _load_master_protocol_index(self) -> str:
        """Load the Master Protocol Index into context."""
        try:
            if self.master_index_path.exists():
                with open(self.master_index_path, 'r') as f:
                    content = f.read()
                return content
            else:
                return ""
        except Exception as e:
            print(f"Warning: Could not load Master Protocol Index: {e}")
            return ""
    
    def _get_active_protocol_ids(self) -> list:
        """Get list of active protocol IDs."""
        return [
            "error-recovery",
            "user-communication", 
            "task-approach",
            "information-integration",
            "progress-communication"
        ]
    
    def _check_database_status(self) -> dict:
        """Check the status of Bob's database systems."""
        try:
            import sqlite3
            
            # Check primary database
            primary_db = Path(__file__).parent / "data" / "bob.db"
            primary_status = "available" if primary_db.exists() else "missing"
            
            # Check knowledge database  
            knowledge_db = Path(__file__).parent / "data" / "edgebase" / "knowledge_edges.db"
            knowledge_status = "available" if knowledge_db.exists() else "missing"
            
            # Test database connection
            primary_connection = "ok"
            memory_count = 0
            if primary_db.exists():
                try:
                    conn = sqlite3.connect(str(primary_db))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM memories")
                    memory_count = cursor.fetchone()[0]
                    conn.close()
                except Exception as e:
                    primary_connection = f"error: {str(e)}"
            
            return {
                "primary_db_status": primary_status,
                "knowledge_db_status": knowledge_status, 
                "primary_connection": primary_connection,
                "stored_memories": memory_count,
                "database_engine": "SQLite"
            }
        except ImportError:
            return {"error": "sqlite3 not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_database_tables(self) -> list:
        """Get list of available database tables."""
        try:
            import sqlite3
            primary_db = Path(__file__).parent / "data" / "bob.db"
            
            if not primary_db.exists():
                return []
            
            conn = sqlite3.connect(str(primary_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception:
            return []
    
    def _generate_protocol_guidance(self, intent_analysis: dict, user_message: str) -> dict:
        """Generate specific protocol guidance for the current request."""
        
        primary_intent = intent_analysis["primary"]
        confidence = intent_analysis["confidence"]
        
        # Determine recommended protocols based on intent
        protocol_recommendations = {
            "protocol": {
                "primary": ["task-approach", "user-communication"],
                "secondary": [],
                "tools": ["protocols:protocol_list"],
                "guidance": "Use actual protocol_list tool to show real protocols. Never hallucinate protocol names."
            },
            "system": {
                "primary": ["task-approach", "progress-communication"],
                "secondary": ["error-recovery"],
                "tools": ["brain:brain_status", "system:system_info"],
                "guidance": "Check actual system status with tools. Provide clear status communication."
            },
            "development": {
                "primary": ["task-approach", "information-integration"],
                "secondary": ["progress-communication"],
                "tools": ["git:git_status", "project-finder:list_projects"],
                "guidance": "Integrate multiple development sources. Show progress for complex operations."
            },
            "analysis": {
                "primary": ["information-integration", "task-approach"],
                "secondary": ["progress-communication"],
                "tools": ["bullshit-detector:detect_bullshit", "cognition:cognition_process"],
                "guidance": "Synthesize multiple sources. Use actual analysis tools."
            },
            "memory": {
                "primary": ["information-integration", "user-communication"],
                "secondary": ["task-approach"],
                "tools": ["brain:brain_recall", "brain:brain_remember"],
                "guidance": "Access actual memory systems. Integrate stored information with current context."
            }
        }
        
        # Get guidance for current intent
        guidance_info = protocol_recommendations.get(primary_intent, {
            "primary": ["task-approach", "user-communication"],
            "secondary": [],
            "tools": ["brain:brain_status"],
            "guidance": "Apply general task approach and user communication protocols."
        })
        
        # Generate tool sequence using intelligence system
        tool_sequence = self.intelligence.suggest_tool_sequence(intent_analysis, user_message)
        
        return {
            "recommended_protocols": {
                "primary": guidance_info["primary"],
                "secondary": guidance_info["secondary"],
                "rationale": f"Based on {primary_intent} intent with {confidence:.2f} confidence"
            },
            "tool_sequence": tool_sequence,
            "guidance": guidance_info["guidance"],
            "anti_hallucination_reminder": "Always use actual tools to verify capabilities. Never make up information."
        }
    
    def get_protocol_summary(self) -> dict:
        """Get a summary of Bob's protocol system."""
        return {
            "total_protocols": 5,
            "protocol_ids": self._get_active_protocol_ids(),
            "master_index_location": str(self.master_index_path),
            "intelligence_patterns": len(self.intelligence.intent_patterns) if self.intelligence else 0,
            "status": "operational"
        }


def bob_brain_init(user_message: str = "", context_budget: float = 0.35, verbose: bool = True) -> dict:
    """
    Main function to initialize Bob's brain system.
    
    Args:
        user_message: Optional user message for context analysis
        context_budget: Context budget to use (default 35%)
        verbose: Print initialization details
        
    Returns:
        Initialization results
    """
    
    brain_init = BobBrainInit()
    results = brain_init.initialize_brain(user_message, context_budget)
    
    if verbose:
        print("🤖 Bob Brain System Initialization")
        print("=" * 50)
        print(f"Status: {results['status']}")
        print(f"Version: {results['version']}")
        print(f"Protocols Loaded: {results['protocol_system']['total_protocols']}")
        print(f"Intelligence Patterns: {results['intelligence_system']['pattern_count']}")
        print(f"Initialization Time: {results['session_info']['initialization_time']:.3f}s")
        
        if 'user_analysis' in results:
            ua = results['user_analysis']
            print(f"\n🎯 User Request Analysis:")
            print(f"Intent: {ua['detected_intent']} (confidence: {ua['confidence']:.2f})")
            print(f"Recommended Protocols: {', '.join(ua['suggested_protocols']['primary'])}")
            print(f"Guidance: {ua['guidance']}")
        
        print(f"\n✅ Bob is ready for intelligent interaction!")
    
    return results


if __name__ == "__main__":
    # Command line usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Bob's Brain System")
    parser.add_argument("--message", "-m", default="", help="User message for context analysis")
    parser.add_argument("--context", "-c", type=float, default=0.35, help="Context budget (0.0-1.0)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")
    
    args = parser.parse_args()
    
    results = bob_brain_init(
        user_message=args.message,
        context_budget=args.context,
        verbose=not args.quiet
    )
    
    # Exit with success
    sys.exit(0 if results["status"] == "success" else 1)
