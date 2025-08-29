"""
__init__.py - Interface Module Initialization

Exports the main interface classes and provides convenient imports
for the Bob Agent interface layer.

AVAILABLE INTERFACES:
====================
• BobCLI - Command-line interface for interactive usage
• BobCLISession - CLI session management
• FastAPI app - RESTful API interface for programmatic access
• run_api - API server runner function

USAGE:
======
# CLI Interface
from interfaces import BobCLI
cli = BobCLI()
await cli.start()

# API Interface  
from interfaces import run_api
run_api(host="0.0.0.0", port=8000)

# Or run API directly
from interfaces.api_interface import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
"""

from .cli_interface import BobCLI, BobCLISession
from .api_interface import app, run_api

__all__ = [
    "BobCLI",
    "BobCLISession", 
    "app",
    "run_api"
]

__version__ = "1.0.0"
__description__ = "Bob LLM-as-Kernel Intelligence System - User Interfaces"
