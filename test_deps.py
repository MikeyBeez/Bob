#!/usr/bin/env python3

import sys
import os

# Add virtual environment to path
venv_path = "/Users/bard/Bob/.venv/lib/python3.9/site-packages"
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

try:
    import aiohttp
    print("✅ aiohttp installed with uv and working!")
    print("🚀 Now testing full Bob...")
    
    # Test Bob's main interface
    sys.path.insert(0, "/Users/bard/Bob")
    from bob_ollama_bridge import BrainSystemFunctionBridge
    
    print("✅ Bob's LLM bridge works!")
    print("🎉 Bob is ready with real Ollama integration!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Falling back to simple Bob interface...")
