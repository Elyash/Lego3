"""Tetanus spec tests."""
from typing import List

import asyncio
import pathlib
import pytest

from .components.giraffe import Giraffe
from .libs.tetanus import Tetanus

TEST_VERSION = 3


class TestsSpecGiraffe:
    """A Giraffe spec tests base.

    Args:
        giraffe: Giraffe instance.
    """

    _giraffe: Giraffe = None # type: ignore

    @classmethod
    @pytest.mark.lego('giraffe.bob')
    def setup_class(cls, components: List[Giraffe]) -> None:
        """Initializes the variables once in the start of the spec.

        Args:
            components: Required components.
        """

        cls._giraffe, *_ = components


class TestsSpecTetanus(TestsSpecGiraffe):
    """A Tetanus spec tests.

    Args:
        _tetanus_lib: An instance of the tested library.
        _echo_port: A port to echo on.
    """

    _tetanus_lib: Tetanus
    _echo_port: int

    @pytest.fixture(scope='class', autouse=True)
    def init_tetanus_lib(self) -> None:
        """Initializes tetanus lib, only once, in the start of the test suite."""

        # Can't set instance attributes in fixture with scope='class', only class attributes.
        cls = type(self)
        cls._tetanus_lib = Tetanus()  # pylint: disable=protected-access
        cls._echo_port = 1337  # pylint: disable=protected-access

    @pytest.fixture(scope='function', autouse=True, params=[TEST_VERSION])
    def tetanus(self, request):  # type: ignore
        """Install Tetanus before every test function, and uninstall after test end."""

        tetanus_version = request.param
        # Install Tetanus at the start of each test.
        self._tetanus_lib.install(self._giraffe, tetanus_version, self._echo_port)
        yield
        # Uninstall Tetanus at the end of each test.
        self._tetanus_lib.uninstall(self._giraffe)

    @pytest.mark.lego('zebra.alice')
    async def test_send_and_recv(self, components):  # type: ignore
        """Send packets and expect them back."""

        zebra, *_ = components
        await zebra.send_and_receive(self._giraffe.get_ip(), self._echo_port)

    @pytest.mark.lego('zebra.alice and zebra.logan')
    async def test_multi_send_and_recv(self, components):  # type: ignore
        """Send packets from multiple components and expect them back."""

        tasks = []

        for component in components:
            tasks.append(asyncio.ensure_future(
                component.send_and_receive(self._giraffe.get_ip(), self._echo_port)))

        await asyncio.gather(*tasks)

    @pytest.mark.lego('zebra.alice')
    async def test_monitor_send_and_recv(self, components):  # type: ignore
        """Send packets and expect them back while validating no bad logs written."""

        zebra, *_ = components
        with TestsSpecTetanus._giraffe.monitor():
            await zebra.send_and_receive(self._giraffe.get_ip(), self._echo_port)

    @pytest.mark.lego('zebra.alice and zebra.logan')
    # Example of cool usage of parametrize.
    @pytest.mark.parametrize(
        'tetanus',
        [
            pytest.param(1, marks=pytest.mark.xfail),
            pytest.param(2, marks=pytest.mark.xfail),
            3
        ],
        indirect=True)
    async def test_multi_monitor_send_and_receive(self, components):  # type: ignore
        """Send and receive data from multiple components, while validating no bad logs written."""

        tasks = []

        for component in components:
            tasks.append(asyncio.ensure_future(
                component.send_and_receive(self._giraffe.get_ip(), self._echo_port)))

        with TestsSpecTetanus._giraffe.monitor():
            await asyncio.gather(*tasks)

    @pytest.mark.lego('zebra.alice')
    async def test(self, components):
        with TestsSpecTetanus._giraffe.sniff_packets():
            await asyncio.sleep(5)
