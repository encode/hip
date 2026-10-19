from ._content import Binary, Content, Empty
from ._headers import Headers
from ._urls import URL

__all__ = ["Method", "Request"]

STANDARD_METHODS = (
    "CONNECT",
    "DELETE",
    "GET",
    "HEAD",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "TRACE",
)


class Method:
    def __init__(self, method: str, standard=True):
        if standard:
            method = method.upper()
            if method not in STANDARD_METHODS:
                raise ValueError(f"Non-standard method {method!r}")
        self._method = method

    def has_body(self) -> bool:
        return self._method in ("POST", "PUT", "PATCH")

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __bytes__(self) -> bytes:
        return self._method.encode("ascii")

    def __str__(self) -> str:
        return self._method

    def __repr__(self):
        return f"<Method {self._method}>"


class Request:
    def __init__(
        self,
        method: Method | str,
        url: URL | str,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ):
        self.method = Method(method) if not isinstance(method, Method) else method
        self.url = URL(url) if not isinstance(url, URL) else url
        self.headers = Headers(headers) if not isinstance(headers, Headers) else headers
        self.content: Content = (
            content
            if isinstance(content, Content)
            else Binary(content)
            if isinstance(content, bytes) or self.method.has_body()
            else Empty()
        )

        # https://datatracker.ietf.org/doc/html/rfc2616#section-14.23
        # RFC 2616, Section 14.23, Host.
        #
        # A client MUST include a Host header field in all HTTP/1.1 request messages.
        if "Host" not in self.headers:
            self.headers = self.headers.copy_set("Host", self.url.netloc)

        # https://datatracker.ietf.org/doc/html/rfc2616#section-4.3
        # RFC 2616, Section 4.3, Message Body.
        #
        # The presence of a message-body in a request is signaled by the
        # inclusion of a Content-Length or Transfer-Encoding header field in
        # the request's message-headers.
        self.headers = self.headers.copy_update(self.content.headers())

    @property
    def body(self) -> bytes:
        return bytes(self.content)

    def __repr__(self):
        return f"<Request [{self.method} {str(self.url)!r}]>"
