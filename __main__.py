import asyncio
import logging
from core.bob_agent import BobAgent

# Configure basic logging to see the agent's activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

async def main():
    """
    A simple integration test for the BobAgent.
    Initializes the agent, submits a few jobs, lets it run, and then shuts down.
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting Bob Agent integration test...")

    # 1. Initialize the agent
    config = {} # Using default config for now
    agent = BobAgent(config)
    await agent.initialize()

    # 2. Start the agent's main run loop in the background
    agent_task = asyncio.create_task(agent.run())

    # 3. Submit a few test queries
    # These will be processed as jobs by the JobManager
    logger.info("Submitting test queries...")
    await agent.process_query("What is the meaning of life?")
    await agent.process_query("Can you summarize the book 'Dune'?")
    await agent.process_query("Write a short poem about asynchronous programming.")

    # 4. Let the agent run for a bit to process the jobs
    logger.info("Letting the agent work for 5 seconds...")
    await asyncio.sleep(5)

    # 5. Shut down the agent gracefully
    logger.info("Shutting down the agent...")
    agent_task.cancel() # Cancel the main run loop
    try:
        await agent_task # Wait for the run loop to finish cleanup
    except asyncio.CancelledError:
        logger.info("Agent run loop cancelled successfully.")

    logger.info("Integration test finished.")

if __name__ == "__main__":
    asyncio.run(main())
