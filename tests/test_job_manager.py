import asyncio
import pytest
from core.job_system.manager import JobManager
from core.intelligence.mock_api_client import MockOllamaApiClient

@pytest.mark.asyncio
async def test_job_manager_with_mock_client():
    """
    Tests that the JobManager can successfully process a job
    using a mock API client.
    """
    job_manager = JobManager(config={}, num_workers=1)
    await job_manager.start()

    mock_client = MockOllamaApiClient()
    prompt = "Hello from the test!"
    messages = [{"role": "user", "content": prompt}]

    job_id = await job_manager.submit_job(mock_client.generate_chat_completion, messages=messages)

    result = await job_manager.result_queue.get()
    job_manager.result_queue.task_done()

    await job_manager.stop()

    assert result.job_id == job_id
    assert result.error is None
    assert result.result == f"Mock response to: {prompt}"
