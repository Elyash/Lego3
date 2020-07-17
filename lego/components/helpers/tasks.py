"""TODO: Add doc and typing"""
from typing import Any, TextIO, List, Callable, Optional

import asyncio
import contextlib
import functools

def run_as_task(func):
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
