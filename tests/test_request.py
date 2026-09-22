import pytest

import httpx


def test_request():
    r = httpx.Request("GET", "https://example.com")

    assert repr(r) == "<Request [GET 'https://example.com']>"
    assert r.method == "GET"
    assert repr(r.method) == "<Method GET>"
    assert r.url == "https://example.com"
    assert r.headers == {"Host": "example.com"}
    assert r.body == b""


def test_request_bytes():
    content = b"Hello, world"
    r = httpx.Request("POST", "https://example.com", content=content)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "12",
    }
    assert r.body == b"Hello, world"


def test_request_json():
    data = httpx.JSON({"msg": "Hello, world"})
    r = httpx.Request("POST", "https://example.com", content=data)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "22",
        "Content-Type": "application/json",
    }
    assert r.body == b'{"msg":"Hello, world"}'


def test_request_empty_post():
    r = httpx.Request("POST", "https://example.com")

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "0",
    }
    assert r.body == b""


@pytest.mark.parametrize("method", ["CONNECT", "OPTIONS", "TRACE"])
def test_request_supports_additional_standard_methods(method):
    r = httpx.Request(method, "https://example.com")

    assert r.method == method


def test_request_rejects_invalid_method():
    with pytest.raises(ValueError, match="Non-standard method 'INVALID METHOD'"):
        httpx.Request("INVALID METHOD", "https://example.com")


def test_request_stream_repr():
    request = httpx.Request("GET", "https://example.com")

    with request as stream:
        assert repr(stream) == "<RequestStream [GET 'https://example.com']>"
