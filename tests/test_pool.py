import pytest

import httpx


def hello_world(request):
    content = httpx.Text("Hello, world.")
    return httpx.Response(200, content=content)


@pytest.fixture
def server():
    with httpx.Server(hello_world) as server:
        yield server


def test_connection_pool_request(server):
    with httpx.ConnectionPool() as pool:
        assert repr(pool) == "<ConnectionPool [0 active]>"
        assert len(pool.connections) == 0

        r = pool.request("GET", server.url)

        assert r.status_code == 200
        assert repr(pool) == "<ConnectionPool [0 active, 1 idle]>"
        assert len(pool.connections) == 1


def test_connection_pool_connection_close(server):
    with httpx.ConnectionPool() as pool:
        assert repr(pool) == "<ConnectionPool [0 active]>"
        assert len(pool.connections) == 0

        r = pool.request("GET", server.url, headers={"Connection": "close"})

        # TODO: Really we want closed connections proactively removed from the pool,
        assert r.status_code == 200
        assert repr(pool) == "<ConnectionPool [0 active, 1 closed]>"
        assert len(pool.connections) == 1


def test_connection_pool_stream(server):
    with httpx.ConnectionPool() as pool:
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
    with httpx.ConnectionPool() as pool:
        pass

    with pytest.raises(RuntimeError):
        pool.request("GET", "http://example.com")


def test_connection_pool_should_have_managed_lifespan(server):
    pool = httpx.ConnectionPool()
    with pytest.warns(UserWarning):
        del pool


def test_connection_request(server):
    with httpx.open_connection(server.url) as conn:
        assert repr(conn) == f"<Connection [{server.url} idle]>"

        r = conn.request("GET", "/")

        assert r.status_code == 200
        assert repr(conn) == f"<Connection [{server.url} idle]>"


def test_connection_stream(server):
    with httpx.open_connection(server.url) as conn:
        assert repr(conn) == f"<Connection [{server.url} idle]>"
        with conn.stream("GET", "/") as r:
            assert r.status_code == 200
            assert repr(conn) == f"<Connection [{server.url} active]>"
            r.read()
        assert repr(conn) == f"<Connection [{server.url} idle]>"


def test_connection_stream_read_in_chunks(server):
    with httpx.open_connection(server.url) as conn, conn.stream("GET", "/") as response:
        assert response.read(5) == b"Hello"
        assert response.read(5) == b", wor"
        assert response.read() == b"ld."
