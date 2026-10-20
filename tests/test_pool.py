import pytest

import hip


def hello_world(request):
    content = hip.Text("Hello, world.")
    return hip.Response(200, content=content)


@pytest.fixture
def server():
    with hip.Server(hello_world) as server:
        yield server


def test_connection_pool_request(server):
    with hip.ConnectionPool() as pool:
        assert repr(pool) == "<ConnectionPool [0 active]>"
        assert len(pool.connections) == 0

        r = pool.request("GET", server.url)

        assert r.status_code == 200
        assert repr(pool) == "<ConnectionPool [0 active, 1 idle]>"
        assert len(pool.connections) == 1


def test_transport_request_not_implemented():
    transport = hip.Transport()

    with pytest.raises(NotImplementedError):
        transport.request("GET", "http://example.com")


def test_transport_close():
    hip.Transport().close()


def test_connection_pool_connection_close(server):
    with hip.ConnectionPool() as pool:
        assert repr(pool) == "<ConnectionPool [0 active]>"
        assert len(pool.connections) == 0

        r = pool.request("GET", server.url, headers={"Connection": "close"})

        # TODO: Really we want closed connections proactively removed from the pool,
        assert r.status_code == 200
        assert repr(pool) == "<ConnectionPool [0 active, 1 closed]>"
        assert len(pool.connections) == 1


def test_connection_pool_stream(server):
    with hip.ConnectionPool() as pool:
        assert repr(pool) == "<ConnectionPool [0 active]>"
        assert len(pool.connections) == 0

        with pool.stream("GET", server.url) as r:
            assert r.status_code == 200
            assert repr(pool) == "<ConnectionPool [1 active]>"
            assert len(pool.connections) == 1
            r.read()

        assert repr(pool) == "<ConnectionPool [0 active, 1 idle]>"
        assert len(pool.connections) == 1


def test_connection_pool_cannot_request_after_closed():
    with hip.ConnectionPool() as pool:
        pass

    with pytest.raises(RuntimeError):
        pool.request("GET", "http://example.com")


def test_connection_pool_should_have_managed_lifespan(server):
    pool = hip.ConnectionPool()
    with pytest.warns(UserWarning):
        del pool


def test_connection_request(server):
    with hip.open_connection(server.url) as conn:
        assert repr(conn) == f"<Connection [{server.url} idle]>"

        r = conn.request("GET", "/")

        assert r.status_code == 200
        assert repr(conn) == f"<Connection [{server.url} idle]>"


def test_connection_stream(server):
    with hip.open_connection(server.url) as conn:
        assert repr(conn) == f"<Connection [{server.url} idle]>"
        with conn.stream("GET", "/") as r:
            assert r.status_code == 200
            assert repr(conn) == f"<Connection [{server.url} active]>"
            r.read()
        assert repr(conn) == f"<Connection [{server.url} idle]>"


def test_connection_stream_read_in_chunks(server):
    with hip.open_connection(server.url) as conn, conn.stream("GET", "/") as response:
        assert response.read(5) == b"Hello"
        assert response.read(5) == b", wor"
        assert response.read() == b"ld."


class TLSBackend:
    def connect_tls(self, host, port, hostname):
        self.connect_tls_args = (host, port, hostname)
        return hip.Binary(b"").open()


def test_open_https_connection():
    backend = TLSBackend()

    with hip.open_connection(
        "https://example.com",
        hostname="example.com",
        backend=backend,
    ):
        pass

    assert backend.connect_tls_args == ("example.com", 443, "example.com")
