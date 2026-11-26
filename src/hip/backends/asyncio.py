from __future__ import annotations

import asyncio
import ssl
import types
import typing
from typing import Self

import truststore

from .base import AsyncNetworkBackend, AsyncNetworkStream

__all__ = ["AsyncioBackend", "AsyncioServer", "AsyncioStream"]


class AsyncioStream(AsyncNetworkStream):
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._is_closed = False

    async def read(self, size: int = -1) -> bytes:
        if size == 0:
            raise ValueError("Size must be greater than zero.")
        max_bytes = 64 * 1024 if size < 0 else size
        return await self._reader.read(max_bytes)

    async def write(self, data: bytes) -> None:
        if not data:
            return
        self._writer.write(data)
        await self._writer.drain()

    async def aclose(self) -> None:
        if self._is_closed:
            return  # pragma: no cover
        self._is_closed = True
        self._writer.close()
        try:
            await self._writer.wait_closed()
        except (ConnectionError, OSError):  # pragma: no cover
            pass

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
        return f"<AsyncioStream{description}>"


class AsyncioBackend(AsyncNetworkBackend):
    def __init__(self, ssl_ctx: ssl.SSLContext | None = None) -> None:
        self._ssl_ctx = self.create_default_context() if ssl_ctx is None else ssl_ctx

    def create_default_context(self) -> ssl.SSLContext:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    async def connect(self, host: str, port: int) -> AsyncioStream:
        reader, writer = await asyncio.open_connection(host, port)
        return AsyncioStream(reader, writer)

    async def connect_tls(
        self, host: str, port: int, hostname: str = ""
    ) -> AsyncioStream:
        reader, writer = await asyncio.open_connection(
            host,
            port,
            ssl=self._ssl_ctx,
            server_hostname=hostname or host,
        )
        return AsyncioStream(reader, writer)

    def serve(
        self,
        host: str,
        port: int,
        handler: typing.Callable[[AsyncioStream], typing.Awaitable[None]],
    ) -> AsyncioServer:
        return AsyncioServer(host, port, handler)

    def __repr__(self) -> str:
        return "<AsyncioBackend>"


class AsyncioServer:
    def __init__(
        self,
        host: str,
        port: int,
        handler: typing.Callable[[AsyncioStream], typing.Awaitable[None]],
    ) -> None:
        self.host = host
        self.port = port
        self._handler = handler
        self._server: asyncio.Server | None = None
        self._tasks: set[asyncio.Task[None]] = set()

    async def __aenter__(self) -> Self:
        self._server = await asyncio.start_server(self._accept, self.host, self.port)
        sockets = self._server.sockets
        if self.port == 0 and sockets:
            self.port = int(sockets[0].getsockname()[1])
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ) -> None:
        assert self._server is not None
        self._server.close()
        await self._server.wait_closed()

        tasks = tuple(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)  # pragma: no cover

    def _accept(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        task = asyncio.create_task(self._handle_stream(reader, writer))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _handle_stream(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        stream = AsyncioStream(reader, writer)
        try:
            await self._handler(stream)
        finally:
            await stream.aclose()
