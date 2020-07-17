"""
Connections provides the connection to the components. A connection should provide simple
functionality to the component, such as running a shell command or upload a file.
Each connection should be based on different protocol, e.g. SSH or telnet.
"""
from __future__ import annotations
from typing import Optional, Type, TypeVar
from types import TracebackType
import abc

import plumbum
import rpyc
from rpyc.utils.zerodeploy import DeployedServer

Connection = TypeVar('Connection', bound='BaseConnection')


class BaseConnection(metaclass=abc.ABCMeta):
    """
    BaseConnection class is the base class of every connection to any type of components.
    A connection should provide simple API to communicate and control the component.
    """

    def __enter__(self: Connection) -> Connection:
        """Allowing the use of 'with' statement with connections objects.

        Returns:
            Created class instance.
        """

        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]) -> None:
        """Closes the connection at the exit from the context manager.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            traceback: Exception traceback.
        """
        self.close()

    @abc.abstractmethod
    def close(self) -> None:
        """Closes all connections."""


class SSHConnection(BaseConnection):
    """SSH connection for remote machine.

    This connection provides a shell, that can be used to run shell commands and upload or
    download files.

    Usage example:
    connection = SSHConnection('zebra', 'admin', 'root')
    remote_shell = connection.shell
    r_ls = shell["ls"]
    remote_files = r_ls()

    For more details on how to use plumbum.SshMachine see:
    https://plumbum.readthedocs.io/en/latest/#user-guide
    """

    def __init__(self, hostname: str, username: str, password: str) -> None:
        """Initiates SSH connection.

        Args:
            hostname: The hostname of the component we want to connect to.
            username: Username for SSH connection.
            password: Password for SSH connection.
        """

        # TODO: Check if Paramkio machine can be used with rpyc.DeployedServer.
        #       SshMachine uses an ssh connection for every command, and paramkio use only
        #       one connection.
        self._machine = plumbum.SshMachine(hostname, user=username, password=password)

    @property
    def shell(self) -> plumbum.SshMachine:
        """The SSH connection to component."""

        return self._machine

    def close(self) -> None:
        """Closes all SSH connections."""

        self._machine.close()


class RPyCConnection(BaseConnection):
    """RPyC wrapper for component connection.

    In case the machine doesn't already run SlaveService, we will try to use SSH to upload and
    deploy RPyC SlaveService.
    """

    def __init__(
            self,
            hostname: str,
            username: Optional[str] = None,
            password: Optional[str] = None
    ) -> None:
        """Connects (or start with SSH if needed) to RPyC remote SlaveService.

        Connect to RPyC SlaveService on remote machine. If the service isn't running, try
        to deploy it with SSHConnection and RPyC zero deploy library.

        Args:
            hostname: The hostname of the component we want to connect to.
            username: Username for SSH login (if needed).
            password: Password for SSH login (if needed).
        """

        self._server = None
        try:
            # Checks if the machine already runs RPyC SlaveService.
            self._connection = rpyc.classic.connect(hostname, keepalive=True)
        except ConnectionRefusedError:
            if username is None or password is None:
                # Not given necessary SSH credentials.
                raise

            with SSHConnection(hostname, username, password) as ssh:
                # Upload RPyC and start SlaveService in a temporarily directory.
                self._server = DeployedServer(ssh.shell)  # pylint: disable=no-member
                self._connection = self._server.classic_connect()

    @property
    def rpyc(self) -> rpyc.Connection:
        """The RPyc connection to component."""

        return self._connection

    def close(self) -> None:
        """Closes RPyC connections."""

        self._connection.close()
        if self._server is not None:
            self._server.close()

# TODO: Add telnet connection that will support RPyC.
