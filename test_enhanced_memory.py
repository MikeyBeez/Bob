#!/usr/bin/env python3
"""
Test the enhanced memory system
"""

import sys
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent))

from bob_ollama_bridge import BrainSystemFunctionBridge

async def test_memory_system():
    """Test the memory storage and retrieval system."""
    
    print("🧪 Testing Bob's Enhanced Memory System")
    print("=" * 50)
    
    # Create bridge
    bridge = BrainSystemFunctionBridge()
    
    # Test 1: Store a memory
    print("\n1️⃣ Testing Memory Storage:")
    store_result = await bridge.execute_brain_tool("brain_remember", {
        "content": "User likes Python programming"
    })
    print(f"Storage result: {store_result}")
    
    # Test 2: Recall with specific query
    print("\n2️⃣ Testing Memory Recall (specific):")
    recall_result = await bridge.execute_brain_tool("brain_recall", {
        "query": "Python"
    })
    print(f"Recall result: {recall_result}")
    
    # Test 3: Recall with generic query
    print("\n3️⃣ Testing Memory Recall (generic):")
    generic_recall = await bridge.execute_brain_tool("brain_recall", {
        "query": "me"
    })
    print(f"Generic recall result: {generic_recall}")
    
    # Test 4: Store another memory
    print("\n4️⃣ Testing Second Memory Storage:")
    store_result2 = await bridge.execute_brain_tool("brain_remember", {
        "content": "User prefers TypeScript for web development"
    })
    print(f"Second storage result: {store_result2}")
    
    # Test 5: Recall all memories
    print("\n5️⃣ Testing Recall All Memories:")
    all_recall = await bridge.execute_brain_tool("brain_recall", {
        "query": "a"  # Short query should show all
    })
    print(f"All memories result: {all_recall}")
    
    # Test formatting
    print("\n📋 Testing Result Formatting:")
    formatted_store = bridge._format_tool_result("brain_remember", store_result)
    print(f"Formatted storage:\n{formatted_store}")
    
    formatted_recall = bridge._format_tool_result("brain_recall", all_recall)
    print(f"\nFormatted recall:\n{formatted_recall}")

if __name__ == "__main__":
    asyncio.run(test_memory_system())
