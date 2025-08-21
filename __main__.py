"""
Bob - Better Organized Brain
Main entry point for the agent system
"""

import asyncio
import logging
from pathlib import Path

from core.bob_agent import BobAgent
from config.settings import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for Bob"""
    try:
        # Load configuration
        config = load_config()
        logger.info("Bob v5.0 - Better Organized Brain starting...")
        
        # Initialize Bob agent
        bob = BobAgent(config)
        await bob.initialize()
        
        # Start Bob's main loop
        await bob.run()
        
    except KeyboardInterrupt:
        logger.info("Bob shutting down gracefully...")
    except Exception as e:
        logger.error(f"Bob encountered an error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
