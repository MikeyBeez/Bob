# Bob - Better Organized Brain (v5.0)

An intelligent agent system built around Ollama for enhanced cognition and knowledge management.

## Project Overview

Bob is the fifth iteration of an evolving brain enhancement system. This version focuses on:

- **Ollama Integration**: Local LLM agent capabilities
- **Knowledge Organization**: Better information management
- **Cognitive Enhancement**: Augmented thinking and reasoning
- **Agent Framework**: Autonomous task execution

## Architecture

```
Bob/
├── core/           # Core agent logic
├── agents/         # Specialized agent modules  
├── knowledge/      # Knowledge management system
├── interfaces/     # APIs and user interfaces
├── config/         # Configuration and settings
├── tools/          # External tool integrations
├── data/           # Persistent data storage
└── tests/          # Test suites
```

## Technology Stack

- **Python 3.11+** - Core language
- **Ollama** - Local LLM inference
- **FastAPI** - Web API framework  
- **SQLite/PostgreSQL** - Data persistence
- **asyncio** - Async operations
- **Pydantic** - Data validation
- **pytest** - Testing framework

## Getting Started

```bash
# Setup development environment with UV
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or run directly with UV
uv run python -m bob
```

## Development Status

**Version 5.0** - Fifth reboot focusing on Ollama integration and agent capabilities.

Previous iterations explored various approaches to cognitive enhancement and knowledge management. This version represents a significant architectural evolution.
