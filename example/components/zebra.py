"""Zebra component is the API to Zebra component."""
import asyncio
import functools
import random
import ipaddress

from Octavius.lego.components.base import RPyCComponent


class Zebra(RPyCComponent):
    """An extended interface for Zebra component."""

    async def send_and_receive(
            self,
            dst_ip: ipaddress.IPv4Address,
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
        payload = '13 Jun 9:31:28 dv-elyash sysint: Octavius is great\n'
        src_port = random.randint(10000, 20000)

        r_scapy = self.connection.modules['scapy.all']
        packet = (
            r_scapy.IP(dst=str(dst_ip)) /
            r_scapy.UDP(sport=src_port, dport=dst_port) /
            r_scapy.Raw(load=payload)
        )

        r_srloop = r_scapy.srloop
        partial_r_srloop = functools.partial(
            r_srloop, packet, filter=f'udp and dst port {src_port}', timeout=1, count=count)

        loop = asyncio.get_running_loop()
        answered, unanswered = await loop.run_in_executor(executor, partial_r_srloop)

        assert len(answered) == count
        assert len(unanswered) == 0
        for i in range(count):
            assert answered[i][received_index].load.decode() == payload
