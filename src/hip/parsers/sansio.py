class ParseError(Exception):
    pass


class BytesParser:
    """
    A parser following the Sans-IO design pattern.

    Provides parsing operations for "read some data" and
    "read some data up until a fixed delimiter".

    Used by the HTTP parsing to handle parsing the different
    sections of the request and response.
    """

    def __init__(self):
        self._buffer = bytearray()
        self._closed = False
        self._cursor = 0

    def read_some(self, max_size: int) -> bytes | None:
        """
        Returns up to `max_size` bytes.
        Returns b'' to indicate the end of the stream.
        Removes the returned data from the buffer.

        Returns `None` to indicate feed required.
        """
        if not self._buffer:
            if self._closed:
                return b""
            return None

        read, unread = self._buffer[:max_size], self._buffer[max_size:]
        self._buffer = bytearray(unread)
        return bytes(read)

    def read_until(self, marker: bytes, max_size: int) -> bytes | None:
        """
        Returns data up to and excluding the designated `marker`.
        Returns at most `max_size` bytes.
        Removes both the returned data and the marker from the buffer.

        Returns `None` to indicate feed required.

        Raises a `ParseError` if the marker cannot be found.
        """
        if self._cursor >= len(self._buffer):
            if self._closed:
                raise ParseError()
            return None

        start_point = self._cursor
        end_point = max_size + len(marker)
        idx = self._buffer.find(marker, start_point, end_point)
        if idx < 0:
            self._cursor = max(0, len(self._buffer) - len(marker))
            return None

        read, unread = self._buffer[:idx], self._buffer[idx + len(marker) :]
        self._buffer = bytearray(unread)
        self._cursor = 0
        return bytes(read)

    def feed(self, data: bytes) -> None:
        """
        Feed `data` bytes to the parser.
        Feed b'' to indicate the end of the stream.
        """
        if data:
            if self._closed:
                raise ValueError("Attempted to feed data to a closed parser.")
            self._buffer.extend(data)
        else:
            self._closed = True

    # def read_is_eof(self) -> bool | None:
    #     """
    #     Returns True to indicate the end of the stream.
    #     Returns False to indicate the st
    #     Does not remove any data from the buffer.

    #     Returns `None` to indicate feed required.
    #     """


# ---


class ProtocolError(Exception):
    pass


WAIT = 0
SEND_START = 1
SEND_HEADERS = 2
SEND_BODY = 3
SEND_COMPLETE = 4

# Internal state to track how the HTTP request/response body is sent.
# The typical case is simply 'Content-Length', or 0 bytes content.
# When the content length is unknown upfront 'Transfer-Encoding: chunked' is used.
# In this case we need state to keep track of which part
USE_CONTENT_LENGTH = 0
CHUNK_FRAME_START = 1
CHUNK_FRAME_DATA = 2
CHUNK_FRAME_NEXT = 3
CHUNK_FRAME_END = 4

# ...
MAX_REQUEST_LINE_SIZE = 16384  # Maximum size of 'GET /path?search=blue HTTP/1.1'.
MAX_RESPONSE_LINE_SIZE = 1024  # Maximum size of 'HTTP/1.1 200 OK'.
MAX_HEADERS_SIZE = 65536  # Maximum size of the request or response headers.
MAX_BODY_STREAM = 65536  # Limit individual part sizes while retutrning body.


# def _validate_request_line(data: bytes) -> tuple[bytes, bytes, bytes]:
#     try:
#         method, url, protocol = data.split(b" ")
#     except ValueError:
#         raise ProtocolError("Invalid request line")

#     if method.strip() == b"" or len(method) > 20:
#         raise ProtocolError("Invalid method")
#     if url.strip() == b"" or len(url) > 16384:
#         raise ProtocolError("Invalid url")
#     if protocol != b"HTTP/1.1" and protocol != b"HTTP/1.0":
#         raise ProtocolError("Invalid protocol")

#     return method, url, protocol


def _validate_status_line(data: bytes) -> tuple[bytes, int, bytes]:
    try:
        protocol, status_code, reason = data.split(b" ", 3)
    except ValueError:
        raise ProtocolError("Invalid status line")

    if protocol != b"HTTP/1.1" and protocol != b"HTTP/1.0":
        raise ProtocolError("Invalid protocol")

    if len(status_code) != 3:
        raise ProtocolError("Invalid status code")
    try:
        status = int(status_code)
    except ValueError:
        raise ProtocolError("Invalid status code")
    if not 100 <= status <= 999:
        raise ProtocolError("Invalid status code")

    return protocol, status, reason


def _validate_headers(data: bytes) -> list[tuple[bytes, bytes]]:
    headers = []
    for line in data.split(b"\r\n"):
        try:
            name, value = line.split(b":", 1)
        except ValueError:
            raise ProtocolError("Invalid header")
        headers.append((name, value.strip()))
    return headers


def _validate_content_length(headers: list[tuple[bytes, bytes]]) -> int:
    for key, val in headers:
        if key.lower() == b"content-length":
            return int(val)
    return 0


def _validate_data_transfer_mode(headers: list[tuple[bytes, bytes]]) -> int:
    for key, val in headers:
        if key.lower() == b"transfer-encoding" and val == b"chunked":
            return CHUNK_FRAME_START
    return USE_CONTENT_LENGTH


# TODO:

# * Content-Length validation
# * Connection: keep-alive support
# * Transfer-Encoding: chunked support
# * Validate Host header

# self._recv_te_
# self._recv_te_state = FRAME_START


# 'HEAD' responses
# 'Connection: upgrade' / 101
# 'CONNECT' support / 2xx
# 'Transfer-Encoding: chunked' - chunk extensions
# 'Transfer-Encoding: chunked' - trailing headers


class HTTPClient:
    def __init__(self):
        self._parser = BytesParser()

        self._client = SEND_START
        self._server = WAIT

        # Switch for Content-Length vs Transfer-Encoding: chunked.
        self._send_body_mode = USE_CONTENT_LENGTH
        self._recv_body_mode = USE_CONTENT_LENGTH

        # Track byte sent/recv counts.
        self._send_seen_bytes = 0
        self._send_content_length = 0
        self._recv_seen_bytes = 0
        self._recv_content_length = 0

        # Track chunk sent/recv counts.
        self._send_chunk_size = 0
        self._send_chunk_seen_bytes = 0
        self._recv_chunk_size = 0
        self._recv_chunk_seen_bytes = 0

    def send_request_line(self, method: bytes, target: bytes, protocol: bytes) -> bytes:
        if self._client != SEND_START:
            raise RuntimeError("Called 'send_method_line' out of sequence.")

        data = b"%b %b %b\r\n" % (method, target, protocol)

        # Request method line too long
        # Invalid request method line
        # Protocol not supported

        self._client = SEND_HEADERS
        self._server = SEND_START

        return data

    def send_headers(self, headers: list[tuple[bytes, bytes]]) -> bytes:
        if self._client != SEND_HEADERS:
            raise RuntimeError("Called 'send_headers' out of sequence.")

        self._send_content_length = _validate_content_length(headers)
        self._send_body_mode = _validate_data_transfer_mode(headers)

        lines = [b"%b: %b\r\n" % (name, value) for name, value in headers]
        lines.append(b"\r\n")
        data = b"".join(lines)

        # Headers too long
        # Too many headers
        # Invalid request header

        self._client = SEND_BODY

        return data

    def send_body(self, body: bytes) -> bytes:
        if self._client != SEND_BODY:
            raise RuntimeError("Called 'send_body' out of sequence.")

        # Too little body for declared Content-Length
        # Too much body for declared Content-Length
        if self._send_body_mode == USE_CONTENT_LENGTH:
            part = body
        else:
            part = b"%X\r\n%b\r\n" % (len(body), body)

        self._send_seen_bytes += len(part)

        if part == b"":
            self._client = SEND_COMPLETE

            # if self._server == SEND_COMPLETE:
            #     self._client = SEND_START
            #     self._server = WAIT

        return part

    def recv_status_line(self) -> tuple[bytes, int, bytes] | None:
        if self._server != SEND_START:
            raise RuntimeError("Called 'recv_status_line' out of sequence.")

        if (data := self._parser.read_until(b"\r\n", MAX_RESPONSE_LINE_SIZE)) is None:
            return None

        protocol, status, reason = _validate_status_line(data)

        self._server = SEND_HEADERS

        return protocol, status, reason

    def recv_headers(self) -> list[tuple[bytes, bytes]] | None:
        if self._server != SEND_HEADERS:
            raise RuntimeError("Called 'recv_headers' out of sequence.")

        if (data := self._parser.read_until(b"\r\n\r\n", MAX_HEADERS_SIZE)) is None:
            return None

        headers = _validate_headers(data)
        self._recv_content_length = _validate_content_length(headers)
        self._recv_body_mode = _validate_data_transfer_mode(headers)

        self._server = SEND_BODY

        return headers

    def recv_body(self) -> bytes | None:
        if self._server != SEND_BODY:
            raise RuntimeError("Called 'recv_body' out of sequence.")

        if self._recv_body_mode == USE_CONTENT_LENGTH:
            body = self._recv_body_content_length()
        else:
            body = self._recv_body_te_chunked()

        if body == b"":
            self._server = SEND_COMPLETE
            # if self._client == SEND_COMPLETE:
            #     self._client = SEND_START
            #     self._server = WAIT

        return body

    def _recv_body_content_length(self) -> bytes | None:
        count = min(self._recv_content_length - self._recv_seen_bytes, MAX_BODY_STREAM)
        if (body := self._parser.read_some(max_size=count)) is None:
            return None
        self._recv_seen_bytes += len(body)
        return body

    def _recv_body_te_chunked(self) -> bytes | None:
        if self._recv_body_mode == CHUNK_FRAME_NEXT:
            # Read a closing '\r\n', not the final frame.
            if self._parser.read_until(b"\r\n", max_size=0) is None:
                return None
            self._recv_body_mode = CHUNK_FRAME_START
            self._recv_chunk_seen_bytes = 0
            self._recv_chunk_size = 0

        if self._recv_body_mode == CHUNK_FRAME_START:
            # Read a leading 'xxxx\r\n', opening the frame.
            if (
                chunk_size_bytes := self._parser.read_until(b"\r\n", max_size=10)
            ) is None:
                return None
            self._recv_chunk_size = int(chunk_size_bytes, base=16)
            if self._recv_chunk_size > 0:
                self._recv_body_mode = CHUNK_FRAME_DATA
            else:
                self._recv_body_mode = CHUNK_FRAME_END

        if self._recv_body_mode == CHUNK_FRAME_END:
            # Read the closing '\r\n' returning the closing b''.
            if self._parser.read_until(b"\r\n", max_size=0) is None:
                return None
            return b""

        # Read and return some '<data>' from the frame.
        count = min(
            self._recv_chunk_size - self._recv_chunk_seen_bytes, MAX_BODY_STREAM
        )
        if (chunk := self._parser.read_some(max_size=count)) is None:
            return None
        self._recv_chunk_seen_bytes += len(chunk)
        if self._recv_chunk_seen_bytes >= self._recv_chunk_size:
            self._recv_body_mode = CHUNK_FRAME_NEXT
        return chunk

    def feed(self, data: bytes) -> None:
        """
        Feed `data` bytes to the parser.
        Feeding b'' indicates EOF.
        """
        self._parser.feed(data)

    # @property
    # def is_keep_alive(self) -> bool:
    #     ...


# class HTTPServerParser:
#     def __init__(self):
#         self._parser = BytesParser()

#     def recv_method(self) -> tuple[bytes, bytes, bytes] | None:
#         if (data := self._parser.read_until("\r\n", _MAX_REQUEST_LINE)) is None:
#             return None
#         # Request method line too long
#         # Invalid request method line
#         # Protocol not supported

#     def recv_headers(self) -> list[tuple[bytes, bytes]] | None:
#         if (data := self._parser.read_until("\r\n\r\n", _MAX_HEADERS_SIZE)) is None:
#             return None
#         ...
#         # Headers too long
#         # Too many headers
#         # Invalid request header

#     def recv_body(self) -> bytes | None:
#         if (body := self._parser.read_some(max_size=...)) is None:
#             return None
#         # Too little body for declared Content-Length
#         # Invalid framing for Transfer-Encoding

#     def send_response(self, protocol: bytes, status: int, reason: bytes) -> bytes:
#         # Protocol not supported
#         # Invalid status code
#         # Invalid reason
#         ...

#     def send_headers(self, headers: list[tuple[bytes, bytes]]) -> bytes:
#         # Headers too long
#         # Too many headers
#         # Missing Host header
#         # Conflicting Content-Length / Transfer-Encoding headers
#         ...

#     def send_body(self, body: bytes) -> bytes:
#         # Too much body for declared Content-Length
#         # Too little body for declared Content-Length
#         ...

#     def feed(self, data: bytes) -> None:
#         """
#         Feed `data` bytes to the parser.
#         Feeding b'' indicates EOF.
#         """
#         self._parser.feed(data)

#     @property
#     def is_keep_alive(self) -> bool:
#         ...
