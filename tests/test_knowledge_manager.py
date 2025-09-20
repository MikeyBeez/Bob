import asyncio
import os
import subprocess
from unittest.mock import patch, AsyncMock

import pytest
from core.knowledge_manager import KnowledgeManager

@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)

    # Create an initial commit so we can push to a branch
    (repo_path / "README.md").write_text("Initial commit")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    return repo_path

@pytest.mark.asyncio
async def test_store_thought_creates_commit_and_pushes(temp_git_repo):
    """
    Tests that store_thought creates a new file, commits it, and calls the
    non-blocking push function.
    """
    repo_path = str(temp_git_repo)
    km = KnowledgeManager(config={})

    prompt = "test prompt"
    thought = "this is a test thought"

    with patch("core.knowledge_manager.non_blocking_git_push", new_callable=AsyncMock) as mock_push:
        # We need to change the working directory so that the KnowledgeManager,
        # which uses relative paths, works correctly within the temp repo.
        original_cwd = os.getcwd()
        os.chdir(repo_path)

        try:
            await km.store_thought(prompt, thought)
        finally:
            os.chdir(original_cwd)

        # 1. Assert that the push function was called
        mock_push.assert_called_once_with(".", "origin", "main")

        # 2. Assert that a new file was created in the thoughts directory
        thought_files = os.listdir(os.path.join(repo_path, "thoughts"))
        assert len(thought_files) == 1

        sanitized_prompt = "test_prompt"
        expected_filename = f"{sanitized_prompt}.txt"
        assert thought_files[0].startswith(sanitized_prompt)

        # 3. Assert that a new commit was created
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        # We expect 2 commits: the initial one and the one from store_thought
        assert int(result.stdout.strip()) == 2

        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        assert result.stdout.strip() == f"Add thought for prompt: {prompt}"
