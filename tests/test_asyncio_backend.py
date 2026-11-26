import asyncio
from unittest.mock import AsyncMock

import pytest

from hip.backends.asyncio import AsyncioBackend, AsyncioStream


def test_connect_serve_context_managers():
    async def send_hello(stream):
        await stream.write(b"hello")

    async def run():
        backend = AsyncioBackend()
        assert repr(backend) == "<AsyncioBackend>"

        async with backend.serve("127.0.0.1", 0, send_hello) as server:
            stream = await backend.connect(server.host, server.port)

            async with stream:
                with pytest.raises(ValueError, match="Size must be greater than zero"):
                    await stream.read(0)

                received = b""
                while chunk := await stream.read():
                    received += chunk
                assert received == b"hello"

            assert "CLOSED" in repr(stream)

    asyncio.run(run())


def test_write_empty():
    async def run():
        reader = AsyncMock()
        writer = AsyncMock()
        stream = AsyncioStream(reader, writer)

        await stream.write(b"")

        writer.write.assert_not_called()
        writer.drain.assert_not_awaited()

    asyncio.run(run())
