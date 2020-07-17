"""This module manages the prompt input and output."""
from typing import Any

import contextlib

import pytest_lego


@contextlib.contextmanager
def manage_io() -> Any:
    """Manages input and output with pytest."""

    # Suspend input capture by pytest so user input can be recorded here
    capture_manager = pytest_lego.PYTEST_CONFIG.pluginmanager.getplugin('capturemanager')
    capture_manager.suspend_global_capture(in_=True)

    yield

    # Resume capture after input insertion
    capture_manager.resume_global_capture()
