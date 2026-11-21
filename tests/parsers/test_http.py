import io

import pytest

import hip


class Request:
    def __init__(self, l, h, b):
        self.method, self.target, self.protocol = l
        self.headers = h
        self.body = b"".join(b)


class Response:
    def __init__(self, l, h, b):
        self.protocol, self.status, self.reason = l
        self.headers = h
        self.body = b"".join(b)


def send(req: bytes, res: bytes):
    # We're playing both sides here, in order to fully exercise
    # both the client and server parsing.
    #
    # Think of this like a proxy, we're:
    #
    # * Getting a bytestream in, parsing the request.
    # * Sending the outgoing request.
    # * Getting a bytestream out, parsing the response.
    # * Sending the outgoing response.

    server = hip.parsers.HTTPServer()
    client = hip.parsers.HTTPClient()

    req_stream = io.BytesIO(req)
    res_stream = io.BytesIO(res)

    # Use the server to parse an incoming request
    req_b = []
    while (req_l := server.recv_request_line()) is None:
        server.feed(req_stream.read(1))
    while (req_h := server.recv_headers()) is None:
        server.feed(req_stream.read(1))
    while (some_body := server.recv_body()) != b"":
        if some_body is None:
            server.feed(req_stream.read(1))
        else:
            req_b.append(some_body)

    # Use the client to send an outgoing request
    client.send_request_line(*req_l)
    client.send_headers(req_h)
    for some_body in req_b:
        client.send_body(some_body)
    client.send_body(b"")

    # Use the client to parse an incoming response
    res_b = []
    while (res_l := client.recv_status_line()) is None:
        client.feed(res_stream.read(1))
    while (res_h := client.recv_headers()) is None:
        client.feed(res_stream.read(1))
    while (some_body := client.recv_body()) != b"":
        if some_body is None:
            client.feed(res_stream.read(1))
        else:
            res_b.append(some_body)

    # Use the server to send an outgoing response
    server.send_status_line(*res_l)
    server.send_headers(res_h)
    for some_body in res_b:
        server.send_body(some_body)
    server.send_body(b"")

    return Request(req_l, req_h, req_b), Response(res_l, res_h, res_b)


def test_request_response():
    req, res = send(
        # Request...
        b"POST / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
        # Response...
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: 24\r\n"
        b"\r\n"
        b"<html>hola, mundo</html>",
    )

    # Request...
    assert req.method == b"POST"
    assert req.target == b"/"
    assert req.protocol == b"HTTP/1.1"
    assert req.headers == [
        (b"Host", b"www.example.com"),
        (b"User-Agent", b"hip/dev"),
    ]
    assert req.body == b""

    # Response...
    assert res.protocol == b"HTTP/1.1"
    assert res.status == 200
    assert res.reason == b"OK"
    assert res.headers == [
        (b"Content-Type", b"text/html"),
        (b"Content-Length", b"24"),
    ]
    assert res.body == b"<html>hola, mundo</html>"


def test_request_response_content_length():
    req, res = send(
        # Request...
        b"POST / HTTP/1.1\r\n"
        b"Host: www.example.com\r\n"
        b"User-Agent: hip/dev\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: 24\r\n"
        b"\r\n"
        b"<html>hola, mundo</html>",
        # Response...
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: 24\r\n"
        b"\r\n"
        b"<html>hola, mundo</html>",
    )

    # Request...
    assert req.method == b"POST"
    assert req.target == b"/"
    assert req.protocol == b"HTTP/1.1"
    assert req.headers == [
        (b"Host", b"www.example.com"),
        (b"User-Agent", b"hip/dev"),
        (b"Content-Type", b"text/html"),
        (b"Content-Length", b"24"),
    ]
    assert req.body == b"<html>hola, mundo</html>"

    # Response...
    assert res.protocol == b"HTTP/1.1"
    assert res.status == 200
    assert res.reason == b"OK"
    assert res.headers == [
        (b"Content-Type", b"text/html"),
        (b"Content-Length", b"24"),
    ]
    assert res.body == b"<html>hola, mundo</html>"


def test_request_response_te_chunked():
    req, res = send(
        # Request...
        b"GET / HTTP/1.1\r\n"
        b"Host: www.example.com\r\n"
        b"User-Agent: hip/dev\r\n"
        b"Content-Type: text/html\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"\r\n"
        b"A\r\n<html>hola\r\nA\r\n, mundo</h\r\n4\r\ntml>\r\n0\r\n\r\n",
        # Response...
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"\r\n"
        b"A\r\n<html>hola\r\nA\r\n, mundo</h\r\n4\r\ntml>\r\n0\r\n\r\n",
    )

    # Request...
    assert req.method == b"GET"
    assert req.target == b"/"
    assert req.protocol == b"HTTP/1.1"
    assert req.headers == [
        (b"Host", b"www.example.com"),
        (b"User-Agent", b"hip/dev"),
        (b"Content-Type", b"text/html"),
        (b"Transfer-Encoding", b"chunked"),
    ]
    assert req.body == b"<html>hola, mundo</html>"

    # Response...
    assert res.protocol == b"HTTP/1.1"
    assert res.status == 200
    assert res.reason == b"OK"
    assert res.headers == [
        (b"Content-Type", b"text/html"),
        (b"Transfer-Encoding", b"chunked"),
    ]
    assert res.body == b"<html>hola, mundo</html>"


def test_invalid_request_line():
    msg = "Invalid request line"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"...\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid method"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b" / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid url"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET  HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid protocol"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / ...\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid status line"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"...\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid protocol"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"... 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid status code"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 007 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid status code"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 XXX OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid status code"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / HTTP/1.1\r\nHost: www.example.com\r\nUser-Agent: hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 XXXX OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )

    msg = "Invalid header"
    with pytest.raises(hip.parsers.ParseError, match=msg):
        send(
            # Request...
            b"GET / HTTP/1.1\r\nHost www.example.com\r\nUser-Agent hip/dev\r\n\r\n",
            # Response...
            b"HTTP/1.1 XXXX OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: 24\r\n"
            b"\r\n"
            b"<html>hola, mundo</html>",
        )


def test_client_invalid_transitions():
    # Ensure calling parser methods cannot be called in an invalid order.
    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPClient()
        parser.send_request_line(b"GET", b"/", b"HTTP/1.1")
        parser.send_request_line(b"GET", b"/", b"HTTP/1.1")

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPClient()
        parser.send_headers([])

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPClient()
        parser.send_body(b"")

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPClient()
        parser.recv_status_line()

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPClient()
        parser.recv_headers()

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPClient()
        parser.recv_body()


def test_server_invalid_transitions():
    # Ensure calling parser methods cannot be called in an invalid order.
    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPServer()
        parser.feed(b"GET / HTTP/1.1\r\n")
        parser.recv_request_line()
        parser.recv_request_line()

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPServer()
        parser.recv_headers()

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPServer()
        parser.recv_body()

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPServer()
        parser.send_status_line(b"HTTP/1.1", 200, b"OK")

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPServer()
        parser.send_headers([])

    with pytest.raises(RuntimeError):
        parser = hip.parsers.HTTPServer()
        parser.send_body(b"")
