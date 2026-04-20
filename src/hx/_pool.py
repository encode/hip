import time
import typing
import types

from ._connection import Connection, Transport, open_connection
from ._network import NetworkBackend, Semaphore
from ._response import Response
from ._request import Request
from ._urls import URL


__all__ = [
    "ConnectionPool",
]


class ConnectionPool(Transport):
    def __init__(self, backend: NetworkBackend | None = None):
        if backend is None:
            backend = NetworkBackend()

        self._connections: list[Connection] = []
        self._network_backend = backend
        self._limit_concurrency = Semaphore(100)
        self._closed = False

    # Public API...
    def send(self, request: Request) -> Response:
        if self._closed:
            raise RuntimeError("ConnectionPool is closed.")

        # TODO: concurrency limiting
        self._cleanup()
        connection = self._get_connection(request)
        response = connection.send(request)
        return response

    def close(self):
        self._closed = True
        closing = list(self._connections)
        self._connections = []
        for conn in closing:
            conn.close()

    # Create or reuse connections as required...
    def _get_connection(self, request: Request) -> "Connection":
        # Attempt to reuse an existing connection.
        url = request.url
        origin = URL(scheme=url.scheme, host=url.host, port=url.port)
        for conn in self._connections:
            if conn.origin() == origin and conn.is_idle() and not conn.is_expired():
                return conn

        # Or else create a new connection.
        conn = open_connection(
            origin,
            hostname=request.headers["Host"],
            backend=self._network_backend
        )
        self._connections.append(conn)
        return conn

    # Connection pool management...
    def _cleanup(self) -> None:
        now = time.monotonic()
        for conn in list(self._connections):
            if conn.is_expired():
                conn.close()
            if conn.is_closed():
                self._connections.remove(conn)

    @property
    def connections(self) -> typing.List['Connection']:
        return [c for c in self._connections]

    def description(self) -> str:
        counts = {"active": 0}
        for status in [c.description() for c in self._connections]:
            counts[status] = counts.get(status, 0) + 1
        return ", ".join(f"{count} {status}" for status, count in counts.items())

    # Builtins...
    def __repr__(self) -> str:
        return f"<ConnectionPool [{self.description()}]>"

    def __del__(self):
        if not self._closed:
            import warnings
            warnings.warn("ConnectionPool was garbage collected without being closed.")

    def __enter__(self) -> "ConnectionPool":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ) -> None:
        self.close()
