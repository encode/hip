import asyncio
import ssl
import truststore
import types

from .._streams import Stream


class NetworkStream(Stream):
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, address: tuple[str, int]) -> None:
        self._reader = reader
        self._writer = writer
        self._address = address
        self._is_tls = False
        self._is_closed = False

    @property
    def host(self) -> str:
        return self._address[0]

    @property
    def port(self) -> int:
        return self._address[1]

    async def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = 64 * 1024
        return await self._reader.read(size)

    async def write(self, buffer: bytes) -> None:
        self._writer.write(buffer)
        await self._writer.drain()

    async def close(self) -> None:
        if not self._is_closed:
            self._is_closed = True
            self._writer.close()
            await self._writer.wait_closed()

    def __repr__(self):
        description = ""
        description += " TLS" if self._is_tls else ""
        description += " CLOSED" if self._is_closed else ""
        return f"<NetworkStream [{self.host}:{self.port}{description}]>"

    async def __aenter__(self) -> "Self":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ):
        await self.close()


class NetworkBackend:
    def __init__(self, ssl_ctx: ssl.SSLContext | None = None):
        self._ssl_ctx = self.create_default_context() if ssl_ctx is None else ssl_ctx

    def create_default_context(self) -> ssl.SSLContext:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    async def connect(self, host: str, port: int) -> NetworkStream:
        """
        Connect to the given address, returning a NetworkStream instance.
        """
        address = (host, port)
        reader, writer = await asyncio.open_connection(host, port)
        return NetworkStream(reader, writer, address)

    async def connect_tls(self, host: str, port: int, hostname: str = "") -> NetworkStream:
        """
        Connect to the given address, returning a NetworkStream instance.
        """
        address = (host, port)
        reader, writer = await asyncio.open_connection(host, port, ssl=self._ssl_ctx, server_hostname=hostname)
        return NetworkStream(reader, writer, address)


Semaphore = asyncio.Semaphore
Lock = asyncio.Lock
