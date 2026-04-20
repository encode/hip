import hx
import pytest


def test_request():
    r = hx.Request("GET", "https://example.com")

    assert repr(r) == "<Request [GET 'https://example.com']>"
    assert r.method == "GET"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com"
    }
    assert r.body == b""


def test_request_bytes():
    content = b"Hello, world"
    r = hx.Request("POST", "https://example.com", content=content)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "12",
    }
    assert r.body == b"Hello, world"


def test_request_json():
    data = hx.JSON({"msg": "Hello, world"})
    r = hx.Request("POST", "https://example.com", content=data)

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
    r = hx.Request("POST", "https://example.com")

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "0",
    }
    assert r.body == b''
