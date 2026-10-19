import pytest

import hip


def test_request():
    r = hip.Request("GET", "https://example.com")

    assert repr(r) == "<Request [GET 'https://example.com']>"
    assert r.method == "GET"
    assert repr(r.method) == "<Method GET>"
    assert r.url == "https://example.com"
    assert r.headers == {"Host": "example.com"}
    assert r.body == b""


def test_request_bytes():
    content = b"Hello, world"
    r = hip.Request("POST", "https://example.com", content=content)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "12",
    }
    assert r.body == b"Hello, world"


def test_request_json():
    data = hip.JSON({"msg": "Hello, world"})
    r = hip.Request("POST", "https://example.com", content=data)

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
    r = hip.Request("POST", "https://example.com")

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
    r = hip.Request(method, "https://example.com")

    assert r.method == method


def test_request_rejects_invalid_method():
    with pytest.raises(ValueError, match="Non-standard method 'INVALID METHOD'"):
        hip.Request("INVALID METHOD", "https://example.com")
