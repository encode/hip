import gzip
import json
import random

import pytest

import hip


def redirect(request):
    if request.url.path == "/redirect":
        return hip.Response(302, headers={"Location": "/"})
    return hip.Response(200, content=hip.Text("hello, world!"))


def echo(request):
    response = hip.Response(
        200,
        content=hip.JSON(
            {
                "method": str(request.method),
                "query-params": dict(request.url.params.items()),
                "content-type": request.headers.get("Content-Type"),
                "json": json.loads(request.body) if request.body else None,
            }
        ),
    )
    return response


def json_response_with_content_type_options(request):
    return hip.Response(
        200,
        headers={"Content-Type": 'application/json; title="hello\\"world"'},
        content=b'{"message":"hello"}',
    )


def invalid_content_type(request):
    return hip.Response(
        200,
        headers={"Content-Type": "; charset=utf-8"},
        content=b"hello",
    )


def application_problem_json_response(request):
    return hip.Response(
        403,
        headers={"Content-Type": "application/problem+json"},
        content=b'{"detail":"Forbidden"}',
    )


def application_octet_stream_response(request):
    return hip.Response(
        200,
        headers={"Content-Type": "application/octet-stream"},
        content=b"\x00\x01\x02",
    )


@pytest.fixture
def client():
    with hip.Client() as client:
        yield client


@pytest.fixture
def server():
    with hip.Server(echo) as server:
        yield server


def test_client(client):
    assert repr(client) == "<Client [0 active]>"


def test_get(client, server):
    r = client.get(server.url)
    assert r.status_code == 200
    assert (
        r.body == b'{"method":"GET","query-params":{},"content-type":null,"json":null}'
    )
    assert r.content == {
        "method": "GET",
        "query-params": {},
        "content-type": None,
        "json": None,
    }


def test_post(client, server):
    data = hip.JSON({"data": 123})
    r = client.post(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        "method": "POST",
        "query-params": {},
        "content-type": "application/json",
        "json": {"data": 123},
    }


def test_put(client, server):
    data = hip.JSON({"data": 123})
    r = client.put(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        "method": "PUT",
        "query-params": {},
        "content-type": "application/json",
        "json": {"data": 123},
    }


def test_patch(client, server):
    data = hip.JSON({"data": 123})
    r = client.patch(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        "method": "PATCH",
        "query-params": {},
        "content-type": "application/json",
        "json": {"data": 123},
    }


def test_delete(client, server):
    r = client.delete(server.url)
    assert r.status_code == 200
    assert r.content == {
        "method": "DELETE",
        "query-params": {},
        "content-type": None,
        "json": None,
    }


def test_request(client, server):
    r = client.request("GET", server.url)
    assert r.status_code == 200
    assert r.content == {
        "method": "GET",
        "query-params": {},
        "content-type": None,
        "json": None,
    }


def test_stream(client, server):
    with client.stream("GET", server.url) as r:
        assert r.status_code == 200
        body = r.read()
        assert json.loads(body) == {
            "method": "GET",
            "query-params": {},
            "content-type": None,
            "json": None,
        }


def test_stream_read_after_eof(client, server):
    with client.stream("GET", server.url) as response:
        assert response.read()
        assert response.read() == b""
        assert response.read() == b""


def test_keepalive(client, server):
    first = client.get(server.url)
    second = client.get(server.url)

    assert first.status_code == 200
    assert second.status_code == 200


def test_response_content_type_with_options(client):
    with hip.Server(json_response_with_content_type_options) as server:
        response = client.get(server.url)

    assert response.content == {"message": "hello"}


def test_response_invalid_content_type(client):
    with hip.Server(invalid_content_type) as server:
        response = client.get(server.url)

    assert response.body == b"hello"


def test_response_with_json_suffix(client):
    with hip.Server(application_problem_json_response) as server:
        response = client.get(server.url)

    assert response.status_code == 403
    assert response.content == {"detail": "Forbidden"}


def test_response_with_unregistered_media_type(client):
    with hip.Server(application_octet_stream_response) as server:
        response = client.get(server.url)

    assert isinstance(response.content, hip.Binary)
    assert response.body == b"\x00\x01\x02"


def test_get_with_invalid_scheme(client):
    with pytest.raises(ValueError):
        client.get("nope://www.example.com")


def test_redirect(client):
    with hip.Server(redirect) as server:
        r = client.get(server.url + "redirect")
        assert r.status_code == 200
        assert r.body == b"hello, world!"


def redirect_to_invalid_url(request):
    return hip.Response(
        302,
        headers={"Location": "http://example.com:abc"},
    )


def test_redirect_to_invalid_url(client):
    with hip.Server(redirect_to_invalid_url) as server:
        response = client.get(server.url + "redirect")

        assert response.status_code == 302
        assert response.body == b""


def gzip_response(request):
    assert request.headers["Accept-Encoding"] == "gzip"
    return hip.Response(
        200,
        headers={
            "Content-Type": "text/plain",
            "Content-Encoding": "gzip",
        },
        content=gzip.compress(b"Hello, world."),
    )


def test_client_receives_gzip_response(client):
    with hip.Server(gzip_response) as server:
        response = client.get(server.url)

    assert response.body == b"Hello, world."


def test_client_receives_mixed_case_gzip_response(client):
    def app(request):
        return hip.Response(
            200,
            headers={
                "Content-Type": "text/plain",
                "Content-Encoding": "GZip",
            },
            content=gzip.compress(b"Hello, world."),
        )

    with hip.Server(app) as server:
        response = client.get(server.url)

    assert response.body == b"Hello, world."


def test_client_streams_gzip_response(client):
    with (
        hip.Server(gzip_response) as server,
        client.stream("GET", server.url) as response,
    ):
        assert response.read(5) == b"Hello"
        assert response.read(5) == b", wor"
        assert response.read(5) == b"ld."
        assert response.read(5) == b""
        assert response.read(5) == b""


def test_client_rejects_truncated_gzip_response(client):
    def app(request):
        content = gzip.compress(b"Hello, world.")[:-8]
        return hip.Response(
            200,
            headers={
                "Content-Type": "text/plain",
                "Content-Encoding": "gzip",
            },
            content=content,
        )

    with (
        hip.Server(app) as server,
        pytest.raises(ValueError, match=r"Invalid gzip response content\."),
    ):
        client.get(server.url)


def test_client_rejects_invalid_gzip_response(client):
    def app(request):
        return hip.Response(
            200,
            headers={
                "Content-Type": "text/plain",
                "Content-Encoding": "gzip",
            },
            content=b"not gzip content",
        )

    with (
        hip.Server(app) as server,
        pytest.raises(ValueError, match=r"Invalid gzip response content\."),
    ):
        client.get(server.url)


def test_client_streams_gzip_response_in_multiple_chunks(client):
    source = random.Random(0).randbytes(20_000)
    gzipped = gzip.compress(source)
    assert len(gzipped) > 8192

    def app(request):
        return hip.Response(
            200,
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Encoding": "gzip",
            },
            content=gzipped,
        )

    with (
        hip.Server(app) as server,
        client.stream("GET", server.url) as response,
    ):
        assert response.read() == source
