from __future__ import annotations

import contextlib
import signal
import socket
from types import FrameType
from typing import Iterator


class NetworkAccessError(RuntimeError):
    """Raised when submission code attempts network access."""


class TaskTimeoutError(TimeoutError):
    """Raised when a task exceeds its wall-clock budget."""


@contextlib.contextmanager
def block_network() -> Iterator[None]:
    original_socket = socket.socket
    original_create_connection = socket.create_connection

    class GuardedSocket(original_socket):
        def connect(self, *args, **kwargs):  # type: ignore[override]
            self.close()
            raise NetworkAccessError("Network access is disabled during evaluation.")

        def connect_ex(self, *args, **kwargs):  # type: ignore[override]
            self.close()
            raise NetworkAccessError("Network access is disabled during evaluation.")

    def blocked_create_connection(*args, **kwargs):
        raise NetworkAccessError("Network access is disabled during evaluation.")

    socket.socket = GuardedSocket  # type: ignore[assignment]
    socket.create_connection = blocked_create_connection  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket = original_socket  # type: ignore[assignment]
        socket.create_connection = original_create_connection  # type: ignore[assignment]


@contextlib.contextmanager
def time_limit(seconds: float) -> Iterator[None]:
    if not hasattr(signal, "setitimer"):
        yield
        return

    def handle_timeout(signum: int, frame: FrameType | None) -> None:
        raise TaskTimeoutError(f"Task exceeded {seconds} seconds.")

    previous_handler = signal.signal(signal.SIGALRM, handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, max(seconds, 0.001))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_handler)
