import pytest

import hip


def echo(stream):
    while buffer := stream.read():
        stream.write(buffer)


@pytest.fixture
def server():
    net = hip.backends.NetworkBackend()
    with net.serve("127.0.0.1", 8080, echo) as server:
        yield server


def test_network_backend():
    net = hip.backends.NetworkBackend()
    assert repr(net) in ["<NetworkBackend [trio]>", "<NetworkBackend [threaded]>"]


def test_network_backend_connect(server):
    net = hip.backends.NetworkBackend()
    stream = net.connect(server.host, server.port)
    try:
        assert repr(stream) == f"<NetworkStream [{server.host}:{server.port}]>"
        stream.write(b"Hello, world.")
        content = stream.read()
        assert content == b"Hello, world."
    finally:
        stream.close()


class FakeSSLContext:
    def __init__(self, tls_socket):
        self.tls_socket = tls_socket
        self.wrap_socket_args = None

    def wrap_socket(self, socket, server_hostname):
        self.wrap_socket_args = (socket, server_hostname)
        return self.tls_socket


class FakeSocket:
    def __init__(self):
        self.shutdown_args = None
        self.closed = False

    def shutdown(self, how):
        self.shutdown_args = how

    def close(self):
        self.closed = True


class FailingShutdownSocket(FakeSocket):
    def shutdown(self, how):
        raise OSError


def test_network_stream_close_ignores_shutdown_errors():
    sock = FailingShutdownSocket()
    stream = hip.backends.NetworkStream(sock, ("example.com", 443))

    stream.close()

    assert sock.closed


def test_network_backend_connect_tls(monkeypatch):
    raw_socket = FakeSocket()
    tls_socket = FakeSocket()
    ssl_context = FakeSSLContext(tls_socket)
    backend = hip.backends.NetworkBackend(ssl_ctx=ssl_context)

    create_connection_args = []

    def create_connection(address, timeout):
        create_connection_args.append((address, timeout))
        return raw_socket

    monkeypatch.setattr("hip.backends.sync.socket.create_connection", create_connection)

    stream = backend.connect_tls("example.com", 443)
    try:
        assert repr(stream) == "<NetworkStream [example.com:443]>"
        assert create_connection_args == [(("example.com", 443), None)]
        assert ssl_context.wrap_socket_args == (raw_socket, "example.com")
    finally:
        stream.close()


def test_network_listener_context_managed():
    backend = hip.backends.NetworkBackend()

    with backend.listen("127.0.0.1", 0) as listener:
        assert listener.host == "127.0.0.1"

    assert listener.accept() is None


def test_network_backend_context_managed(server):
    net = hip.backends.NetworkBackend()
    with net.connect(server.host, server.port) as stream:
        stream.write(b"Hello, world.")
        content = stream.read()
        assert content == b"Hello, world."
    assert repr(stream) == f"<NetworkStream [{server.host}:{server.port} CLOSED]>"


def test_network_backend_timeout(server):
    net = hip.backends.NetworkBackend()
    with (
        hip.timeout(0.0),
        pytest.raises(TimeoutError),
        net.connect(server.host, server.port),
    ):
        pass

    with hip.timeout(10.0), net.connect(server.host, server.port):
        pass
