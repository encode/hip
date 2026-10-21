import types
import typing

if typing.TYPE_CHECKING:
    # Once we drop 3.10 support, we can use 'typing.Self'.
    from typing_extensions import Self

from ._body import GZipStream, HTTPStream
from ._content import Content
from ._headers import Headers
from ._network import Lock, NetworkBackend
from ._parsers import HTTPParser
from ._request import Method, Request
from ._response import Response, StatusCode
from ._streams import Stream
from ._urls import URL

__all__ = [
    "Connection",
    "ResponseStream",
    "Transport",
    "open_connection",
]


class ResponseStream(Stream):
    def __init__(
        self, status_code: StatusCode, headers: Headers, stream: Stream
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.stream = stream

    def read(self, size: int = -1) -> bytes:
        return self.stream.read(size)

    def close(self):
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ) -> None:
        self.close()


class Transport:
    def send(self, request: Request) -> ResponseStream:
        raise NotImplementedError()

    def close(self):
        pass

    def request(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> Response:
        request = Request(method, url, headers=headers, content=content)
        with self.send(request) as stream:
            body = stream.read()
        return Response(stream.status_code, headers=stream.headers, content=body)

    def stream(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> ResponseStream:
        request = Request(method, url, headers=headers, content=content)
        return self.send(request)


class Connection(Transport):
    def __init__(self, stream: Stream, origin: URL | str):
        self._stream = stream
        self._origin = URL(origin) if not isinstance(origin, URL) else origin
        self._request_lock = Lock()
        self._parser = HTTPParser(stream, mode="CLIENT")

    # API for connection pool management...
    def origin(self) -> URL:
        return self._origin

    def is_idle(self) -> bool:
        return self._parser.is_idle()

    def is_expired(self) -> bool:
        return self._parser.is_idle() and self._parser.keepalive_expired()

    def is_closed(self) -> bool:
        return self._parser.is_closed()

    def description(self) -> str:
        return self._parser.description()

    # API entry points...
    def send(self, request: Request) -> ResponseStream:
        # async with self._request_lock:
        #    try:
        self._send_head(request)
        self._send_body(request)
        code, headers = self._recv_head()
        stream = self._recv_body(headers)
        return ResponseStream(code, headers, stream)

    def close(self) -> None:
        with self._request_lock:
            self._close()

    # Top-level API for working directly with a connection.
    def request(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> Response:
        url = self._origin.join(url)
        request = Request(method, url, headers=headers, content=content)
        with self.send(request) as stream:
            body = stream.read()
        return Response(stream.status_code, headers=stream.headers, content=body)

    def stream(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> ResponseStream:
        url = self._origin.join(url)
        request = Request(method, url, headers=headers, content=content)
        return self.send(request)

    # Send the request...
    def _send_head(self, request: Request) -> None:
        method = bytes(request.method)
        target = request.url.target.encode("ascii")
        protocol = b"HTTP/1.1"
        self._parser.send_method_line(method, target, protocol)
        headers = request.headers.as_byte_pairs()
        self._parser.send_headers(headers)

    def _send_body(self, request: Request) -> None:
        with request.content.open() as stream:
            while data := stream.read(64 * 1024):
                self._parser.send_body(data)
        self._parser.send_body(b"")

    # Receive the response...
    def _recv_head(self) -> tuple[StatusCode, Headers]:
        _, code, _ = self._parser.recv_status_line()
        h = self._parser.recv_headers()
        status_code = StatusCode(code)
        headers = Headers([(k.decode("ascii"), v.decode("ascii")) for k, v in h])
        return status_code, headers

    def _recv_body(self, headers) -> Stream:
        stream: Stream = HTTPStream(self._parser, is_response=True)
        content_encoding = headers.get("Content-Encoding", "")
        if content_encoding.lower() == "gzip":
            stream = GZipStream(stream)
        return stream

    # Request/response cycle complete...
    def _close(self) -> None:
        self._parser.close()

    # Builtins...
    def __repr__(self) -> str:
        return f"<Connection [{self._origin} {self.description()}]>"

    def __enter__(self) -> "Self":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ):
        self.close()


def open_connection(
    url: URL | str,
    hostname: str = "",
    backend: NetworkBackend | None = None,
) -> Connection:

    if isinstance(url, str):
        url = URL(url)

    if url.scheme not in ("http", "https"):
        raise ValueError("URL scheme must be 'http://' or 'https://'.")
    if backend is None:
        backend = NetworkBackend()

    host = url.host
    port = url.port or {"http": 80, "https": 443}[url.scheme]

    if url.scheme == "https":
        stream = backend.connect_tls(host, port, hostname)
    else:
        stream = backend.connect(host, port)

    return Connection(stream, url)
