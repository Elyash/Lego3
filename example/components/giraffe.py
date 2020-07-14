"""Giraffe component is the API to Giraffe component."""
from typing import Any, Optional, TextIO

import asyncio
import contextlib
import time
import os

from .linux import LinuxRPyCComponent


class Giraffe(LinuxRPyCComponent):
    """An extended interface for Giraffe component."""

    pass
