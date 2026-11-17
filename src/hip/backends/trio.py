from __future__ import annotations

import ssl
import types
import typing

import trio
import truststore

if typing.TYPE_CHECKING:
    from typing import Self

from .base import AsyncNetworkBackend, AsyncNetworkStream

__all__ = ["TrioBackend", "TrioServer", "TrioStream"]


class TrioStream(AsyncNetworkStream):
    def __init__(self, stream: trio.abc.Stream) -> None:
        self._stream = stream
        self._is_closed = False

    async def read(self, size: int = -1) -> bytes:
        if size == 0:
            raise ValueError("Size must be greater than zero.")
        max_bytes = 64 * 1024 if size < 0 else size
        return bytes(await self._stream.receive_some(max_bytes=max_bytes))

    async def write(self, data: bytes) -> None:
        if not data:
            return
        await self._stream.send_all(data)

    async def aclose(self) -> None:
        if not self._is_closed:
            self._is_closed = True
            with trio.CancelScope(shield=True):
                await self._stream.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        description = " CLOSED" if self._is_closed else ""
        return f"<TrioStream{description}>"


class TrioBackend(AsyncNetworkBackend):
    def __init__(self, ssl_ctx: ssl.SSLContext | None = None) -> None:
        self._ssl_ctx = self.create_default_context() if ssl_ctx is None else ssl_ctx

    def create_default_context(self) -> ssl.SSLContext:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    async def connect(self, host: str, port: int) -> TrioStream:
        stream = await trio.open_tcp_stream(host, port)
        return TrioStream(stream)

    async def connect_tls(self, host: str, port: int, hostname: str = "") -> TrioStream:
        tcp_stream = await trio.open_tcp_stream(host, port)
        stream = trio.SSLStream(
            tcp_stream,
            ssl_context=self._ssl_ctx,
            server_hostname=hostname or host,
            https_compatible=True,
        )
        try:
            await stream.do_handshake()
        except BaseException:
            with trio.CancelScope(shield=True):
                await stream.aclose()
            raise  # We'll want well defined exception semantics here.
        return TrioStream(stream)

    def serve(
        self,
        host: str,
        port: int,
        handler: typing.Callable[[TrioStream], typing.Awaitable[None]],
    ) -> TrioServer:
        return TrioServer(host, port, handler)

    def __repr__(self) -> str:
        return "<TrioBackend>"


class TrioServer:
    def __init__(
        self,
        host: str,
        port: int,
        handler: typing.Callable[[TrioStream], typing.Awaitable[None]],
    ) -> None:
        self.host = host
        self.port = port
        self._handler = handler
        self._listeners: list[trio.SocketListener] = []
        self._nursery_context: typing.Any = None
        self._nursery: typing.Any = None

    async def __aenter__(self) -> Self:
        self._listeners = await trio.open_tcp_listeners(self.port, host=self.host)
        self._nursery_context = trio.open_nursery()
        self._nursery = await self._nursery_context.__aenter__()

        for listener in self._listeners:
            self._nursery.start_soon(
                trio.serve_listeners,
                self._handle_stream,
                [listener],
            )

        if self.port == 0 and self._listeners:
            self.port = self._listeners[0].socket.getsockname()[1]
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ) -> bool | None:
        self._nursery.cancel_scope.cancel()
        try:
            return await self._nursery_context.__aexit__(exc_type, exc_value, traceback)
        finally:
            with trio.CancelScope(shield=True):
                for listener in self._listeners:
                    await listener.aclose()

    async def _handle_stream(self, stream: trio.SocketStream) -> None:
        trio_stream = TrioStream(stream)
        try:
            await self._handler(trio_stream)
        finally:
            await trio_stream.aclose()
