from unittest.mock import AsyncMock

import pytest
import trio

from hip.backends.trio import TrioBackend, TrioStream


def test_connect_serve_context_managers():
    async def send_hello(stream):
        await stream.write(b"hello")

    async def run():
        backend = TrioBackend()
        assert repr(backend) == "<TrioBackend>"

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

    trio.run(run)


def test_write_empty():
    async def run():
        transport = AsyncMock()
        await TrioStream(transport).write(b"")
        transport.send_all.assert_not_awaited()

    trio.run(run)
