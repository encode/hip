import pytest

import httpx


def test_response():
    r = httpx.Response(200)

    assert repr(r) == "<Response [200 OK]>"
    assert r.status_code == 200
    assert repr(r.status_code) == "<StatusCode [200 OK]>"
    assert r.status_code.is_2xx_success()
    assert r.headers == {"Content-Length": "0"}
    assert r.body == b""


def test_response_204():
    r = httpx.Response(204)

    assert repr(r) == "<Response [204 No Content]>"
    assert repr(r.content) == "<Empty>"
    assert r.status_code == 204
    assert r.headers == {}
    assert r.body == b""


def test_response_redirect():
    r = httpx.Response(302)

    assert r.status_code.is_3xx_redirect()


def test_response_client_error():
    r = httpx.Response(404)

    assert r.status_code.is_4xx_client_error()


def test_response_server_error():
    r = httpx.Response(500)

    assert r.status_code.is_5xx_server_error()


def test_response_bytes():
    content = b"Hello, world"
    r = httpx.Response(200, content=content)

    assert repr(r) == "<Response [200 OK]>"
    assert repr(r.content) == "<Binary b'Hello, world'>"
    assert r.headers == {
        "Content-Length": "12",
    }
    assert r.body == b"Hello, world"


def test_response_json():
    data = httpx.JSON({"msg": "Hello, world"})
    r = httpx.Response(200, content=data)

    assert repr(r) == "<Response [200 OK]>"
    assert r.headers == {
        "Content-Length": "22",
        "Content-Type": "application/json",
    }
    assert r.body == b'{"msg":"Hello, world"}'


def test_response_with_invalid_code():
    with pytest.raises(ValueError, match="Invalid status code 80"):
        httpx.Response(80)


def test_response_stream_repr():
    response = httpx.Response(200)

    with response as stream:
        assert repr(stream) == "<ResponseStream [200 OK]>"
