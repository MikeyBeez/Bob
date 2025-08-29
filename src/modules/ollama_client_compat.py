"""
Compatibility Layer for Ollama Client Migration
Provides backward compatibility while transitioning to contract-based architecture.
"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.text import Text

# Fix imports for integration layer
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from integrations.api_clients import OllamaClient, create_ollama_client
from integrations.contracts import APIRequest, ClientConfiguration
from .logging_setup import logger
from .save_history import save_interaction


class OllamaClientCompatibility:
    """
    Compatibility wrapper that provides the old interface
    while using the new contract-based implementation internally.
    """
    
    def __init__(self, base_url="http://localhost:11434", timeout=60):
        """Initialize compatibility layer"""
        self.console = Console()
        config = ClientConfiguration(base_url=base_url, timeout=timeout)
        self._client = OllamaClient(config)
    
    def process_prompt(self, prompt: str, model: str, username: str) -> str:
        """
        Legacy sync interface - converts to async internally
        Maintains exact same signature as original implementation
        """
        logger.info(f"Processing prompt for user: {username}, model: {model}")
        
        try:
            # Run async method in sync context
            response = asyncio.run(self._process_prompt_async(prompt, model, username))
            return response
            
        except Exception as e:
            error_msg = f"Error processing prompt: {str(e)}"
            logger.error(error_msg)
            self.console.print(error_msg, style="bold red")
            return error_msg
    
    async def _process_prompt_async(self, prompt: str, model: str, username: str) -> str:
        """Internal async implementation"""
        # Create API request using new contract
        request = APIRequest(
            prompt=prompt,
            model=model,
            max_tokens=4096,
            temperature=0.7
        )
        
        try:
            # Show processing indicator
            with Live(Text("Processing...", style="yellow bold"), refresh_per_second=4) as live:
                # Use new contract-based client
                response = await self._client.generate_response(request)
                live.update(Text(response.content, style="yellow bold"))
            
            # Save interaction using existing system
            save_interaction(prompt, response.content, username, model)
            
            logger.info(f"Response generated for prompt: {prompt[:50]}...")
            return response.content
            
        except Exception as e:
            # Convert new errors to old format for compatibility
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


# Create global instance for backward compatibility
default_client_compat = OllamaClientCompatibility()

def process_prompt(prompt: str, model: str, username: str) -> str:
    """
    Global function maintaining exact same interface as original
    """
    return default_client_compat.process_prompt(prompt, model, username)

# Maintain legacy alias
generate_response = process_prompt

# For projects that import the class directly
OllamaClientLegacy = OllamaClientCompatibility

__all__ = [
    'OllamaClientCompatibility', 
    'OllamaClientLegacy',
    'process_prompt', 
    'generate_response',
    'default_client_compat'
]
