import types
import typing

if typing.TYPE_CHECKING:
    # Once we drop 3.10 support, we can use 'typing.Self'.
    from typing_extensions import Self

from .._body import GZipStream, HTTPStream
from .._content import Content
from .._headers import Headers
from .._parsers import HTTPParser
from .._request import Method, Request
from .._response import Response, StatusCode
from .._streams import Stream
from .._urls import URL
from ..backends.asyncio import Lock, NetworkBackend
from .base import SendContext, Transport

__all__ = ["Connection", "open_connection"]


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
    async def send(self, request: Request) -> SendContext:
        # async with self._request_lock:
        #    try:
        await self._send_head(request)
        await self._send_body(request)
        code, headers = await self._recv_head()
        stream = await self._recv_body(headers)
        return SendContext((code, headers, stream))

    async def close(self) -> None:
        async with self._request_lock:
            await self._parser.close()

    # Top-level API for working directly with a connection.
    async def request(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> Response:
        url = self._origin.join(url)
        request = Request(method, url, headers=headers, content=content)
        async with await self.send(request) as (status_code, resp_headers, stream):
            body = stream.read()
        return Response(status_code, headers=resp_headers, content=body)

    # Send the request...
    async def _send_head(self, request: Request) -> None:
        method = bytes(request.method)
        target = request.url.target.encode("ascii")
        protocol = b"HTTP/1.1"
        await self._parser.send_method_line(method, target, protocol)
        headers = request.headers.as_byte_pairs()
        await self._parser.send_headers(headers)

    async def _send_body(self, request: Request) -> None:
        async with await request.content.open() as stream:
            while data := await stream.read(64 * 1024):
                await self._parser.send_body(data)
        await self._parser.send_body(b"")

    # Receive the response...
    async def _recv_head(self) -> tuple[StatusCode, Headers]:
        _, code, _ = await self._parser.recv_status_line()
        h = await self._parser.recv_headers()
        status_code = StatusCode(code)
        headers = Headers([(k.decode("ascii"), v.decode("ascii")) for k, v in h])
        return status_code, headers

    async def _recv_body(self, headers) -> Stream:
        stream: Stream = HTTPStream(self._parser, is_response=True)
        content_encoding = headers.get("Content-Encoding", "")
        if content_encoding.lower() == "gzip":
            stream = GZipStream(stream)
        return stream

    # Builtins...
    def __repr__(self) -> str:
        return f"<Connection [{self._origin} {self.description()}]>"

    async def __aenter__(self) -> "Self":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ):
        await self.close()


async def open_connection(
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
        stream = await backend.connect_tls(host, port, hostname)
    else:
        stream = await backend.connect(host, port)

    return Connection(stream, url)
