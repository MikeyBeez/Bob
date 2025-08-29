#!/usr/bin/env python3
"""
Bob API Entry Point

Direct entry point for the Bob API interface that handles imports properly
when run as a module or script.
"""

import sys
import os
from pathlib import Path

# Add the Bob directory to Python path
bob_dir = Path(__file__).parent.absolute()
if str(bob_dir) not in sys.path:
    sys.path.insert(0, str(bob_dir))

# Now import the API
from interfaces.api_interface import run_api

def main():
    """Main entry point for Bob API."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bob LLM-as-Kernel Intelligence System API"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Logging level (default: info)"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Bob API on {args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    
    run_api(
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
