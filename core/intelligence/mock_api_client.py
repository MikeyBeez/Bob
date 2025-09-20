import abc
import asyncio

class BrainSystemInterface(abc.ABC):
    """
    Abstract base class for brain system integrations.
    Defines the contract for interacting with different AI model backends.
    """

    @abc.abstractmethod
    async def generate_chat_completion(self, messages: list, **kwargs) -> str:
        """Generate a chat completion from a list of messages."""
        pass

class MockOllamaApiClient(BrainSystemInterface):
    """
    A mock API client for Ollama that returns a dummy response.
    This is used for testing purposes when Ollama is not available.
    """
    async def generate_chat_completion(self, messages: list, **kwargs) -> str:
        """
        Returns a mock response after a short delay.
        """
        await asyncio.sleep(0.1)  # Simulate network latency
        last_message = messages[-1]['content'] if messages else ""
        return f"Mock response to: {last_message}"
