import types

from .._content import Content
from .._headers import Headers
from .._request import Method, Request
from .._response import Response, StatusCode
from .._streams import Stream
from .._urls import URL

__all__ = ["ResponseStream", "Transport"]


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
