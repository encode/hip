import logging

from ._body import RequestContent
from ._content import Text
from ._parsers import HTTPParser
from ._request import Request
from ._response import Response
from ._network import NetworkBackend, sleep

__all__ = [
    "Server"
]

logger = logging.getLogger("httpx.server")


class ConnectionClosed(Exception):
    pass


class HTTPConnection:
    def __init__(self, stream, endpoint):
        self._stream = stream
        self._endpoint = endpoint
        self._parser = HTTPParser(stream, mode='SERVER')

    # API entry points...
    def handle_requests(self):
        try:
            while not (self._parser.keepalive_expired() or self._parser.recv_close()):
                method, url, headers = self._recv_head()
                with RequestContent(self._parser).open() as stream:
                    body = stream.read()
                request = Request(method, url, headers=headers, content=body)
                # TODO: Handle endpoint exceptions
                # async with Request(method, url, headers=headers, content=content) as request:
                try:
                    response = self._endpoint(request)
                    status_line = f"{request.method} {request.url.target} [{response.status_code}]"
                    logger.info(status_line)
                except Exception:
                    logger.error("Internal Server Error", exc_info=True)
                    content = Text("Internal Server Error")
                    err = Response(500, content=content)
                    self._send_head(err)
                    self._send_body(err)
                else:
                    self._send_head(response)
                    self._send_body(response)
        except BaseException:
            logger.error("Internal Server Error", exc_info=True)

    def close(self):
        self._parser.close()

    # Receive the request...
    def _recv_head(self) -> tuple[str, str, list[tuple[str, str]]]:
        method, target, _ = self._parser.recv_method_line()
        m = method.decode('ascii')
        t = target.decode('ascii')
        headers = self._parser.recv_headers()
        h = [
            (k.decode('latin-1'), v.decode('latin-1'))
            for k, v in headers
        ]
        return m, t, h

    def _recv_body(self):
        return self._parser.recv_body()

    # Return the response...
    def _send_head(self, response: Response):
        protocol = b"HTTP/1.1"
        status, reason = response.status_code.as_tuple()
        self._parser.send_status_line(protocol, status, reason)
        headers = response.headers.as_byte_pairs()
        self._parser.send_headers(headers)

    def _send_body(self, response: Response):
        with response as stream:
            while data := stream.read(64 * 1024):
                self._parser.send_body(data)
            self._parser.send_body(b'')


class Server:
    def __init__(self, app):
        self.app = app
        self.backend = NetworkBackend()
        self.url = 'http://127.0.0.1:8080/'

        logging.basicConfig(
            format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG
        )

    def __enter__(self):
        self._tcp_server = self.backend.serve("127.0.0.1", 8080, self.handle_stream)
        self._tcp_server.__enter__()
        logger.info(f"Serving on http://127.0.0.1:8080 (Press CTRL+C to quit)")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tcp_server.__exit__(exc_type, exc_val, exc_tb)

    def handle_stream(self, stream):
        connection = HTTPConnection(stream, self.app)
        connection.handle_requests()

    def serve(self):
        with self as server:
            while(True):
                sleep(1)
