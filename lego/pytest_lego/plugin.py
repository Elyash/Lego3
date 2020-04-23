# type: ignore
# pylint: skip-file
"""
Implementation of the pytest-lego plugin.
"""
from typing import Any, List
import contextlib
import functools

import pytest
import rpyc

from . import component_factory
from lego.components import BaseComponent

LEGO_MARK = 'lego'


@pytest.fixture(scope='session')
def lego_manager(request) -> rpyc.Connection:
    """Provides the connection to the lego manager.

    Args:
        request: A PyTest fixture helper, with information on the requesting test function.

    Returns:
        RPyC connection to LegoManager service.
    """

    assert LEGO_MARK in request.config.inicfg.config.sections, f'Missing {LEGO_MARK} section in inifile'

    try:
        manager_hostname = request.config.inicfg.config.sections[LEGO_MARK]['lego_manager_hostname']
        manager_port = request.config.inicfg.config.sections[LEGO_MARK]['lego_manager_port']
    except KeyError as e:
        missing_key = e.args[0]
        raise KeyError(f'Missing {missing_key} under {LEGO_MARK} section in inifile')

    lego_manager = rpyc.connect(manager_hostname, manager_port)
    request.addfinalizer(lego_manager.close)

    return lego_manager


@contextlib.contextmanager
def get_components(request, lego_manager) -> List[BaseComponent]:
    """Provides the components requested in corresponding lego mark for the test.

    This fixture provides the components requested by the test function.
    To provide arguments to the components, one should define [component] section in pytest config file.

    Typical usage example:

    @pytest.mark.lego('zebra.alice and elephant.bob')
    def test_default_sizes(self, components):
        zebra, elephant, *_ = components
        assert zebra.size == elephant.size

    Example for configuration in pytest.ini:
    [zebra.alice]
    hostname = zebra
    username = admin
    password = password
    [elephant.bob]
    hostname=192.168.100.11
    name = Bob
    size = 120

    Args:
        request: A PyTest fixture helper, with information on the requesting test function.
        lego_manager: An RPyC connection to LegoManager service.

    Returns:
        List of components requested in lego.mark.
    """
    lego_mark = request.node.get_closest_marker(LEGO_MARK)
    if lego_mark is None:
        # The test doesn't have the 'lego' mark.
        yield None
        # There is no resources to free.
        return

    with component_factory.acquire_components(
            lego_manager,
            request.config,
            *lego_mark.args,
            **lego_mark.kwargs
    ) as components:
        yield components


@pytest.fixture(scope='function')
def components_func(request, lego_manager) -> List[BaseComponent]:
    """Provides the components get_components fixture with scope=function.

    Args:
        request: A PyTest fixture helper, with information on the requesting test function.
        lego_manager: An RPyC connection to LegoManager service.

    Returns:
        List of components requested in lego.mark.
    """
    with get_components(request, lego_manager) as components:
        yield components


@pytest.fixture(scope='class')
def components_cls(request, lego_manager) -> List[BaseComponent]:
    """Provides the components get_components fixture with scope=class.

    Args:
        request: A PyTest fixture helper, with information on the requesting test function.
        lego_manager: An RPyC connection to LegoManager service.

    Returns:
        List of components requested in lego.mark.
    """
    with get_components(request, lego_manager) as components:
        yield components


def pytest_configure(config: Any) -> None:
    """Adds the lego mark.

    Args:
        config: A PyTest configuration object.
    """

    config.addinivalue_line(
        'markers',
        f'{LEGO_MARK}: Lego mark used in order to supply components by query'
    )


@pytest.mark.tryfirst
def pytest_fixture_setup(fixturedef, request):
    """Adds the ability to add lego marks to `setup_class` functions in test classes."""

    if fixturedef.argname != '_Class__pytest_setup_class':
        return

    test_class = request.cls
    marks = getattr(test_class.setup_class, 'pytestmark', None)
    if marks is None:
        return

    try:
        lego_mark = next(mark for mark in marks if LEGO_MARK == mark.name)
    except StopIteration:
        # The function doesn't have the 'lego' mark.
        return

    @functools.wraps(fixturedef.func)
    def setup_class_wrapper(*args, **kwargs):
        lego_manager = request.getfixturevalue('lego_manager')
        with component_factory.acquire_components(
                lego_manager,
                request.config,
                *lego_mark.args,
                **lego_mark.kwargs
        ) as wrapped_connections:
            test_class.setup_class(wrapped_connections, *args, **kwargs)
            try:
                yield
            finally:
                teardown_class = getattr(test_class, 'teardown_class', None)
                if teardown_class is not None:
                    teardown_class()

    fixturedef.func = setup_class_wrapper
