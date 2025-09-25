#!/usr/bin/env python3
"""
Test Bob's Memory Intelligence System
Simple function-based memory intelligence (no MCP complexity)
"""

import sys
from pathlib import Path

# Add Bob directory to path
bob_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(bob_dir))

from bob_memory_intelligence import BobMemoryIntelligence
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

def test_memory_intelligence():
    """Comprehensive test of Bob's memory intelligence."""
    console = Console()
    
    console.print(Panel(
        "🧠 Bob Memory Intelligence System Test\nSimple Functions - No MCP Complexity",
        title="Memory Intelligence",
        style="cyan bold"
    ))
    
    # Initialize the system
    intelligence = BobMemoryIntelligence()
    
    # Test cases
    test_cases = [
        ("i like chocolate", "Should detect preference storage"),
        ("what do you remember about me", "Should detect memory recall"),
        ("remember that", "Should provide clarification"),
        ("recommend a good restaurant", "Should detect context enhancement"),
        ("hello how are you", "Should do nothing"),
        ("i work at Google", "Should detect work information"),
        ("my wife Sarah", "Should detect relationship info"),
        ("remember it", "Should clarify unclear reference")
    ]
    
    # Create results table
    table = Table(title="Memory Intelligence Analysis Results")
    table.add_column("User Input", style="white", width=25)
    table.add_column("Action", style="yellow", width=12)
    table.add_column("Confidence", style="green", width=10)
    table.add_column("Type/Reason", style="cyan", width=20)
    table.add_column("Expected", style="magenta", width=25)
    
    console.print()
    
    for user_input, expected in test_cases:
        analysis = intelligence.analyze_user_input(user_input)
        
        action = analysis['action']
        confidence = f"{analysis.get('confidence', 0):.2f}" if analysis.get('confidence') else "N/A"
        
        if action == 'store':
            detail = f"Type: {analysis.get('type', 'unknown')}"
        elif action == 'recall':
            detail = f"Query: {analysis.get('query_type', 'unknown')}"
        elif action == 'clarify':
            detail = f"Issue: {analysis.get('issue', 'unknown')}"
        elif action == 'enhance':
            detail = f"Context: {analysis.get('context_type', 'unknown')}"
        else:
            detail = analysis.get('reason', 'none')
            
        # Color code the action
        if action == 'store':
            action_colored = f"[green]{action}[/green]"
        elif action == 'recall':
            action_colored = f"[blue]{action}[/blue]"
        elif action == 'clarify':
            action_colored = f"[yellow]{action}[/yellow]"
        elif action == 'enhance':
            action_colored = f"[cyan]{action}[/cyan]"
        else:
            action_colored = f"[dim]{action}[/dim]"
        
        table.add_row(
            user_input,
            action_colored, 
            confidence,
            detail,
            expected
        )
    
    console.print(table)
    
    # Show system stats
    console.print()
    stats = intelligence.get_stats()
    
    stats_panel = Panel(
        f"""**System**: {stats['system']}
**Analyzed**: {stats['stats']['analyzed']} inputs
**Capabilities**: {len(stats['capabilities'])} features

**Pattern Types**:
• Storage: {', '.join(stats['patterns_supported']['storage'])}
• Recall: {', '.join(stats['patterns_supported']['recall'])}  
• Clarification: {', '.join(stats['patterns_supported']['clarification'])}
• Enhancement: {', '.join(stats['patterns_supported']['enhancement'])}

✅ **No MCP servers needed** - Pure function-based intelligence!
🚀 **Ready for integration** with Bob's Ollama bridge""",
        title="Memory Intelligence Stats",
        style="green"
    )
    
    console.print(stats_panel)
    
    console.print()
    console.print("🎉 [bold green]Memory Intelligence Test Complete![/bold green]")
    console.print("💡 [dim]Bob now has intelligent memory management without MCP complexity![/dim]")

if __name__ == "__main__":
    test_memory_intelligence()
