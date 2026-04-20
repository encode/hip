import hx
import pytest


def test_headers_from_dict():
    headers = hx.Headers({
        'Content-Length': '1024',
        'Content-Type': 'text/plain; charset=utf-8',
    })
    assert headers['Content-Length'] == '1024'
    assert headers['Content-Type'] == 'text/plain; charset=utf-8'


def test_headers_from_list():
    headers = hx.Headers([
        ('Location', 'https://www.example.com'),
        ('Set-Cookie', 'session_id=3498jj489jhb98jn'),
    ])
    assert headers['Location'] == 'https://www.example.com'
    assert headers['Set-Cookie'] == 'session_id=3498jj489jhb98jn'


def test_header_keys():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert list(h.keys()) == ["Accept", "User-Agent"]


def test_header_values():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert list(h.values()) == ["*/*", "python/hx"]


def test_header_items():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert list(h.items()) == [("Accept", "*/*"), ("User-Agent", "python/hx")]


def test_header_get():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert h.get("User-Agent") == "python/hx"
    assert h.get("user-agent") == "python/hx"
    assert h.get("missing") is None


def test_header_copy_set():
    h = hx.Headers({"Expires": "0"})
    h = h.copy_set("Expires", "Wed, 21 Oct 2015 07:28:00 GMT")
    assert h == hx.Headers({"Expires": "Wed, 21 Oct 2015 07:28:00 GMT"})

    h = hx.Headers({"Expires": "0"})
    h = h.copy_set("expires", "Wed, 21 Oct 2015 07:28:00 GMT")
    assert h == hx.Headers({"Expires": "Wed, 21 Oct 2015 07:28:00 GMT"})


def test_header_copy_remove():
    h = hx.Headers({"Accept": "*/*"})
    h = h.copy_remove("Accept")
    assert h == hx.Headers({})

    h = hx.Headers({"Accept": "*/*"})
    h = h.copy_remove("accept")
    assert h == hx.Headers({})


def test_header_getitem():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert h["User-Agent"] == "python/hx"
    assert h["user-agent"] == "python/hx"
    with pytest.raises(KeyError):
        h["missing"]


def test_header_contains():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert "User-Agent" in h
    assert "user-agent" in h
    assert "missing" not in h


def test_header_bool():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert bool(h)
    h = hx.Headers()
    assert not bool(h)


def test_header_iter():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert [k for k in h] == ["Accept", "User-Agent"]


def test_header_len():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert len(h) == 2


def test_header_repr():
    h = hx.Headers({"Accept": "*/*", "User-Agent": "python/hx"})
    assert repr(h) == "<Headers {'Accept': '*/*', 'User-Agent': 'python/hx'}>"


def test_header_invalid_name():
    with pytest.raises(ValueError):
        hx.Headers({"Accept\n": "*/*"})


def test_header_invalid_value():
    with pytest.raises(ValueError):
        hx.Headers({"Accept": "*/*\n"})
