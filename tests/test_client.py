import json
import httpx
import pytest


def echo(request):
    response = httpx.Response(200, content=httpx.JSON({
        'method': str(request.method),
        'query-params': dict(request.url.params.items()),
        'content-type': request.headers.get('Content-Type'),
        'json': json.loads(request.body) if request.body else None,
    }))
    return response


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
    assert r.body == b'{"method":"GET","query-params":{},"content-type":null,"json":null}'
    assert r.content == {
        "method": "GET",
        "query-params": {},
        "content-type": None,
        "json": None
    }


def test_post(client, server):
    data = httpx.JSON({"data": 123})
    r = client.post(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        'method': 'POST',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_put(client, server):
    data = httpx.JSON({"data": 123})
    r = client.put(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        'method': 'PUT',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_patch(client, server):
    data = httpx.JSON({"data": 123})
    r = client.patch(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        'method': 'PATCH',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_delete(client, server):
    r = client.delete(server.url)
    assert r.status_code == 200
    assert r.content == {
        'method': 'DELETE',
        'query-params': {},
        'content-type': None,
        'json': None,
    }


def test_request(client, server):
    r = client.request("GET", server.url)
    assert r.status_code == 200
    assert r.content == {
        'method': 'GET',
        'query-params': {},
        'content-type': None,
        'json': None,
    }


def test_stream(client, server):
    with client.stream("GET", server.url) as r:
        assert r.status_code == 200
        body = r.read()
        assert json.loads(body) == {
            'method': 'GET',
            'query-params': {},
            'content-type': None,
            'json': None,
        }


def test_get_with_invalid_scheme(client):
    with pytest.raises(ValueError):
        client.get("nope://www.example.com")
