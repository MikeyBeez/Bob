import logging
import asyncio
import os
import time
from typing import Dict, Any, List

from tools.non_blocking_git_push import non_blocking_git_push

logger = logging.getLogger(__name__)

class KnowledgeManager:
    """
    Manages Bob's knowledge base.
    This is a placeholder implementation.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info("KnowledgeManager initialized (placeholder).")

    async def initialize(self):
        """Initializes the knowledge manager."""
        logger.info("KnowledgeManager resources initialized (placeholder).")

    async def cleanup(self):
        """Cleans up resources."""
        logger.info("KnowledgeManager resources cleaned up (placeholder).")

    async def store_thought(self, prompt: str, thought: str):
        """Stores a thought by committing it to a git repository and pushing."""
        logger.info(f"Storing thought by committing and pushing: {prompt[:50]}...")

        # In a real application, these would come from the config.
        repo_path = "."  # Assuming the repo is the current directory
        remote = "origin"
        branch = "main"

        # 1. Create a file with the thought
        # Sanitize the prompt to create a valid filename
        sanitized_prompt = "".join(c if c.isalnum() or c in (' ', '-') else '' for c in prompt).rstrip()
        thought_filename = f"thoughts/{sanitized_prompt[:40].replace(' ', '_')}.txt"

        # ensure thoughts directory exists
        os.makedirs("thoughts", exist_ok=True)

        with open(thought_filename, "w") as f:
            f.write(thought)

        # 2. Stage the new file
        await self.run_git_command(repo_path, ["git", "add", thought_filename])

        # 3. Commit the change
        commit_message = f"Add thought for prompt: {prompt}"
        await self.run_git_command(repo_path, ["git", "commit", "-m", commit_message])

        # 4. Push the change using the non-blocking tool
        start_time = time.monotonic()
        success = await non_blocking_git_push(repo_path, remote, branch)
        duration = time.monotonic() - start_time
        logger.info(f"Operation 'non_blocking_git_push' took {duration:.4f} seconds.")

        if success:
            logger.info("Successfully stored and pushed thought.")
        else:
            logger.error("Failed to store and push thought.")

    async def run_git_command(self, repo_path: str, command: list[str]):
        """Helper to run a git command asynchronously."""
        cmd = command
        # Insert -C repo_path into git command
        if command[0] == "git":
            # a bit of a hack to avoid modifying the list in place multiple times
            cmd = command[:1] + ["-C", repo_path] + command[1:]

        start_time = time.monotonic()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        duration = time.monotonic() - start_time
        logger.info(f"Operation '{" ".join(cmd)}' took {duration:.4f} seconds.")

        # git commit can return 1 if there's nothing to commit, which is not an error for us.
        if process.returncode != 0:
            stderr_str = stderr.decode()
            if "nothing to commit" in stderr_str:
                logger.info("Nothing to commit, continuing.")
                return True

            logger.error(f"Git command failed: {' '.join(cmd)}")
            logger.error(stderr_str)
            return False

        if stdout:
            logger.info(f"[git stdout] {stdout.decode()}")
        if stderr:
            logger.info(f"[git stderr] {stderr.decode()}")
        return True

    async def search_relevant(self, query: str) -> Dict[str, List[str]]:
        """Searches for relevant knowledge."""
        logger.info(f"Searching knowledge (placeholder): {query[:50]}...")
        return {"relevant_docs": []}

    async def periodic_maintenance(self):
        """Performs periodic maintenance."""
        pass
