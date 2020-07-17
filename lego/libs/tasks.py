"""TODO: Add doc and typing"""
from typing import Any, Callable

import asyncio
import contextlib
import functools

def run_as_task(func: Callable) -> Any:
    """Runs a function as an AsyncIO task.

    Args:
     func: The function to run as task.

     Returns:
        A context manager to start and end the task.
    """

    @functools.wraps(func)
    @contextlib.contextmanager
    def wrapper(*args, **kwargs):
        task = asyncio.create_task(func(*args, **kwargs))
        yield
        try:
            task.result() # Raises the task exceptions
        except asyncio.exceptions.InvalidStateError:
            pass
        finally:
            task.cancel()
    return wrapper
