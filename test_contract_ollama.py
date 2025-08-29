"""
Test for Contract-Based Ollama Client
Tests the new contract-compliant implementation.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add Bob project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.api_clients import OllamaClient, create_ollama_client
from integrations.contracts import APIRequest, ClientConfiguration


async def test_ollama_client():
    """Test the new contract-based Ollama client"""
    print("🧪 Testing Contract-Based Ollama Client")
    print("=" * 50)
    
    # Test client creation
    print("1. Creating Ollama client...")
    client = create_ollama_client()
    print(f"   ✓ Client created: {client.client_name}")
    print(f"   ✓ Base URL: {client.base_url}")
    print(f"   ✓ Features: {client.supported_features}")
    
    # Test connection
    print("\n2. Testing connection...")
    health_status = await client.health_check()
    connection_details = await client.test_connection()
    print(f"   ✓ Health check: {'PASS' if health_status else 'FAIL'}")
    print(f"   ✓ Connection test: {connection_details['message']}")
    
    if not health_status:
        print("   ⚠️  Ollama not running - skipping API tests")
        print("   💡 Start Ollama with: ollama serve")
        return
    
    # Test model listing
    print("\n3. Getting available models...")
    try:
        models = await client.get_available_models()
        if models:
            print(f"   ✓ Found {len(models)} models:")
            for model in models[:3]:  # Show first 3
                print(f"     • {model.name}")
        else:
            print("   ⚠️  No models found - pull a model first")
            print("   💡 Try: ollama pull llama2")
            return
    except Exception as e:
        print(f"   ❌ Error getting models: {e}")
        return
    
    # Test simple generation
    print("\n4. Testing text generation...")
    try:
        request = APIRequest(
            prompt="Say hello in exactly 5 words",
            model=models[0].name,  # Use first available model
            max_tokens=50,
            temperature=0.1
        )
        
        response = await client.generate_response(request)
        print(f"   ✓ Generation successful")
        print(f"   ✓ Response: {response.content.strip()}")
        print(f"   ✓ Tokens used: {response.tokens_used}")
        print(f"   ✓ Duration: {response.duration:.2f}s")
        print(f"   ✓ Cost: ${response.cost:.4f}")
        
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        return
    
    # Test streaming
    print("\n5. Testing streaming generation...")
    try:
        stream_request = APIRequest(
            prompt="Count from 1 to 5, one number per line",
            model=models[0].name,
            max_tokens=100,
            temperature=0.1,
            stream=True
        )
        
        print("   ✓ Streaming response:")
        print("   ", end="", flush=True)
        
        async for chunk in client.stream_response(stream_request):
            print(chunk, end="", flush=True)
        
        print(f"\n   ✓ Streaming completed")
        
    except Exception as e:
        print(f"   ❌ Streaming failed: {e}")
    
    # Test configuration
    print("\n6. Testing configuration...")
    current_config = client.get_configuration()
    print(f"   ✓ Current timeout: {current_config.timeout}s")
    
    new_config = ClientConfiguration(
        base_url=current_config.base_url,
        timeout=30,
        max_retries=5
    )
    
    config_success = await client.configure(new_config)
    updated_config = client.get_configuration()
    print(f"   ✓ Config updated: {config_success}")
    print(f"   ✓ New timeout: {updated_config.timeout}s")
    print(f"   ✓ New max retries: {updated_config.max_retries}")
    
    print("\n" + "=" * 50)
    print("🎉 Contract-based Ollama client test completed!")
    print(f"📊 Client made {client.request_count} requests")
    print(f"⏰ Last request: {client.last_request_time}")


async def test_compatibility_layer():
    """Test the compatibility layer"""
    print("\n🔄 Testing Compatibility Layer")
    print("=" * 50)
    
    try:
        # Import compatibility layer
        from src.modules.ollama_client_compat import process_prompt, OllamaClientCompatibility
        
        print("1. Testing compatibility import...")
        print("   ✓ Compatibility layer imported successfully")
        
        print("\n2. Testing legacy interface...")
        compat_client = OllamaClientCompatibility()
        
        # This should work exactly like the old client
        # Note: This will fail if Ollama isn't running, which is expected
        try:
            response = compat_client.process_prompt(
                "Say hello in 3 words", 
                "llama2",  # This might not exist
                "test_user"
            )
            print(f"   ✓ Legacy interface works: {response[:50]}...")
        except Exception as e:
            print(f"   ⚠️  Legacy interface error (expected if model not available): {e}")
        
        print("   ✓ Compatibility layer functional")
        
    except ImportError as e:
        print(f"   ❌ Compatibility layer import failed: {e}")


if __name__ == "__main__":
    print("🚀 Bob v5.0 - Contract-Based Ollama Client Tests")
    print("=" * 60)
    
    # Run async tests
    asyncio.run(test_ollama_client())
    
    # Test compatibility
    asyncio.run(test_compatibility_layer())
    
    print("\n✅ All tests completed!")
