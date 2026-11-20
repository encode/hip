from __future__ import annotations


class AsyncNetworkStream:
    async def read(self, size: int = -1) -> bytes:
        raise NotImplementedError()  # pragma: nocover

    async def write(self, data: bytes) -> None:
        raise NotImplementedError()  # pragma: nocover

    async def aclose(self) -> None:
        raise NotImplementedError()  # pragma: nocover


class AsyncNetworkBackend:
    async def connect(
        self,
        host: str,
        port: int,
    ) -> AsyncNetworkStream:
        raise NotImplementedError()  # pragma: nocover

    async def connect_tls(
        self, host: str, port: int, hostname: str = ""
    ) -> AsyncNetworkStream:
        raise NotImplementedError()  # pragma: nocover
