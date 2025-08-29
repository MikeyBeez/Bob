"""
streaming.py - Handle streaming responses from Ollama API
"""

import json
from typing import AsyncGenerator, Dict, Any


class StreamHandler:
    """Handles streaming responses from Ollama."""
    
    def __init__(self):
        """Initialize stream handler."""
        self.current_response = ""
        self.total_tokens = 0
        
    async def handle_stream(self, 
                           connection,
                           endpoint: str,
                           data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Handle streaming response from Ollama.
        
        Args:
            connection: ConnectionManager instance
            endpoint: API endpoint
            data: Request data
            
        Yields:
            Response chunks as they arrive
        """
        self.current_response = ""
        self.total_tokens = 0
        
        async for line in connection.post_stream(endpoint, data):
            try:
                # Decode and parse JSON line
                chunk = json.loads(line.decode('utf-8'))
                
                # Extract response text
                if 'response' in chunk:
                    text = chunk['response']
                    self.current_response += text
                    yield text
                
                # Track token count if available
                if 'eval_count' in chunk:
                    self.total_tokens = chunk['eval_count']
                
                # Check if stream is done
                if chunk.get('done', False):
                    break
                    
            except json.JSONDecodeError:
                # Skip malformed lines
                continue
            except Exception as e:
                # Log error but continue stream
                print(f"Stream processing error: {e}")
                continue
    
    def get_accumulated_response(self) -> str:
        """Get the complete accumulated response."""
        return self.current_response
    
    def get_token_count(self) -> int:
        """Get the total token count from the stream."""
        return self.total_tokens
    
    async def handle_chat_stream(self,
                                connection,
                                endpoint: str,
                                data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Handle streaming chat response.
        
        Args:
            connection: ConnectionManager instance
            endpoint: API endpoint
            data: Request data
            
        Yields:
            Chat response chunks
        """
        self.current_response = ""
        
        async for line in connection.post_stream(endpoint, data):
            try:
                chunk = json.loads(line.decode('utf-8'))
                
                # Extract message content
                if 'message' in chunk and 'content' in chunk['message']:
                    text = chunk['message']['content']
                    self.current_response += text
                    yield text
                
                if chunk.get('done', False):
                    break
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Chat stream error: {e}")
                continue
