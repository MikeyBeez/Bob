"""
Core Bob Agent - The heart of the Better Organized Brain
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import ollama
from core.knowledge_manager import KnowledgeManager
from core.task_scheduler import TaskScheduler
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class BobAgent(BaseAgent):
    """Main Bob agent that orchestrates all cognitive functions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Bob", config)
        self.ollama_client = ollama.Client(host=config.get('ollama_host', 'http://localhost:11434'))
        self.knowledge_manager = KnowledgeManager(config)
        self.task_scheduler = TaskScheduler(config)
        self.active_tasks = {}
        self.thinking_model = config.get('thinking_model', 'llama3.2')
        
    async def initialize(self):
        """Initialize Bob's cognitive systems"""
        logger.info("Initializing Bob's cognitive systems...")
        
        # Test Ollama connection
        try:
            models = await asyncio.to_thread(self.ollama_client.list)
            logger.info(f"Connected to Ollama. Available models: {[m['name'] for m in models['models']]}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise
        
        # Initialize knowledge system
        await self.knowledge_manager.initialize()
        
        # Initialize task scheduler
        await self.task_scheduler.initialize()
        
        logger.info("Bob initialized successfully")
    
    async def think(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Core thinking function using Ollama"""
        try:
            # Add context from knowledge base
            if context:
                enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
            else:
                enhanced_prompt = prompt
            
            # Generate response using Ollama
            response = await asyncio.to_thread(
                self.ollama_client.generate,
                model=self.thinking_model,
                prompt=enhanced_prompt,
                stream=False
            )
            
            thought = response['response']
            
            # Store the thought for future reference
            await self.knowledge_manager.store_thought(prompt, thought)
            
            return thought
            
        except Exception as e:
            logger.error(f"Error in thinking process: {e}")
            return f"Sorry, I encountered an error while thinking: {e}"
    
    async def process_query(self, query: str) -> str:
        """Process a user query and return response"""
        logger.info(f"Processing query: {query}")
        
        # Search relevant knowledge
        context = await self.knowledge_manager.search_relevant(query)
        
        # Generate response
        response = await self.think(query, context)
        
        return response
    
    async def run(self):
        """Main execution loop for Bob"""
        logger.info("Bob is now active and ready to help organize your brain!")
        
        try:
            while True:
                # Process scheduled tasks
                await self.task_scheduler.process_pending_tasks()
                
                # Check for knowledge updates
                await self.knowledge_manager.periodic_maintenance()
                
                # Sleep briefly to avoid busy waiting
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Bob received shutdown signal")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean shutdown of Bob's systems"""
        logger.info("Bob is cleaning up...")
        await self.knowledge_manager.cleanup()
        await self.task_scheduler.cleanup()
        logger.info("Bob shutdown complete")
    
    def _enhance_prompt_with_context(self, prompt: str, context: Dict) -> str:
        """Enhance prompt with relevant context"""
        context_text = "\n".join([
            f"Relevant information: {item}" 
            for item in context.get('relevant_docs', [])
        ])
        
        enhanced = f"""Context from knowledge base:
{context_text}

User query: {prompt}

Please provide a helpful response based on the context and your knowledge."""
        
        return enhanced
