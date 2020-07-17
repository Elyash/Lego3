"""Monitorable component is the base class of each component with monitoring ability."""
from typing import Any, TextIO, List, Callable, Optional

import pathlib
import rpyc

from Octavius.lego.components.base import RPyCComponent

from Octavius.lego.libs.prompt import validate_with_user


class Monitor:
    """Monitor on component."""

    def __init__(
            self,
            component: RPyCComponent,
            allowed: Optional[List[Any]] = None,
            expected: Optional[List[Any]] = None,
            unallowed: Optional[List[Any]] = None
        ) -> None:

        init_default_list: Callable[[str], List[Any]] = (
            lambda l: list() if l is None else l
        )

        self._component: RPyCComponent = component

        self._allowed: List[Any] = init_default_list(allowed)
        self._expected: List[Any] = init_default_list(expected)
        self._unallowed: List[Any] = init_default_list(unallowed)

    @property
    def component(self) -> RPyCComponent:
        """Gets the monitored component."""

        return self._component

    @property
    def connection(self) -> rpyc.Connection:
        """Gets the connection to the monitored component."""

        return self._component.connection

    @property
    def allowed(self) -> List[Any]:
        """Gets the allowed list."""

        return self._allowed

    @property
    def expected(self) -> List[Any]:
        """Gets the expected list."""

        return self._expected

    @property
    def unallowed(self) -> List[Any]:
        """Gets the unallowed list."""

        return self._unallowed

    def monitor_element(self, element: Any) -> None:
        """Monitors an accpeted element.

        Override this method monitor the element in a different way.

        Args:
            element: The new accepted element.
        """

        for unallowed_element in self.unallowed:
            assert unallowed_element not in element

        for expected_element in self.expected:
            if expected_element in element:
                self.expected.remove(expected_element)

        for allowed_element in self.allowed:
            if allowed_element in element:
                validate_with_user(element)

    def start(self) -> None:
        """Starts the monitor."""

        raise NotImplementedError()

    def loop(self, final: bool = False) -> None:
        """The monitor loop.

        Args:
            final: Whether this is the last time loop called.
        """

        raise NotImplementedError()

    def end(self) -> None:
        """The monitor end."""

        raise NotImplementedError()


class LogsMonitor(Monitor):
    """Monitor a log on component."""

    def __init__(self, *args, path: pathlib.Path, **kwargs):
        super().__init__(*args, **kwargs)

        self._path: pathlib.Path = path
        self._log_file: Optional[TextIO] = None

    @property
    def path(self) -> pathlib.Path:
        """Gets the monitored log path."""

        return self._path

    @property
    def log_file(self) -> TextIO:
        """Gets the log file."""

        return self._log_file

    def start(self) -> None:
        """Starts the log monitoring.

        Args:
            path: The file to monitor.
        """

        self._log_file = self.connection.builtin.open(self.path, 'r')

        self.log_file.seek(0, self.connection.modules.os.SEEK_END)

    def loop(self, final: bool = False) -> None:

        for new_log_line in self.log_file:
            if new_log_line:
                self.monitor_element(new_log_line)

        if final:
            assert not self.expected

    def end(self) -> None:
        self.log_file.close()
