import datetime
import logging

from ._body import HTTPStream
from ._content import Text
from ._headers import Headers
from ._network import NetworkBackend, sleep
from ._parsers import HTTPParser
from ._request import Request
from ._response import Response

__all__ = ["Server"]

logger = logging.getLogger("hip.server")


class HTTPConnection:
    def __init__(self, stream, endpoint):
        self._stream = stream
        self._endpoint = endpoint
        self._parser = HTTPParser(stream, mode="SERVER")
        self._default_headers = Headers(
            {"Server": "hip/dev", "Connection": "keep-alive"}
        )

    # API entry points...
    def handle_requests(self):
        try:
            while self._parser.is_idle():
                try:
                    method, url, headers = self._recv_head()
                except EOFError:
                    # The client closed while waiting for a request line.
                    return
                with HTTPStream(self._parser, is_response=False) as stream:
                    body = stream.read()
                request = Request(method, url, headers=headers, content=body)
                # TODO: Handle endpoint exceptions
                # async with Request(method, url, headers=headers, content=content) as request:
                try:
                    response = self._endpoint(request)
                    status_line = f"{request.method} {request.url.target} [{response.status_code}]"
                    logger.info(status_line)
                except Exception:
                    logger.exception("Internal Server Error")
                    content = Text("Internal Server Error")
                    err = Response(500, content=content)
                    self._send_head(err)
                    self._send_body(err)
                else:
                    self._send_head(response)
                    self._send_body(response)
        except BaseException:
            logger.exception("Internal Server Error")

    # Receive the request...
    def _recv_head(self) -> tuple[str, str, list[tuple[str, str]]]:
        method, target, _ = self._parser.recv_method_line()
        m = method.decode("ascii")
        t = target.decode("ascii")
        headers = self._parser.recv_headers()
        h = [(k.decode("latin-1"), v.decode("latin-1")) for k, v in headers]
        return m, t, h

    # Return the response...
    def _send_head(self, response: Response):
        protocol = b"HTTP/1.1"
        status, reason = response.status_code.as_tuple()
        self._parser.send_status_line(protocol, status, reason)

        now = datetime.datetime.now(datetime.timezone.utc)
        date = now.strftime("%a, %d %b %Y, %H:%M:%S GMT")

        headers = self._default_headers
        headers = headers.copy_set("Date", date)
        headers = headers.copy_update(response.headers)
        self._parser.send_headers(headers.as_byte_pairs())

    def _send_body(self, response: Response):
        with response.content.open() as stream:
            while data := stream.read(64 * 1024):
                self._parser.send_body(data)
            self._parser.send_body(b"")
        self._parser.complete()


class Server:
    def __init__(self, app, host="127.0.0.1", port=8080):
        self.app = app
        self.host = host
        self.port = port
        self.backend = NetworkBackend()
        self.url = f"http://{host}:{port}/"

        logging.basicConfig(
            format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG,
        )

    def __enter__(self):
        self._tcp_server = self.backend.serve(self.host, self.port, self.handle_stream)
        self._tcp_server.__enter__()
        logger.info(f"Serving on http://{self.host}:{self.port} (Press CTRL+C to quit)")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tcp_server.__exit__(exc_type, exc_val, exc_tb)

    def until_interrupt(self):  # pragma: no cover
        """Keep a context-managed server alive until Ctrl+C is pressed."""
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass

    def handle_stream(self, stream):
        connection = HTTPConnection(stream, self.app)
        connection.handle_requests()
