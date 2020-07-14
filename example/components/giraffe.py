"""Giraffe component is the API to Giraffe component."""
from typing import Any, Optional

import contextlib
import watchdog.events

from Octavius.lego.components import RPyCComponent


class Giraffe(RPyCComponent):
    """An extended interface for Giraffe component."""

    @contextlib.contextmanager
    def monitor_logs(
            self,
            event_handler: Optional[watchdog.events.FileSystemEventHandler],
            directory: str
    ) -> Any:
        """Monitor specific directory to not change.

        Args:
            event_handler: Event handler that is called with every
                incoming file system event.
            directory: Directory to watch.
        """

        r_observer = self.connection.modules['watchdog.observers'].Observer()
        r_observer.schedule(event_handler, directory)
        r_observer.start()
        try:
            yield r_observer
        finally:
            r_observer.stop()
            r_observer.join()
            if not r_observer.event_queue.empty():
                for event in r_observer.event_queue.get():
                    assert 'log.txt' not in event.src_path
