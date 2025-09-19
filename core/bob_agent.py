import asyncio
import logging
from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from core.knowledge_manager import KnowledgeManager
from core.job_system.manager import JobManager
from core.job_system.models import JobResult

logger = logging.getLogger(__name__)

class BobAgent(BaseAgent):
    """
    Main Bob agent. Orchestrates all cognitive functions by managing a
    JobManager and handling results.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Bob", config)
        self.knowledge_manager = KnowledgeManager(config)
        self.job_manager = JobManager(config)
        self.active_jobs: Dict[int, str] = {}
        self.thinking_model = config.get('thinking_model', 'llama3.2') # Will be moved to a client
        self._shutdown = asyncio.Event()

    async def initialize(self):
        """Initializes Bob's cognitive systems."""
        logger.info("Initializing Bob's cognitive systems...")
        await self.knowledge_manager.initialize()
        await self.job_manager.start()
        logger.info("Bob initialized successfully.")

    async def think_task(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        A task that performs the core thinking process.
        This will be executed as a job by the JobManager.
        NOTE: For now, this returns a dummy response. It will be updated to
        use a pluggable LLM client (e.g., Gemini).
        """
        logger.info(f"Thinking about: {prompt[:80]}...")
        await asyncio.sleep(2) # Simulate work
        
        if context:
            enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
        else:
            enhanced_prompt = prompt

        # DUMMY RESPONSE
        response = f"This is a dummy response to the prompt: '{enhanced_prompt}'"
        
        await self.knowledge_manager.store_thought(prompt, response)
        return response

    async def process_query(self, query: str):
        """
        Processes a user query by submitting it as a job.
        This method is now non-blocking.
        """
        logger.info(f"Processing query: {query}")
        context = await self.knowledge_manager.search_relevant(query)
        job_id = await self.job_manager.submit_job(
            self.think_task, query, context=context
        )
        self.active_jobs[job_id] = query
        logger.info(f"Query submitted as job {job_id}.")

    async def run(self):
        """Main execution loop for Bob."""
        logger.info("Bob is now active and ready to help organize your brain!")
        
        try:
            while not self._shutdown.is_set():
                try:
                    # Wait for a result from the JobManager
                    result: JobResult = await asyncio.wait_for(self.job_manager.result_queue.get(), timeout=1.0)
                    self._handle_result(result)
                except asyncio.TimeoutError:
                    # No result, continue loop. We can do other maintenance here.
                    await self.knowledge_manager.periodic_maintenance()

        except KeyboardInterrupt:
            logger.info("Bob received shutdown signal.")
        finally:
            await self.cleanup()

    def _handle_result(self, result: JobResult):
        """Handles a completed job result."""
        original_prompt = self.active_jobs.pop(result.job_id, "Unknown prompt")
        if result.error:
            logger.error(f"Job {result.job_id} ('{original_prompt}') failed: {result.error}")
        else:
            logger.info(f"Job {result.job_id} ('{original_prompt}') completed successfully.")
            # For now, we just log the result.
            # In the future, this could trigger other jobs or notify the user.
            logger.info(f"Result: {result.result}")

    async def cleanup(self):
        """Clean shutdown of Bob's systems."""
        logger.info("Bob is cleaning up...")
        self._shutdown.set()
        await self.job_manager.stop()
        await self.knowledge_manager.cleanup()
        logger.info("Bob shutdown complete.")

    def _enhance_prompt_with_context(self, prompt: str, context: Dict) -> str:
        """Enhance prompt with relevant context."""
        if not context or not context.get('relevant_docs'):
            return prompt

        context_text = "\n".join(
            [f"- {item}" for item in context.get('relevant_docs', [])]
        )
        
        return f"Context from knowledge base:\n{context_text}\n\nUser query: {prompt}"
