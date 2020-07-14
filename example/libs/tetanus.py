"""
Tetanus is a top secret echo server. It listens for UDP packets in a given port and
then it sends them back.
This module is a library for Tetanus functionality.
"""
import subprocess

from Octavius.example.components.giraffe import Giraffe

# Final version of Tetanus.
TOOL = 'ncat -l {} --keep-open --udp --exec "/bin/cat"'
# This version caused unwanted logs to be written.
BUGGY_LOGS_TOOL = TOOL + ' --output log.txt'
# This version didn't send the received data back.
BUGGY_SEND_TOOL = 'ncat -l {} --keep-open --udp --exec "/bin/echo lego"'

VERSION_TO_TOOL = {
    1: BUGGY_SEND_TOOL,
    2: BUGGY_LOGS_TOOL,
    3: TOOL
}


class Tetanus:
    """Library for Tetanus functionality."""

    def __init__(self) -> None:
        self._tool_process: subprocess.Popen

    def install(
            self,
            giraffe: Giraffe,
            version: int,
            port: int
    ) -> None:
        """Installs an echo server.

        Args:
            giraffe: Component API to install on.
            version: Version of the tool.
            port: Port to echo on.
        """

        r_popen = giraffe.connection.modules['subprocess'].Popen
        tool = VERSION_TO_TOOL[version]
        self._tool_process = r_popen(
            tool.format(port),
            shell=True,
            preexec_fn=giraffe.connection.modules.os.setsid)

    def uninstall(self, giraffe: Giraffe) -> None:
        """Uninstall the echo server.

        Args:
            giraffe: Component API to uninstall tool.
        """
        pgrp = giraffe.connection.modules.os.getpgid(self._tool_process.pid)
        giraffe.connection.modules.os.killpg(
            pgrp, giraffe.connection.modules.signal.SIGINT)
