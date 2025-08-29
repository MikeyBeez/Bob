"""
Simple test for modular OllamaClient without external dependencies
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# We'll mock aiohttp for now
class MockClientSession:
    def __init__(self, *args, **kwargs):
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass
    
    async def get(self, url, **kwargs):
        class Response:
            async def json(self):
                return {"models": []}
            def raise_for_status(self):
                pass
        return Response()
    
    async def post(self, url, **kwargs):
        class Response:
            async def json(self):
                return {"response": "Test response"}
            def raise_for_status(self):
                pass
        return Response()
    
    @property
    def closed(self):
        return False

# Mock aiohttp module
import sys
sys.modules['aiohttp'] = type(sys)('aiohttp')
sys.modules['aiohttp'].ClientSession = MockClientSession
sys.modules['aiohttp'].ClientTimeout = lambda **kwargs: None
sys.modules['aiohttp'].ClientError = Exception

# Now we can import our module
from core.ollama_client import OllamaClient

def test_basic_structure():
    """Test that the modular OllamaClient is properly structured."""
    print("Testing OllamaClient modular structure...")
    
    # Create client
    client = OllamaClient()
    
    # Check main attributes
    assert hasattr(client, 'connection'), "Missing connection manager"
    assert hasattr(client, 'stream_handler'), "Missing stream handler"
    assert hasattr(client, 'retry_manager'), "Missing retry manager"
    assert hasattr(client, 'model_manager'), "Missing model manager"
    assert hasattr(client, 'metrics'), "Missing metrics tracker"
    
    print("✓ All submodules properly initialized")
    
    # Check main methods
    assert hasattr(client, 'generate'), "Missing generate method"
    assert hasattr(client, 'chat'), "Missing chat method"
    assert hasattr(client, 'list_models'), "Missing list_models method"
    assert hasattr(client, 'health_check'), "Missing health_check method"
    assert hasattr(client, 'get_metrics'), "Missing get_metrics method"
    
    print("✓ All main API methods present")
    
    # Check configuration
    assert client.base_url == "http://localhost:11434"
    assert client.timeout == 60
    assert client.max_retries == 3
    
    print("✓ Default configuration correct")
    
    # Test custom configuration
    custom_client = OllamaClient(
        base_url="http://192.168.1.100:11434",
        timeout=120,
        max_retries=5
    )
    
    assert custom_client.base_url == "http://192.168.1.100:11434"
    assert custom_client.timeout == 120
    assert custom_client.max_retries == 5
    
    print("✓ Custom configuration works")
    
    # Test metrics
    client.metrics.track_request("llama2", "Test prompt")
    stats = client.get_metrics()
    assert stats['total_requests'] == 1
    assert stats['model_usage']['llama2'] == 1
    
    print("✓ Metrics tracking works")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("OllamaClient Modular Structure Test")
    print("=" * 60)
    
    try:
        if test_basic_structure():
            print("\n✅ SUCCESS: OllamaClient follows the modular pattern!")
            print("\nModular structure summary:")
            print("  • Clean API surface in ollama_client.py")
            print("  • Connection management in ollama/connection.py")
            print("  • Streaming handler in ollama/streaming.py")
            print("  • Retry logic in ollama/retry.py")
            print("  • Model management in ollama/models.py")
            print("  • Metrics tracking in ollama/metrics.py")
            print("\n🎯 Next steps:")
            print("  1. Fix aiohttp installation in venv")
            print("  2. Run full async tests")
            print("  3. Update PROJECT_STRUCTURE.md")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
