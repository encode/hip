import json
import hx
import pytest


def echo(request):
    response = hx.Response(200, content=hx.JSON({
        'method': str(request.method),
        'query-params': dict(request.url.params.items()),
        'content-type': request.headers.get('Content-Type'),
        'json': json.loads(request.body) if request.body else None,
    }))
    return response


@pytest.fixture
def server():
    with hx.Server(echo) as server:
        yield server


def test_get(server):
    r = hx.get(server.url)
    assert r.status_code == 200
    assert r.content == {
        'method': 'GET',
        'query-params': {},
        'content-type': None,
        'json': None,
    }


def test_post(server):
    data = hx.JSON({"data": 123})
    r = hx.post(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        'method': 'POST',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_put(server):
    data = hx.JSON({"data": 123})
    r = hx.put(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        'method': 'PUT',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_patch(server):
    data = hx.JSON({"data": 123})
    r = hx.patch(server.url, content=data)
    assert r.status_code == 200
    assert r.content == {
        'method': 'PATCH',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_delete(server):
    r = hx.delete(server.url)
    assert r.status_code == 200
    assert r.content == {
        'method': 'DELETE',
        'query-params': {},
        'content-type': None,
        'json': None,
    }
