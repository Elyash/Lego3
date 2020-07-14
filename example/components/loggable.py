"""Giraffe component is the API to Giraffe component."""
from typing import Any, Optional, TextIO, List, NamedTuple

import asyncio
import contextlib
import time
import os

from Octavius.lego.components import RPyCComponent


class LogLine(NamedTuple):
    time: time.struct_time
    server: str
    task: str
    message: str


UNALLOWED_LOG = LogLine(None, None, None, 'Octavius')


class LoggableRPyCComponent(RPyCComponent):
    """An extended interface for RPyC component with logs monitoring funcitonality."""

    def __init__(self, *args, **kwargs):
        """Initializes a loggable RPyC component."""

        super().__init__(*args, **kwargs)

        self._unallowed_logs: List[LogLine] = [UNALLOWED_LOG]
        self._allowed_logs: List[LogLine] = list()
        self._expected_logs: List[LogLine] = list()

    @property
    def unallowed_logs(self) -> List[LogLine]:
        """Gets the unallowed logs."""

        return self._unallowed_logs

    @property
    def allowed_logs(self) -> List[LogLine]:
        """Gets the allowed logs."""

        return self._unallowed_logs

    @property
    def expected_logs(self) -> List[LogLine]:
        """Gets the expected logs."""

        return self._unallowed_logs

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
        log_file = self.connection.builtin.open(path, 'r')

        log_file.seek(0, self.connection.modules.os.SEEK_END)

        # Task Loop
        try:
            while True:
                self._monitor_change(log_file)
                await asyncio.sleep(1) # Pass control to event loop
        # Task Destruction
        except asyncio.exceptions.CancelledError:
            self._monitor_change(log_file)
        finally:
            log_file.close()

    def _monitor_change(self, log_file: TextIO) -> None:
        """Monitors on changes in a file.

        Args:
            log_file: The file to monitor on
        """

        for new_log_line in log_file.read().split('\n'):
            self._monitor_log_line(new_log_line)

    def _monitor_log_line(self, log_line: str):
        """Parses a new log line.

        Args:
            log_line: The new log line.
        """

        try:
            month, day, clock, server, task, *message = log_line.split()

            _time = time.strptime(month + day + clock, '%d%b%H:%M:%S')
            message = ' '.join(message)

            log_line = LogLine(_time, server, task, message)

            for unallowed_log in self.unallowed_logs:
                assert unallowed_log.message not in log_line.message
        except ValueError:
            if not log_line:
                pass
            else:
                raise

