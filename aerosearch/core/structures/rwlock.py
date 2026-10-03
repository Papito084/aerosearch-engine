"""Fair Reader-Writer Lock (RWLock) implementation for safe concurrent reads and exclusive writes."""

import threading
from collections.abc import Generator
from contextlib import contextmanager


class RWLock:
    """A fair Reader-Writer Lock using threading.Condition.

    Allows concurrent simultaneous reads, but grants exclusive access to writers.
    Writers are prioritized when queued to avoid writer starvation.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._read_ready = threading.Condition(self._lock)
        self._readers: int = 0
        self._writers_waiting: int = 0
        self._writer_active: bool = False

    def acquire_read(self) -> None:
        """Acquire a shared read lock."""
        with self._lock:
            while self._writer_active or self._writers_waiting > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self) -> None:
        """Release a shared read lock."""
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self) -> None:
        """Acquire an exclusive write lock."""
        with self._lock:
            self._writers_waiting += 1
            while self._readers > 0 or self._writer_active:
                self._read_ready.wait()
            self._writers_waiting -= 1
            self._writer_active = True

    def release_write(self) -> None:
        """Release an exclusive write lock."""
        with self._lock:
            self._writer_active = False
            self._read_ready.notify_all()

    @contextmanager
    def read_lock(self) -> Generator[None, None, None]:
        """Context manager for shared read lock."""
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self) -> Generator[None, None, None]:
        """Context manager for exclusive write lock."""
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
