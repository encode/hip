import types
import typing

from .core.content import HTML, JSON, Binary, Content, Text, select_media
from .core.headers import Headers
from .core.request import Method, Request
from .core.response import Response
from .core.urls import URL
from .transports import ConnectionPool, SendContext, Transport

__all__ = ["Client"]


class Client:
    def __init__(
        self,
        url: URL | str | None = None,
        headers: Headers | typing.Mapping[str, str] | None = None,
    ):
        if url is None:
            url = ""
        if headers is None:
            headers = {
                "User-Agent": "dev",
                "Accept-Encoding": "gzip",
            }
        self.headers = Headers(headers)
        self.transport = ConnectionPool()
        self.url = URL(url)
        self.via = RedirectMiddleware(self.transport)
        self.media = {
            "application/json": JSON,
            "text/html": HTML,
            "text/*": Text,
            "*/*": Binary,
        }

    def build_request(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> Request:
        return Request(
            method=method,
            url=self.url.join(url),
            headers=self.headers.copy_update(headers),
            content=content,
        )

    def request(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ) -> Response:
        request = self.build_request(method, url, headers=headers, content=content)
        with self.via.send(request) as (status_code, resp_headers, stream):
            ct = resp_headers.get("Content-Type", "application/octet-stream")
            cls = select_media(self.media, ct)
            content = cls.parse(stream)
        return Response(
            status_code=status_code,
            headers=resp_headers,
            content=content,
        )

    def get(
        self,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
    ):
        return self.request("GET", url, headers=headers)

    def post(
        self,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ):
        return self.request("POST", url, headers=headers, content=content)

    def put(
        self,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ):
        return self.request("PUT", url, headers=headers, content=content)

    def patch(
        self,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ):
        return self.request("PATCH", url, headers=headers, content=content)

    def delete(
        self,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
    ):
        return self.request("DELETE", url, headers=headers)

    def close(self):
        self.via.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ):
        self.close()

    def __repr__(self):
        return f"<Client [{self.transport.description()}]>"


class RedirectMiddleware(Transport):
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def build_redirect_request(
        self, request: Request, ctx: SendContext
    ) -> Request | None:
        status, headers, _ = ctx

        # Redirect status codes...
        if status not in (301, 302, 303, 307, 308):
            return None

        # Redirects need a valid location header...
        try:
            location = URL(headers["Location"])
        except (KeyError, ValueError):
            return None

        # Instantiate a redirect request...
        method = request.method
        url = request.url.join(location)
        headers = request.headers
        content = request.content

        return Request(method, url, headers, content)

    def send(self, request: Request) -> SendContext:
        while True:
            ctx = self._transport.send(request)

            # Determine if we have a redirect or not.
            redirect = self.build_redirect_request(request, ctx)

            # If we don't have a redirect, we're done.
            if redirect is None:
                return ctx

            # If we have a redirect, then we read the body of the response.
            # Ensures that the HTTP connection is available for a new
            # request/response cycle.
            with ctx:
                _, _, stream = ctx
                stream.read()

            # Make the next request
            request = redirect

    def close(self):
        self._transport.close()
