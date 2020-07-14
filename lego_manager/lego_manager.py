"""
Lego manager controls and allocates setup for tests.
Each test requests relevant components from lego manager, and lego manager checks if
there is an available setup and allocates it.
Main features:

    1. Controls the timing of the tests to utilize the setup for maximum usage.
    2. Provides information on the state and statistics of different components in the setup.

The manager runs on a central server.

Note:
     Most of the features mentioned above aren't implemented yet.
"""
from typing import List, Dict, Any, Iterator

import contextlib
import rpyc

_ComponentsToClassPath = Dict[str, str]


class LegoManager(rpyc.Service):
    """
    Setup and tests manager.
    Should manage the permissions for tests to run on setup.
    Stores its database using Rest API.
    """
    # Defining the name of RPyC service.
    ALIASES = ["LegoManager"]
    DEFAULT_PORT = 18861

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Allocation is a dictionary with the components from the setup as keys, and boolean values
        # indicating if they are currently in use, e.g., {'zebra.alice': True, 'zebra.logan': False}
        self._allocations: Dict = dict()
        self._bg_threads: Dict = dict()

    def on_connect(self, conn: rpyc.Connection) -> None:
        """Initializes thread for the incoming connection.

        Args:
            conn: An incoming connection.
        """

        self._bg_threads[conn] = rpyc.BgServingThread(conn)

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        """Stops the connection's thread.

        Args:
            conn: A disconnected connection.
        """

        self._bg_threads.pop(conn).stop()

    @contextlib.contextmanager
    def _allocation(
            self,
            query: str,
            exclusive: bool
    ) -> Iterator[_ComponentsToClassPath]:
        """Manages the components allocations.

        Args:
            query: A query that describes the desired setup.
            exclusive: Whether to lock the required setup.

        Yields:
            Required components.
        """

        del exclusive  # TODO: Add this functionality.

        components = query.split('and')

        self._allocate(components)
        try:
            yield self._get_components_path(query)
        finally:
            self._deallocate(components)

    def _allocate(self, components: List[str]) -> None:
        """Allocates the desired components if available.

        Args:
            components: Desired components.
        """

        for component in components:
            self._allocations[component] = True

    def _deallocate(self, components: List[str]) -> None:
        """Deallocates the desired components.

        Args:
            components: Unneeded components.
        """

        for component in components:
            del self._allocations[component]

    @staticmethod
    def _get_components_path(query: str) -> _ComponentsToClassPath:
        """Maps between components names to the path of their python class objects.

        Args:
            query: A query that describes the desired setup.

        Returns:
            Desired components and the corresponding path to their class objects.
        """

        # TODO: Get this dictionary from Lego's DB/management files.
        components_to_class_path = {
            'zebra': 'Octavius.example.components.zebra.Zebra',
            'giraffe': 'Octavius.example.components.giraffe.Giraffe',
        }

        test_components = (component.strip() for component in query.split('and'))

        return {component: components_to_class_path[component.split('.')[0]]
                for component in test_components}

    @staticmethod
    def _run_query(query: str) -> str:
        """Find available setup according to given query.

        Runs the requested setup query on the setup management files, and add instance names
        to components with unspecified names.
        For example, query given - 'zebra.alice and elephant',
        query returned - 'zebra.alice and elephant.bob'.

        Args:
            query: A query that describes the desired setup.

        Returns:
            Final components query for the test. Each component should be built from
            component class and instance name.
        """
        return query

    def exposed_acquire_setup(self, query: str, exclusive: bool):  # type: ignore
        """Acquired the desired setup if available.

        This function also will store all of the data about the setup usage.

        Args:
            query: A query that describes the desired setup.
            The query syntax is -
                1. The components should be splitted by the word 'and'.
                2. The format should be <component_class>.<instance_name>,
                   or only <component_class> if specific instance isn't needed.
            Example:
                 'zebra.alice and elephant.bob and giraffe.4'.

            exclusive: Whether the required setup is needed exclusively.

        Returns:
            Allocated requested setup as list of tuples made of
            components names and corresponding paths to Components classes.
            e.g. [('zebra.alice', 'Octavius.example.components.zebra.Zebra'), ...]
        """
        return self._allocation(self._run_query(query), exclusive)


def main() -> None:
    """Starts Lego server."""

    rpyc.lib.setup_logger()
    from rpyc.utils.server import ThreadedServer  # pylint: disable=import-outside-toplevel
    # Note: all connection will use the same LegoManager
    lego_server = ThreadedServer(
        LegoManager(),
        port=LegoManager.DEFAULT_PORT,
        protocol_config={'allow_public_attrs': True}
    )
    lego_server.start()


if __name__ == "__main__":
    main()
