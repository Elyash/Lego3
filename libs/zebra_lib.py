"""Zebra lib is API to elephant component."""

import random
import asyncio

import libs.core_lib


class ZebraLib(libs.core_lib.CoreLib):
    """An extended library for Zebra component."""

    async def send_and_receive(self, dst_ip: str, dst_port: int, count: int = 5):
        """Sends packets and receive them back.

        Args:
            dst_ip: The IP to send to and receive from.
            dst_port: The port to send to and receive from.
            count: The number of packets to send.
        """

        src_port = random.randint(10000, 20000)
        packet = (
            self.connection.modules['scapy.all'].IP(dst=dst_ip) /
            self.connection.modules['scapy.all'].UDP(sport=src_port, dport=dst_port)/
            'Lego3 is great'
        )
        r_send = self.connection.modules['scapy.all'].send
        r_sniffer = self.connection.modules['scapy.all'].AsyncSniffer(
            filter=f'udp and src port {dst_port} and dst port {src_port}', count=count)

        r_sniffer.start()
        r_send(packet, count=count)
        await asyncio.sleep(3)
        packets = r_sniffer.stop()
        assert len(packets) == count
