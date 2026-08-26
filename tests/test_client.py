import json

import pytest

import httpx


def redirect(request):
    if request.url.path == "/redirect":
        return httpx.Response(302, headers={"Location": "/"})
    return httpx.Response(200, content=httpx.Text("hello, world!"))


def echo(request):
    response = httpx.Response(
        200,
        content=httpx.JSON(
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
    return httpx.Response(
        200,
        headers={"Content-Type": 'application/json; title="hello\\"world"'},
        content=b'{"message":"hello"}',
    )


def invalid_content_type(request):
    return httpx.Response(
        200,
        headers={"Content-Type": "; charset=utf-8"},
        content=b"hello",
    )


@pytest.fixture
def client():
    with httpx.Client() as client:
        yield client


@pytest.fixture
def server():
    with httpx.Server(echo) as server:
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
    data = httpx.JSON({"data": 123})
    r = client.post(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        "method": "POST",
        "query-params": {},
        "content-type": "application/json",
        "json": {"data": 123},
    }


def test_put(client, server):
    data = httpx.JSON({"data": 123})
    r = client.put(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        "method": "PUT",
        "query-params": {},
        "content-type": "application/json",
        "json": {"data": 123},
    }


def test_patch(client, server):
    data = httpx.JSON({"data": 123})
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


def test_keepalive(client, server):
    first = client.get(server.url)
    second = client.get(server.url)

    assert first.status_code == 200
    assert second.status_code == 200


def test_response_content_type_with_options(client):
    with httpx.Server(json_response_with_content_type_options) as server:
        response = client.get(server.url)

    assert response.content == {"message": "hello"}


def test_response_invalid_content_type(client):
    with httpx.Server(invalid_content_type) as server:
        response = client.get(server.url)

    assert response.body == b"hello"


def test_get_with_invalid_scheme(client):
    with pytest.raises(ValueError):
        client.get("nope://www.example.com")


def test_redirect(client):
    with httpx.Server(redirect) as server:
        r = client.get(server.url + "redirect")
        assert r.status_code == 200
        assert r.body == b"hello, world!"


def redirect_to_invalid_url(request):
    return httpx.Response(
        302,
        headers={"Location": "http://example.com:abc"},
    )


def test_redirect_to_invalid_url(client):
    with httpx.Server(redirect_to_invalid_url) as server:
        response = client.get(server.url + "redirect")

        assert response.status_code == 302
        assert response.body == b""
