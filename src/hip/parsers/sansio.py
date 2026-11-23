from .base import BytesParser, ParseError

# * Connection: keep-alive support

# Sending...
# * Validate body matches 'Content-Length'
# * Validate 'Host' header

# 'HEAD' responses
# 'Connection: upgrade' / 101
# 'CONNECT' support / 2xx
# 'Transfer-Encoding: chunked' - chunk extensions
# 'Transfer-Encoding: chunked' - trailing headers

WAIT = 0
SEND_START = 1
SEND_HEADERS = 2
SEND_BODY = 3
SEND_COMPLETE = 4

# Internal state to track how the HTTP request/response body is sent.
USE_CONTENT_LENGTH = 0
USE_TE_CHUNKED = 1

# Internal states for `Transfer-Encoding: chunked`
TE_FRAME_START = 0
TE_FRAME_DATA = 1
TE_FRAME_NEXT = 2
TE_FRAME_END = 3

# Buffer limits...
MAX_REQUEST_LINE_SIZE = 16384  # Maximum size of 'GET /path?search=blue HTTP/1.1'.
MAX_RESPONSE_LINE_SIZE = 1024  # Maximum size of 'HTTP/1.1 200 OK'.
MAX_HEADERS_SIZE = 65536  # Maximum size of the request or response headers.
MAX_BODY_STREAM = 65536  # Limit individual part sizes while returning body.


def _validate_request_line(data: bytes) -> tuple[bytes, bytes, bytes]:
    try:
        method, url, protocol = data.split(b" ", 2)
    except ValueError:
        raise ParseError("Invalid request line")

    if method.strip() == b"" or len(method) > 20:
        raise ParseError("Invalid method")
    if url.strip() == b"" or len(url) > 16384:
        raise ParseError("Invalid url")
    if protocol != b"HTTP/1.1" and protocol != b"HTTP/1.0":
        raise ParseError("Invalid protocol")

    return method, url, protocol


def _validate_status_line(data: bytes) -> tuple[bytes, int, bytes]:
    try:
        protocol, status_code, reason = data.split(b" ", 2)
    except ValueError:
        raise ParseError("Invalid status line")

    if protocol != b"HTTP/1.1" and protocol != b"HTTP/1.0":
        raise ParseError("Invalid protocol")

    if len(status_code) != 3:
        raise ParseError("Invalid status code")
    try:
        status = int(status_code)
    except ValueError:
        raise ParseError("Invalid status code")
    if not 100 <= status <= 999:
        raise ParseError("Invalid status code")

    return protocol, status, reason


def _validate_headers(data: bytes) -> list[tuple[bytes, bytes]]:
    headers = []
    for line in data.split(b"\r\n"):
        try:
            name, value = line.split(b":", 1)
        except ValueError:
            raise ParseError("Invalid header")
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
            return USE_TE_CHUNKED
    return USE_CONTENT_LENGTH


class HTTPClient:
    def __init__(self):
        self._parser = BytesParser()

        self._client = SEND_START
        self._server = WAIT

        # Switch for Content-Length vs Transfer-Encoding: chunked.
        self._send_mode = USE_CONTENT_LENGTH
        self._recv_mode = USE_CONTENT_LENGTH

        # Track byte sent/recv counts.
        self._send_count = 0
        self._recv_count = 0

        # Track Content-Length state.
        self._send_content_length = 0
        self._recv_content_length = 0

        # Track Transfer-Encoding state.
        self._recv_te_state = TE_FRAME_START
        self._recv_te_frame_size = 0
        self._recv_te_frame_count = 0

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
        self._send_mode = _validate_data_transfer_mode(headers)

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
        if self._send_mode == USE_CONTENT_LENGTH:
            part = body
        else:
            part = b"%X\r\n%b\r\n" % (len(body), body)

        self._send_count += len(part)

        if body == b"":
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
        self._recv_mode = _validate_data_transfer_mode(headers)

        self._server = SEND_BODY

        return headers

    def recv_body(self) -> bytes | None:
        if self._server != SEND_BODY:
            raise RuntimeError("Called 'recv_body' out of sequence.")

        if self._recv_mode == USE_CONTENT_LENGTH:
            body = self._recv_body_content_length()
        else:
            body = self._recv_body_te_chunked()

        if body == b"":
            if self._recv_mode == USE_CONTENT_LENGTH and self._recv_count < self._recv_content_length:
                raise ParseError('Response has less content than Content-Length')
            self._server = SEND_COMPLETE
            # if self._client == SEND_COMPLETE:
            #     self._client = SEND_START
            #     self._server = WAIT

        return body

    def _recv_body_content_length(self) -> bytes | None:
        remaining = self._recv_content_length - self._recv_count
        if not remaining:
            return b""

        count = min(remaining, MAX_BODY_STREAM)
        if (body := self._parser.read_some(max_size=count)) is None:
            return None

        self._recv_count += len(body)

        return body

    def _recv_body_te_chunked(self) -> bytes | None:
        if self._recv_te_state == TE_FRAME_NEXT:
            # Read a closing '\r\n', not the final frame.
            if self._parser.read_until(b"\r\n", max_size=0) is None:
                return None
            self._recv_te_state = TE_FRAME_START
            self._recv_te_frame_size = 0
            self._recv_te_frame_count = 0

        if self._recv_te_state == TE_FRAME_START:
            # Read a leading 'xxxx\r\n', opening the frame.
            if (frame_st := self._parser.read_until(b"\r\n", max_size=10)) is None:
                return None
            self._recv_te_frame_size = int(frame_st, base=16)
            if self._recv_te_frame_size > 0:
                self._recv_te_state = TE_FRAME_DATA
            else:
                self._recv_te_state = TE_FRAME_END

        if self._recv_te_state == TE_FRAME_END:
            # Read the closing '\r\n' returning the closing b''.
            if self._parser.read_until(b"\r\n", max_size=0) is None:
                return None
            return b""

        # Read and return some '<data>' from the frame.
        remaining = self._recv_te_frame_size - self._recv_te_frame_count
        count = min(remaining, MAX_BODY_STREAM)
        if (chunk := self._parser.read_some(max_size=count)) is None:
            return None

        # Error case: we could have EOF here.
        self._recv_te_frame_count += len(chunk)
        if self._recv_te_frame_count == self._recv_te_frame_size:
            self._recv_te_state = TE_FRAME_NEXT
        return chunk

    def feed(self, data: bytes) -> None:
        """
        Feed `data` bytes to the parser.
        Feeding b'' indicates EOF.
        """
        self._parser.feed(data)


class HTTPServer:
    def __init__(self):
        self._parser = BytesParser()

        self._client = SEND_START
        self._server = WAIT

        # Switch for Content-Length vs Transfer-Encoding: chunked.
        self._send_mode = USE_CONTENT_LENGTH
        self._recv_mode = USE_CONTENT_LENGTH

        # Track byte sent/recv counts.
        self._send_count = 0
        self._recv_count = 0

        # Track Content-Length state.
        self._send_content_length = 0
        self._recv_content_length = 0

        # Track Transfer-Encoding state.
        self._recv_te_state = TE_FRAME_START
        self._recv_te_frame_size = 0
        self._recv_te_frame_count = 0

    def recv_request_line(self) -> tuple[bytes, bytes, bytes] | None:
        if self._client != SEND_START:
            raise RuntimeError("Called 'recv_request_line' out of sequence.")

        if (data := self._parser.read_until(b"\r\n", MAX_REQUEST_LINE_SIZE)) is None:
            return None

        method, target, protocol = _validate_request_line(data)

        self._client = SEND_HEADERS
        self._server = SEND_START

        return method, target, protocol

    def recv_headers(self) -> list[tuple[bytes, bytes]] | None:
        if self._client != SEND_HEADERS:
            raise RuntimeError("Called 'recv_headers' out of sequence.")

        if (data := self._parser.read_until(b"\r\n\r\n", MAX_HEADERS_SIZE)) is None:
            return None

        headers = _validate_headers(data)
        self._recv_content_length = _validate_content_length(headers)
        self._recv_mode = _validate_data_transfer_mode(headers)

        self._client = SEND_BODY

        return headers

    def recv_body(self) -> bytes | None:
        if self._client != SEND_BODY:
            raise RuntimeError("Called 'recv_body' out of sequence.")

        if self._recv_mode == USE_CONTENT_LENGTH:
            body = self._recv_body_content_length()
        else:
            body = self._recv_body_te_chunked()

        if body == b"":
            if self._recv_mode == USE_CONTENT_LENGTH and self._recv_count < self._recv_content_length:
                raise ParseError('Request has less content than Content-Length')
            self._client = SEND_COMPLETE
            # if self._client == SEND_COMPLETE:
            #     self._client = SEND_START
            #     self._server = WAIT

        return body

    def _recv_body_content_length(self) -> bytes | None:
        remaining = self._recv_content_length - self._recv_count
        if not remaining:
            return b""

        count = min(remaining, MAX_BODY_STREAM)
        if (body := self._parser.read_some(max_size=count)) is None:
            return None

        self._recv_count += len(body)

        return body

    def _recv_body_te_chunked(self) -> bytes | None:
        if self._recv_te_state == TE_FRAME_NEXT:
            # Read a closing '\r\n', not the final frame.
            if self._parser.read_until(b"\r\n", max_size=0) is None:
                return None
            self._recv_te_state = TE_FRAME_START
            self._recv_te_frame_size = 0
            self._recv_te_frame_count = 0

        if self._recv_te_state == TE_FRAME_START:
            # Read a leading 'xxxx\r\n', opening the frame.
            if (frame_st := self._parser.read_until(b"\r\n", max_size=10)) is None:
                return None
            self._recv_te_frame_size = int(frame_st, base=16)
            if self._recv_te_frame_size > 0:
                self._recv_te_state = TE_FRAME_DATA
            else:
                self._recv_te_state = TE_FRAME_END

        if self._recv_te_state == TE_FRAME_END:
            # Read the closing '\r\n' returning the closing b''.
            if self._parser.read_until(b"\r\n", max_size=0) is None:
                return None
            return b""

        # Read and return some '<data>' from the frame.
        remaining = self._recv_te_frame_size - self._recv_te_frame_count
        count = min(remaining, MAX_BODY_STREAM)
        if (chunk := self._parser.read_some(max_size=count)) is None:
            return None
        self._recv_te_frame_count += len(chunk)
        if self._recv_te_frame_count == self._recv_te_frame_size:
            self._recv_te_state = TE_FRAME_NEXT
        return chunk

    def send_status_line(self, protocol: bytes, status: int, reason: bytes) -> bytes:
        if self._server != SEND_START:
            raise RuntimeError("Called 'send_method_line' out of sequence.")

        data = b"%b %d %b\r\n" % (protocol, status, reason)

        # Request method line too long
        # Invalid request method line
        # Protocol not supported

        self._server = SEND_HEADERS

        return data

    def send_headers(self, headers: list[tuple[bytes, bytes]]) -> bytes:
        if self._server != SEND_HEADERS:
            raise RuntimeError("Called 'send_headers' out of sequence.")

        self._send_content_length = _validate_content_length(headers)
        self._send_mode = _validate_data_transfer_mode(headers)

        lines = [b"%b: %b\r\n" % (name, value) for name, value in headers]
        lines.append(b"\r\n")
        data = b"".join(lines)

        # Headers too long
        # Too many headers
        # Invalid request header

        self._server = SEND_BODY

        return data

    def send_body(self, body: bytes) -> bytes:
        if self._server != SEND_BODY:
            raise RuntimeError("Called 'send_body' out of sequence.")

        # Too little body for declared Content-Length
        # Too much body for declared Content-Length
        if self._send_mode == USE_CONTENT_LENGTH:
            part = body
        else:
            part = b"%X\r\n%b\r\n" % (len(body), body)

        self._send_count += len(part)

        if body == b"":
            self._server = SEND_COMPLETE

        return part

    def feed(self, data: bytes) -> None:
        """
        Feed `data` bytes to the parser.
        Feeding b'' indicates EOF.
        """
        self._parser.feed(data)
