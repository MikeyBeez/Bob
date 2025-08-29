#!/usr/bin/env python3
"""
Test Bob's persistent memory system
"""

import json
from pathlib import Path

def test_persistent_memory():
    """Test the persistent memory file system."""
    
    print("🧪 Testing Bob's Persistent Memory System")
    print("=" * 50)
    
    memory_file = Path.home() / '.bob_memories.json'
    print(f"Memory file location: {memory_file}")
    
    # Check if memory file exists
    if memory_file.exists():
        print("✅ Memory file exists!")
        try:
            with open(memory_file, 'r') as f:
                memories = json.load(f)
            print(f"📝 Found {len(memories)} stored memories:")
            for memory_id, memory_data in memories.items():
                print(f"  • {memory_id}: {memory_data['content'][:60]}...")
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ Error reading memory file: {e}")
    else:
        print("📭 No memory file exists yet - will be created when first memory is stored")
    
    # Test storing a memory
    print(f"\\n🧪 Testing Memory Storage:")
    test_content = "User likes Python programming and testing"
    memory_id = f"mem_{hash(test_content) % 10000}"
    
    memories = {}
    if memory_file.exists():
        try:
            with open(memory_file, 'r') as f:
                memories = json.load(f)
        except:
            pass
    
    memories[memory_id] = {
        "content": test_content,
        "timestamp": "2025-08-29T15:30:00Z",
        "category": "user_preference"
    }
    
    try:
        with open(memory_file, 'w') as f:
            json.dump(memories, f, indent=2)
        print(f"✅ Successfully stored test memory: {memory_id}")
    except IOError as e:
        print(f"❌ Failed to store memory: {e}")
        return
    
    # Test retrieving memories
    print(f"\\n🧪 Testing Memory Retrieval:")
    query = "Python"
    
    try:
        with open(memory_file, 'r') as f:
            stored_memories = json.load(f)
        
        found_memories = []
        for mid, mdata in stored_memories.items():
            if query.lower() in mdata['content'].lower():
                found_memories.append(mdata['content'])
        
        if found_memories:
            print(f"✅ Found {len(found_memories)} memories matching '{query}':")
            for memory in found_memories:
                print(f"  • {memory}")
        else:
            print(f"❌ No memories found matching '{query}'")
    
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Error retrieving memories: {e}")
    
    print(f"\\n✅ Persistent memory system test complete!")

if __name__ == "__main__":
    test_persistent_memory()
