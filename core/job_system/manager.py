import asyncio
import logging
from typing import Dict, Any, List

from .models import Job, JobResult

logger = logging.getLogger(__name__)

class JobManager:
    """
    Manages a queue of jobs and processes them asynchronously using workers.
    """
    def __init__(self, config: Dict[str, Any], num_workers: int = 4):
        self.config = config
        self.job_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.num_workers = num_workers
        self._workers: List[asyncio.Task] = []
        self._next_job_id = 0
        self._shutdown = asyncio.Event()

    async def start(self):
        """Starts the worker tasks."""
        if self._workers:
            logger.warning("JobManager already started.")
            return

        logger.info(f"Starting {self.num_workers} worker(s)...")
        self._shutdown.clear()
        self._workers = [
            asyncio.create_task(self._worker(i)) for i in range(self.num_workers)
        ]
        logger.info("JobManager started successfully.")

    async def stop(self):
        """Stops the worker tasks gracefully."""
        if not self._workers:
            logger.warning("JobManager not running.")
            return

        logger.info("Shutting down JobManager...")
        self._shutdown.set()
        await self.job_queue.join()  # Wait for all jobs to be processed

        for worker in self._workers:
            worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []
        logger.info("JobManager shut down completely.")

    async def _worker(self, worker_id: int):
        """The main logic for a worker task."""
        logger.info(f"Worker {worker_id} started.")
        while not self._shutdown.is_set():
            try:
                job = await self.job_queue.get()
                logger.info(f"Worker {worker_id} picked up job {job.job_id}.")

                try:
                    result = await job.task(*job.args, **job.kwargs)
                    job_result = JobResult(job_id=job.job_id, result=result)
                except Exception as e:
                    logger.error(f"Worker {worker_id} encountered an error processing job {job.job_id}: {e}", exc_info=True)
                    job_result = JobResult(job_id=job.job_id, error=e)

                await self.result_queue.put(job_result)
                self.job_queue.task_done()
                logger.info(f"Worker {worker_id} finished job {job.job_id}.")

            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} received cancellation signal.")
                break

        logger.info(f"Worker {worker_id} shutting down.")

    async def submit_job(self, task: callable, *args, **kwargs) -> int:
        """Submits a new job to the queue and returns the job ID."""
        if self._shutdown.is_set():
            raise RuntimeError("Cannot submit job, JobManager is shutting down.")

        self._next_job_id += 1
        job_id = self._next_job_id
        job = Job(job_id=job_id, task=task, args=args, kwargs=kwargs)
        await self.job_queue.put(job)
        logger.info(f"Submitted job {job_id} for task: {getattr(task, '__name__', 'unknown')}")
        return job_id
