"""Giraffe component is the API to Giraffe component."""
from typing import Any, TextIO, List, Callable, Optional

import asyncio
import contextlib
import functools
import pathlib
import click
import colored
import scapy.all
import queue

from ..libs import prompt
from Octavius.lego.components import RPyCComponent


class MonitorableRPyCComponent(RPyCComponent):
    """An extended interface for RPyC component with monitoring capabilities."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Logs monitoring class variables
        self._unallowed_logs: List[str] = ['Really bad error']
        self._allowed_logs: List[str] = ['Octavius']
        self._expected_logs: List[str] = list()

        # Packets monitoring class vairables
        self._received_packets: queue.Queue[scapy.all.packet] = queue.Queue()
        self._unallowed_packets: List[bytes] = [b'Octavius']

    @property
    def unallowed_logs(self) -> List[str]:
        """Gets the unallowed logs."""

        return self._unallowed_logs

    @property
    def allowed_logs(self) -> List[str]:
        """Gets the allowed logs."""

        return self._allowed_logs

    @property
    def expected_logs(self) -> List[str]:
        """Gets the expected logs."""

        return self._expected_logs

    @property
    def unallowed_packets(self) -> List[bytes]:
        """Gets the unallowed packets."""

        return self._unallowed_packets

    @contextlib.contextmanager
    def monitor_logs(self, path: pathlib.Path) -> Any:
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

    async def _monitor_logs(self, path: pathlib.Path) -> Any:
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
            self._monitor_change(log_file, final=True)
        finally:
            log_file.close()

    def _monitor_change(self, log_file: TextIO, final: bool = False) -> None:
        """Monitors changes in a file.

        Args:
            log_file: The file to monitor.
            final: Whether this is the final monitoring before exit.
        """

        for new_log_line in log_file:
            if new_log_line:
                self.monitor_log_line(new_log_line)

        if final:
            assert not self.expected_logs

    def monitor_log_line(self, log_line: str) -> None:
        """Monitors one line from the log.

        Override this method to parse the logs line in a different way.

        Args:
            log_line: The new log line.
        """

        for unallowed_log in self.unallowed_logs:
            assert unallowed_log not in log_line

        for expected_log in self.expected_logs:
            if expected_log in log_line:
                self.expected_logs.remove(expected_log)

        for allowed_log in self.allowed_logs:
            if allowed_log in log_line:
                self._validate_log_with_user(log_line)

    def _validate_log_with_user(self, log_line: str) -> None:
        """Validates with the user interactively whether a log line is valid.

        Args:
            log_line: The line from the log to validate.
        """

        validation_format = colored.fg('blue') + colored.bg('white')
        log_format = colored.fg('red') + colored.bg('white')

        with prompt.manage_io():
            print(colored.stylize('\nPlease confirm the following log:', validation_format))
            assert click.confirm(colored.stylize(log_line, log_format))

    @contextlib.contextmanager
    def sniff_packets(self, *args, **kwargs) -> Any:
        """Sniffs packets by AsyncSniffer and saves them for later monitoring."""

        original_prn = kwargs['prn'] if 'prn' in kwargs.keys() else None
        kwargs['prn'] = functools.partial(self._save_packet_wrapper, original_prn=original_prn)

        r_sniffer = self.connection.modules['scapy.all'].AsyncSniffer(*args, **kwargs)
        r_sniffer.start()

        yield r_sniffer

        packets = r_sniffer.stop()

    def _save_packet_wrapper(
            self,
            packet: scapy.all.scapy.layers.l2.Ether,
            original_prn: Optional[Callable[[scapy.all.scapy.layers.l2.Ether], Any]] = None
        ) -> None:
        """Saves the packet to received queue and calls the original prn.

        Args:
            packet: The received packet.
            original_prn: The original prn callback.
        """

        self._received_packets.put(packet)

        if original_prn:
            original_prn(packet)

