import pytest

import hip


def test_headers_from_dict():
    headers = hip.Headers(
        {
            "Content-Length": "1024",
            "Content-Type": "text/plain; charset=utf-8",
        }
    )
    assert headers["Content-Length"] == "1024"
    assert headers["Content-Type"] == "text/plain; charset=utf-8"


def test_headers_from_list():
    headers = hip.Headers(
        [
            ("Location", "https://www.example.com"),
            ("Set-Cookie", "session_id=3498jj489jhb98jn"),
        ]
    )
    assert headers["Location"] == "https://www.example.com"
    assert headers["Set-Cookie"] == "session_id=3498jj489jhb98jn"


def test_header_keys():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert list(h.keys()) == ["Accept", "User-Agent"]


def test_header_values():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert list(h.values()) == ["*/*", "python/hip"]


def test_header_items():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert list(h.items()) == [("Accept", "*/*"), ("User-Agent", "python/hip")]


def test_header_get():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert h.get("User-Agent") == "python/hip"
    assert h.get("user-agent") == "python/hip"
    assert h.get("missing") is None


def test_header_copy_set():
    h = hip.Headers({"Expires": "0"})
    h = h.copy_set("Expires", "Wed, 21 Oct 2015 07:28:00 GMT")
    assert h == hip.Headers({"Expires": "Wed, 21 Oct 2015 07:28:00 GMT"})

    h = hip.Headers({"Expires": "0"})
    h = h.copy_set("expires", "Wed, 21 Oct 2015 07:28:00 GMT")
    assert h == hip.Headers({"Expires": "Wed, 21 Oct 2015 07:28:00 GMT"})


def test_header_copy_remove():
    h = hip.Headers({"Accept": "*/*"})
    h = h.copy_remove("Accept")
    assert h == hip.Headers({})

    h = hip.Headers({"Accept": "*/*"})
    h = h.copy_remove("accept")
    assert h == hip.Headers({})


def test_header_getitem():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert h["User-Agent"] == "python/hip"
    assert h["user-agent"] == "python/hip"
    with pytest.raises(KeyError):
        h["missing"]


def test_header_contains():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert "User-Agent" in h
    assert "user-agent" in h
    assert "missing" not in h


def test_header_bool():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert bool(h)
    h = hip.Headers()
    assert not bool(h)


def test_header_iter():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert [k for k in h] == ["Accept", "User-Agent"]


def test_header_len():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert len(h) == 2


def test_header_repr():
    h = hip.Headers({"Accept": "*/*", "User-Agent": "python/hip"})
    assert repr(h) == "<Headers {'Accept': '*/*', 'User-Agent': 'python/hip'}>"


def test_header_invalid_name():
    with pytest.raises(ValueError):
        hip.Headers({"Accept\n": "*/*"})


def test_header_invalid_value():
    with pytest.raises(ValueError):
        hip.Headers({"Accept": "*/*\n"})


def test_header_empty_value():
    with pytest.raises(ValueError):
        hip.Headers({""})


def test_headers_not_equal_to_unrelated_type():
    assert hip.Headers() != object()
