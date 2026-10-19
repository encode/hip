import socket

import hip


def app(request):
    content = hip.HTML("<html><body>¡Hola, mundo!</body></html>")
    return hip.Response(200, content=content)


def test_server_defaults():
    server = hip.Server(app)

    assert server.host == "127.0.0.1"
    assert server.port == 8080
    assert server.url == "http://127.0.0.1:8080/"


def test_server_custom_host_and_port():
    server = hip.Server(app, host="0.0.0.0", port=8000)

    assert server.host == "0.0.0.0"
    assert server.port == 8000
    assert server.url == "http://0.0.0.0:8000/"


def test_server_defaults_headers():
    with hip.Server(app) as server, hip.Client() as client:
        response = client.get(server.url)
        assert response.headers["Server"] == "hip/dev"
        assert response.headers["Connection"] == "keep-alive"
        assert response.headers["Date"].endswith("GMT")


def test_server_ignores_clean_client_disconnect(caplog):
    with (
        hip.Server(app) as server,
        socket.create_connection((server.host, server.port)) as client,
    ):
        client.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        # Stop sending, but leave the socket open to read the response.
        client.shutdown(socket.SHUT_WR)
        response = bytearray()
        while chunk := client.recv(4096):
            response.extend(chunk)

    assert response.startswith(b"HTTP/1.1 200 OK\r\n")
    assert not any(
        record.name == "hip.server" and record.getMessage() == "Internal Server Error"
        for record in caplog.records
    )


def error_app(request):
    raise RuntimeError("Something went wrong")


def test_server_internal_server_error():
    with hip.Server(error_app) as server, hip.Client() as client:
        response = client.get(server.url)

    assert response.status_code == 500
    assert response.body == b"Internal Server Error"
