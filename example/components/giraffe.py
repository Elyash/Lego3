"""Giraffe component is the API to Giraffe component."""
from typing import Any, Optional

import asyncio
import contextlib
import os

from Octavius.lego.components import RPyCComponent


class Giraffe(RPyCComponent):
    """An extended interface for Giraffe component."""

    @contextlib.contextmanager
    def monitor_logs(self, path: str) -> Any:
        """Monitors on file or directory in this remove machine.

        Args:
            path: The file or directory to monitor.
        """

        monitoring = asyncio.create_task(self._monitor_logs(path))
        yield
        try:
            monitoring.result() # Raises the task exceptions
        except asyncio.exceptions.InvalidStateError:
            pass
        finally:
            monitoring.cancel()

    async def _monitor_logs(self, path: str) -> Any:
        """Monitors on file or directory in this remove machine.

        This is an asyncio task.

        Args:
            path: The file or directory to monitor.
        """

        # Task Initialization
        r_os = self.connection.modules.os
        last_stat = r_os.stat(path)
        log_file = self.connection.builtin.open(path, 'r')
        last_parsed_point = log_file.seek(0, r_os.SEEK_END)

        # Task Loop
        try:
            while True:
                new_stat = r_os.stat(path)
                if last_stat != new_stat:
                    for new_log_line in log_file.read().split('\n'):
                        self._parse_log_line(new_log_line)
                    last_stat = new_stat
                await asyncio.sleep(0) # Pass control to event loop
        except asyncio.exceptions.CancelledError:
            pass
        finally:
            # Task Destruction
            log_file.close()

    def _parse_log_line(self, log_line: str):
        """Parses a new log line.

        Args:
            log_line: The new log line.
        """

        assert 'error' in log_line

