"""Monitorable component is the base class of each component with monitoring ability."""
from typing import Any, List, Callable, Optional, Dict

import asyncio
import contextlib
import functools
import pathlib
import queue
import scapy.all

from Octavius.lego.libs.tasks import run_as_task
from Octavius.lego.components.base import RPyCComponent

from .helpers.monitor import Monitor, LogsMonitor


class MonitorableRPyCComponent(RPyCComponent):
    """An extended interface for RPyC component with monitoring capabilities."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._received_packets = queue.Queue()
        self._unallowed_packets: List[bytes] = [b'Octavius']

        self._monitors: Dict[str, Monitor] = {
            'log.txt': LogsMonitor(
                self,
                unallowed=['Really bad error'],
                allowed=['Octavius'],
                path=pathlib.Path('/log.txt')
            )
        }

    @property
    def monitors(self) -> Dict[str, Monitor]:
        """Gets all of the monitors."""

        return self._monitors

    def add_monitor(self, name: str, monitor: Monitor) -> None:
        """Adds a new monitor."""

        if name in self.monitors:
            raise KeyError(f'Monitor name already in use (name: {name})')

        self._monitors[name] = monitor

    def remove_monitor(self, name: str) -> None:
        """Removes a monitor."""

        del self._monitors[name]

    @contextlib.contextmanager
    def monitor(self, new_monitors: Dict[str, Monitor] = None):
        """Monitors with all the monitors.

        Args:
            new_monitors: New monitors to add just for this context.
        """

        if new_monitors is None:
            new_monitors = dict()

        for name, monitor in new_monitors:
            self.add_monitor(name, monitor)

        with contextlib.ExitStack() as stack:
            for monitor in list(self.monitors.values()):
                stack.enter_context(self._monitor_task(monitor))
                yield

        for name, _ in new_monitors:
            self.remove_monitor(name)

    @run_as_task
    async def _monitor_task(self, monitor: Monitor) -> Any:
        """Monitor task."""

        monitor.start()
        try:
            while True:
                monitor.loop()
                await asyncio.sleep(1) # Pass control to event loop
        # Task Destruction
        except asyncio.exceptions.CancelledError:
            monitor.loop(final=True)
        finally:
            monitor.end()

    @contextlib.contextmanager
    def sniff_packets(self, *args, **kwargs) -> Any:
        """Sniffs packets by AsyncSniffer and saves them for later monitoring."""

        original_prn = kwargs['prn'] if 'prn' in kwargs.keys() else None
        kwargs['prn'] = functools.partial(self._save_packet_wrapper, original_prn=original_prn)

        r_sniffer = self.connection.modules['scapy.all'].AsyncSniffer(*args, **kwargs)
        r_sniffer.start()

        yield r_sniffer

        r_sniffer.stop()

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
