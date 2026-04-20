import types

from ._content import Binary, Content, Empty
from ._streams import Stream
from ._headers import Headers, parse_opts_header

__all__ = ["Response"]


class StatusCode:
    # We're using the same set as stdlib `http.HTTPStatus` here...
    #
    # https://github.com/python/cpython/blob/main/Lib/http/__init__.py
    _codes = {
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        103: "Early Hints",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Content Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a Teapot",
        421: "Misdirected Request",
        422: "Unprocessable Content",
        423: "Locked",
        424: "Failed Dependency",
        425: "Too Early",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        510: "Not Extended",
        511: "Network Authentication Required",
    }

    def __init__(self, status_code: int):
        if status_code < 100 or status_code > 999:
            raise ValueError("Invalid status code {status_code!r}")
        self.value = status_code
        self.reason_phrase = self._codes.get(status_code, "Unknown Status Code")

    def is_1xx_informational(self) -> bool:
        """
        Returns `True` for 1xx status codes, `False` otherwise.
        """
        return 100 <= int(self) <= 199

    def is_2xx_success(self) -> bool:
        """
        Returns `True` for 2xx status codes, `False` otherwise.
        """
        return 200 <= int(self) <= 299

    def is_3xx_redirect(self) -> bool:
        """
        Returns `True` for 3xx status codes, `False` otherwise.
        """
        return 300 <= int(self) <= 399

    def is_4xx_client_error(self) -> bool:
        """
        Returns `True` for 4xx status codes, `False` otherwise.
        """
        return 400 <= int(self) <= 499

    def is_5xx_server_error(self) -> bool:
        """
        Returns `True` for 5xx status codes, `False` otherwise.
        """
        return 500 <= int(self) <= 599

    def has_body(self) -> bool:
        return not(self.is_1xx_informational() or self.value == 204 or self.value == 304)

    def as_tuple(self) -> tuple[int, bytes]:
        return (self.value, self.reason_phrase.encode('ascii'))

    def __eq__(self, other) -> bool:
        return int(self) == int(other)

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return f"{self.value} {self.reason_phrase}"

    def __repr__(self) -> str:
        return f"<StatusCode [{self.value} {self.reason_phrase}]>"


class Response:
    def __init__(
        self,
        status_code: StatusCode | int,
        *,
        headers: Headers | dict[str, str] | None = None,
        content: Content | bytes | None = None,
    ):
        self.status_code = StatusCode(status_code) if not isinstance(status_code, StatusCode) else status_code
        self.headers = Headers(headers) if not isinstance(headers, Headers) else headers
        self.content = (
            content if isinstance(content, Content) else
            Binary(content) if isinstance(content, bytes) or self.status_code.has_body() else
            Empty()
        )

        # https://datatracker.ietf.org/doc/html/rfc2616#section-4.3
        # RFC 2616, Section 4.3, Message Body.
        #
        # All responses to the HEAD request method
        # MUST NOT include a message-body, even though the presence of entity-
        # header fields might lead one to believe they do. All 1xx
        # (informational), 204 (no content), and 304 (not modified) responses
        # MUST NOT include a message-body. All other responses do include a
        # message-body, although it MAY be of zero length.
        self.headers = self.headers.copy_update(self.content.headers())

    @property
    def body(self) -> bytes:
        return bytes(self.content)

    def __enter__(self) -> 'ResponseStream':
        stream = self.content.open()
        context = ResponseStream(self.status_code, self.headers, stream)
        self._context = context
        return self._context

    def __exit__(self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None
    ) -> None:
        self._context.close()

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


class ResponseStream(Stream):
    def __init__(self, status_code: StatusCode, headers: Headers, stream: Stream) -> None:
        self.status_code = status_code
        self.headers = headers
        self._stream = stream

    def read(self, size: int=-1) -> bytes:
        return self._stream.read(size)

    def close(self) -> None:
        self._stream.close()

    def __repr__(self):
        return f"<RequestStream [{self.status_code}]>"
