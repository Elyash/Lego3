"""Giraffe component is the API to Giraffe component."""
from typing import Any, TextIO, List

import asyncio
import contextlib
import click
import colored

from Octavius.lego.components import RPyCComponent


class LinuxRPyCComponent(RPyCComponent):
    """An extended interface for RPyC component from linux type."""

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a linux RPyC component."""

        super().__init__(*args, **kwargs)

        self._unallowed_logs: List[str] = list()
        self._allowed_logs: List[str] = list()
        self._expected_logs: List[str] = list()

    @property
    def unallowed_logs(self) -> List[str]:
        """Gets the unallowed logs."""

        return self._unallowed_logs

    @property
    def allowed_logs(self) -> List[str]:
        """Gets the allowed logs."""

        return self._unallowed_logs

    @property
    def expected_logs(self) -> List[str]:
        """Gets the expected logs."""

        return self._unallowed_logs

    @contextlib.contextmanager
    def monitor_logs(self, path: str) -> Any:
        """Monitors a file on the remote machine.

        Args:
            path: The file to monitor.
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
        """Monitors a file on the remote machine.

        This is an asyncio task.

        Args:
            path: The file to monitor.
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
            if new_log_line:
                self._monitor_log_line(new_log_line)

    def _monitor_log_line(self, log_line: str) -> None:
        """Parses a new log line.

        Args:
            log_line: The new log line.
        """

        self._validate_log_with_user(log_line)

    def _validate_log_with_user(self, log_line: str) -> None:
        """Validates with the user interactively whether a log line is valid.

        Args:
            log_line: The line from the log to validate.
        """

        validation_format = colored.fg('blue') + colored.bg('white')
        log_format = colored.fg('red') + colored.bg('white')

        with self.manage_io():
            print(colored.stylize('\nPlease confirm the following log:', validation_format))
            assert click.confirm(colored.stylize(log_line, log_format))

    @contextlib.contextmanager
    def manage_io(self) -> Any:
        """Asks the user for input.

        Args:
            message: The message to print.
        """

        # Suspend input capture by pytest so user input can be recorded here
        capture_manager = self.pytest_config.pluginmanager.getplugin('capturemanager')
        capture_manager.suspend_global_capture(in_=True)

        yield

        # resume capture after question have been asked
        capture_manager.resume_global_capture()
