import types

from .._content import Content
from .._headers import Headers
from .._request import Method, Request
from .._response import Response, StatusCode
from .._streams import Stream
from .._urls import URL

__all__ = ["SendContext", "Transport"]


class SendContext:
    def __init__(
        self, status_code: StatusCode, headers: Headers, stream: Stream
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.stream = stream

    def __iter__(self):
        return iter((self.status_code, self.headers, self.stream))

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ) -> None:
        self.stream.close()


class Transport:
    def send(self, request: Request) -> SendContext:
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
        with self.send(request) as (status_code, resp_headers, stream):
            body = stream.read()
        return Response(status_code, headers=resp_headers, content=body)

    def stream(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> SendContext:
        request = Request(method, url, headers=headers, content=content)
        return self.send(request)
