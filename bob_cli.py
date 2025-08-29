#!/usr/bin/env python3
"""
Bob CLI Entry Point

Direct entry point for the Bob CLI interface that handles imports properly
when run as a module or script.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the Bob directory to Python path
bob_dir = Path(__file__).parent.absolute()
if str(bob_dir) not in sys.path:
    sys.path.insert(0, str(bob_dir))

# Now import the CLI
from interfaces.cli_interface import BobCLI

def main():
    """Main entry point for Bob CLI."""
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
    
    asyncio.run(cli.start())

if __name__ == "__main__":
    main()
