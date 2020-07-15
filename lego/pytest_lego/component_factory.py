"""
Supply components to the plugin by acquiring them in the lego manager,
then getting their arguments from pytest configuration (pytest.ini file).
"""
from typing import List, Any, Type, Iterator

import contextlib
import importlib
import rpyc

from Octavius.lego.components import BaseComponent


def _get_component_class(component_path: str) -> Type[BaseComponent]:
    """Gets the requested component's class object.

    Args:
        component_path: The path to the requested component class.
                        For example, Octavius.example.components.zebra.Zebra

    Returns:
        The component's class object.
    """

    *module, component_class = component_path.split('.')
    return getattr(importlib.import_module('.'.join(module)), component_class)


def _get_component(component_name: str, component_path: str, pytest_config: Any) -> BaseComponent:
    """Initialize the component object.

    Args:
        component_name: The component name in pytest config file (usually, pytest.ini file).
        component_path: The path to the requested component class.
        pytest_config: A PyTest configuration object associated with current test.

    Returns:
        Component object.
    """
    try:
        # A dictionary with all the arguments the component should receive in __init__.
        component_config = pytest_config.inicfg.config.sections[component_name]
    except KeyError:
        raise KeyError(f"{component_name} missing in pytest's configuration file.")

    component_class = _get_component_class(component_path)
    return component_class(**component_config, pytest_config=pytest_config)


@contextlib.contextmanager
def acquire_components(
        lego_manager: rpyc.Connection,
        pytest_config: Any,
        query: str,
        exclusive: bool = True
) -> Iterator[List[BaseComponent]]:
    """Creates components based on the requested setup.

    Args:
        lego_manager: A lego manager instance.
        pytest_config: A PyTest configuration object associated with current test.
        query: A query that describes the requested setup.
        exclusive (optional): Whether to lock the requested setup. Defaults to True.

    Yields:
        The requested components.
    """

    with lego_manager.root.acquire_setup(query, exclusive) as available_components:
        with contextlib.ExitStack() as stack:
            components = []
            for component_name, component_path in available_components.items():
                component = _get_component(component_name, component_path, pytest_config)
                components.append(stack.enter_context(component))
            yield components
