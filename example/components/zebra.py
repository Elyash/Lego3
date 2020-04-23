"""Zebra component is the API to Zebra component."""
# TODO: add to docstring what is a zebra component?

import asyncio
import functools
import random

from lego.components import RPyCComponent
from lego.connections import RPyCConnection


class Zebra(RPyCComponent):
    """An extended interface for Zebra component."""

    def __init__(self, hostname, username: str, password: str) -> None:
        """Initialize RPyC connection over SSH.

        Args:
            hostname: Hostname of the component.
            username: Username for SSH login.
            password: Password for SSH login.
        """
        super().__init__(RPyCConnection(hostname, username, password))

        self._rpyc_conn = self.connection.rpyc_connection

    async def send_and_receive(
            self,
            dst_ip: str,
            dst_port: int,
            count: int = 5
    ) -> None:
        """Sends packets and receive them back.

        Args:
            dst_ip: The IP to send to and receive from.
            dst_port: The port to send to and receive from.
            count (optional): The number of packets to send. Defaults to 5.
        """

        executor = None
        received_index = 1
        payload = 'Lego3 is great'
        src_port = random.randint(10000, 20000)

        packet = (
            self._rpyc_conn.modules['scapy.all'].IP(dst=dst_ip) /
            self._rpyc_conn.modules['scapy.all'].UDP(sport=src_port, dport=dst_port)/
            self._rpyc_conn.modules['scapy.all'].Raw(load=payload)
        )

        r_srloop = self._rpyc_conn.modules['scapy.all'].srloop
        partial_r_srloop = functools.partial(
            r_srloop, packet, filter=f'udp and dst port {src_port}', timeout=1, count=count)

        loop = asyncio.get_running_loop()
        answered, unanswered = await loop.run_in_executor(executor, partial_r_srloop)

        assert len(answered) == count
        assert len(unanswered) == 0
        for i in range(count):
            assert answered[i][received_index].load.decode() == payload
