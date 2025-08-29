"""
Test suite for modular OllamaClient
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ollama_client import OllamaClient


class TestOllamaClient:
    """Test the modular OllamaClient implementation."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return OllamaClient()
    
    def test_initialization(self, client):
        """Test client initializes with correct defaults."""
        assert client.base_url == "http://localhost:11434"
        assert client.timeout == 60
        assert client.max_retries == 3
        assert client.connection is not None
        assert client.stream_handler is not None
        assert client.retry_manager is not None
        assert client.model_manager is not None
        assert client.metrics is not None
    
    def test_custom_initialization(self):
        """Test client with custom configuration."""
        client = OllamaClient(
            base_url="http://192.168.1.100:11434",
            timeout=120,
            max_retries=5
        )
        assert client.base_url == "http://192.168.1.100:11434"
        assert client.timeout == 120
        assert client.max_retries == 5
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        # Mock the connection.get method
        client.connection.get = AsyncMock(return_value={"models": []})
        
        result = await client.health_check()
        assert result is True
        client.connection.get.assert_called_once_with("/api/tags")
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test failed health check."""
        # Mock connection failure
        client.connection.get = AsyncMock(side_effect=Exception("Connection failed"))
        
        result = await client.health_check()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_non_streaming(self, client):
        """Test non-streaming text generation."""
        # Mock the retry manager and connection
        mock_response = {
            "response": "Hello, this is a test response",
            "total_duration": 1000000000,  # 1 second in nanoseconds
            "eval_count": 10
        }
        
        client.retry_manager.execute = AsyncMock(return_value=mock_response)
        
        result = await client.generate(
            prompt="Test prompt",
            model="llama2",
            temperature=0.7
        )
        
        assert result == "Hello, this is a test response"
        assert client.metrics.request_count == 1
    
    @pytest.mark.asyncio
    async def test_chat_completion(self, client):
        """Test chat completion."""
        # Mock response
        mock_response = {
            "message": {
                "role": "assistant",
                "content": "This is a chat response"
            }
        }
        
        client.retry_manager.execute = AsyncMock(return_value=mock_response)
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        result = await client.chat(messages, model="llama2")
        
        assert result == "This is a chat response"
        assert client.metrics.request_count == 1
    
    @pytest.mark.asyncio
    async def test_list_models(self, client):
        """Test listing available models."""
        mock_models = {
            "models": [
                {"name": "llama2", "size": 1000000},
                {"name": "codellama", "size": 2000000}
            ]
        }
        
        client.model_manager.list_models = AsyncMock(return_value=mock_models["models"])
        
        models = await client.list_models()
        
        assert len(models) == 2
        assert models[0]["name"] == "llama2"
        assert models[1]["name"] == "codellama"
    
    @pytest.mark.asyncio
    async def test_generate_embeddings(self, client):
        """Test embedding generation."""
        mock_response = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        client.retry_manager.execute = AsyncMock(return_value=mock_response)
        
        embeddings = await client.generate_embeddings(
            text="Test text for embeddings",
            model="llama2"
        )
        
        assert len(embeddings) == 5
        assert embeddings == [0.1, 0.2, 0.3, 0.4, 0.5]
    
    def test_metrics_tracking(self, client):
        """Test metrics are properly tracked."""
        # Track some requests
        client.metrics.track_request("llama2", "Test prompt 1")
        client.metrics.track_request("codellama", "Test prompt 2")
        client.metrics.track_response("llama2", 1000000000, 50)
        
        stats = client.get_metrics()
        
        assert stats["total_requests"] == 2
        assert stats["total_tokens"] == 50
        assert stats["model_usage"]["llama2"] == 1
        assert stats["model_usage"]["codellama"] == 1
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, client):
        """Test that retry logic is properly configured."""
        # Create a mock function that fails twice then succeeds
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return {"success": True}
        
        result = await client.retry_manager.execute(mock_func)
        
        assert call_count == 3
        assert result == {"success": True}


if __name__ == "__main__":
    # Run basic tests
    print("Running OllamaClient tests...")
    
    client = OllamaClient()
    print(f"✓ Client initialized with base_url: {client.base_url}")
    
    # Test metrics
    client.metrics.track_request("llama2", "Test prompt")
    stats = client.get_metrics()
    print(f"✓ Metrics tracking: {stats['total_requests']} requests")
    
    # Run async tests
    async def run_async_tests():
        client = OllamaClient()
        
        # Test health check
        try:
            health = await client.health_check()
            print(f"✓ Health check: {'Ollama is running' if health else 'Ollama not available'}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
        
        # Test model listing if Ollama is available
        if health:
            try:
                models = await client.list_models()
                print(f"✓ Found {len(models)} models")
                for model in models[:3]:  # Show first 3
                    print(f"  - {model.get('name', 'unknown')}")
            except Exception as e:
                print(f"✗ Model listing failed: {e}")
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    print("\n✅ Basic OllamaClient tests completed!")
