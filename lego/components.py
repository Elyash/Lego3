"""
Component object provides the API which tests and libs will use to run code on the component.
"""
from __future__ import annotations
from typing import Optional, Type, TypeVar, Any
from types import TracebackType
import abc
import socket
import ipaddress

import rpyc

from .connections import BaseConnection, RPyCConnection

Component = TypeVar('Component', bound='BaseComponent')


class BaseComponent(metaclass=abc.ABCMeta):
    """
    BaseComponent class is the base class of all other components,
    In order to extend the API implement a wrapping component, and to provide more
    complex functionality add appropriate Lib.
    """

    def __init__(self, connection: BaseConnection, pytest_config: Any) -> None:
        """Initiates the connection to remote machine.

        Args:
            connection: Connection to the component. Every component should initialize it's
                        appropriate connection in __init__ and then pass it to BaseComponent.
            pytest_config: PyTest configruation of the current test.
        """

        self._connection: BaseConnection = connection
        self._pytest_config: Any = pytest_config

    def __enter__(self: Component) -> Component:
        """Allowing the use of 'with' statement with components objects.

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
        self._connection.close()

    def close(self) -> None:
        """Allow subclasses to free resources after finishing tests."""

    @property
    @abc.abstractmethod
    def connection(self) -> BaseConnection:
        """Connection to the component."""

    @property
    def pytest_config(self) -> Any:
        """The PyTest configuration of the current test."""

        return self._pytest_config


class RPyCComponent(BaseComponent):
    """
    Wrapper for RPyC component, a component which we can run python on.
    Provides simple API which is generic for all RPyC connections.
    It has basic functionality which can run cross platform, only assuming we can run
    python on the component.
    """

    _connection: RPyCConnection

    def __init__(
            self,
            hostname: str,
            username: Optional[str] = None,
            password: Optional[str] = None,
            pytest_config: Any = None
    ) -> None:
        """Initiates RPyC connection to SlaveService on remote machine.

        Connect to RPyC SlaveService on remote machine. If the service isn't running, try
        to deploy it with SSHConnection and RPyC zero deploy library.

        Args:
            hostname: Hostname of remote machine.
            username: Username for SSH login (if needed).
            password: Password for SSH login (if needed).
            pytest_config: PyTest configruation of the current test.
        """

        rpyc_connection = RPyCConnection(hostname, username, password)

        super().__init__(rpyc_connection, pytest_config=pytest_config)

    @property
    def connection(self) -> rpyc.Connection:
        """The RPyc connection to component."""

        return self._connection.rpyc

    def getpid(self) -> int:
        """Gets the PID of the service process."""

        return self.connection.modules.os.getpid()

    def get_remote_socket(self, *args: int, **kwargs: int) -> socket.socket:
        """Allocates a socket on remote machine.

        Args:
            args: Positional arguments passed to socket.socket() constructor.
            kwargs: Keyword arguments passed to socket.socket() constructor.
        """

        r_socket = self.connection.modules['socket']
        return r_socket.socket(*args, **kwargs)

    def run_command(self, command: str) -> str:
        """Runs a bash command on the remote machine.

        Args:
            command: The bash command to run.

        Returns:
            The output of the command.
        """

        return self.connection.modules["subprocess"].check_output(command.split())

    def get_ip(self) -> ipaddress.IPv4Address:
        """Gets IP for default route interface of the remote machine."""

        r_socket = self.get_remote_socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't have to be reachable.
            r_socket.connect(('10.255.255.255', 1))
            component_ip = r_socket.getsockname()[0]
        except socket.error:
            # Can't find default route, use localhost interface.
            component_ip = '127.0.0.1'
        finally:
            r_socket.close()

        return ipaddress.ip_address(component_ip)
