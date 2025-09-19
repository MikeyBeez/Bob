from typing import NamedTuple, Callable, Coroutine, Any, Optional

class Job(NamedTuple):
    """
    Represents a job to be executed by a worker.

    Attributes:
        job_id: A unique identifier for the job.
        task: The asynchronous function (coroutine) to be executed.
        args: Positional arguments for the task.
        kwargs: Keyword arguments for the task.
    """
    job_id: int
    task: Callable[..., Coroutine]
    args: tuple
    kwargs: dict

class JobResult(NamedTuple):
    """
    Represents the result of a completed job.

    Attributes:
        job_id: The ID of the job this result corresponds to.
        result: The return value of the job's task. Can be None.
        error: An exception object if the job failed, otherwise None.
    """
    job_id: int
    result: Optional[Any] = None
    error: Optional[Exception] = None
