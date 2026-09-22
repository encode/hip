import re

import pytest

import httpx


def test_url():
    url = httpx.URL("https://www.example.com/")
    assert str(url) == "https://www.example.com/"


def test_url_repr():
    url = httpx.URL("https://www.example.com/")
    assert repr(url) == "<URL 'https://www.example.com/'>"


def test_url_params():
    url = httpx.URL("https://www.example.com/", params={"a": "b", "c": "d"})
    assert str(url) == "https://www.example.com/?a=b&c=d"


def test_url_normalisation():
    url = httpx.URL("https://www.EXAMPLE.com:443/./path/../main")
    assert str(url) == "https://www.example.com/main"


def test_url_relative():
    url = httpx.URL("/README.md")
    assert str(url) == "/README.md"


def test_url_rejects_absolute_url_path_without_leading_slash():
    msg = "For absolute URLs, path must be empty or begin with '/'"
    with pytest.raises(ValueError, match=msg):
        httpx.URL(scheme="https", host="example.com", path="relative")


def test_url_rejects_relative_path_starting_with_double_slash():
    msg = "Relative URLs cannot have a path starting with '//'"
    with pytest.raises(ValueError, match=msg):
        httpx.URL(path="//relative/path")


def test_url_rejects_relative_path_starting_with_colon():
    msg = "Relative URLs cannot have a path starting with ':'"
    with pytest.raises(ValueError, match=msg):
        httpx.URL(path=":relative")


def test_url_escaping():
    url = httpx.URL("https://example.com/path to here?search=🦋")
    assert str(url) == "https://example.com/path%20to%20here?search=%F0%9F%A6%8B"


def test_url_already_escaped():
    url = httpx.URL("https://example.com/path%20to%20here?search=%F0%9F%A6%8B")
    assert str(url) == "https://example.com/path%20to%20here?search=%F0%9F%A6%8B"


def test_url_components():
    url = httpx.URL(scheme="https", host="example.com", path="/")
    assert str(url) == "https://example.com/"


def test_url_constructor_rejects_invalid_scheme():
    msg = "Invalid URL component 'scheme'"
    with pytest.raises(ValueError, match=msg):
        httpx.URL(scheme="1http")


def test_url_rejects_too_long_url():
    url = "https://example.com/" + ("a" * 65536)
    msg = "URL too long!"
    with pytest.raises(ValueError, match=msg):
        httpx.URL(url)


def test_url_rejects_non_printable_ascii_character():
    msg = "Invalid non-printable ASCII character in URL, '\\n' at position 24."
    with pytest.raises(ValueError, match=re.escape(msg)):
        httpx.URL("https://example.com/path\nname")


def test_url_constructor_accepts_netloc():
    url = httpx.URL(netloc="example.com:8080")
    assert url.host == "example.com"
    assert url.port == 8080
    assert str(url) == "//example.com:8080"


def test_url_constructor_builds_userinfo_from_username_and_password():
    url = httpx.URL(
        host="example.com", port=8080, username="user@example.com", password="a secret"
    )
    assert url.userinfo == b"user%40example.com:a%20secret"


def test_url_constructor_accepts_raw_path():
    url = httpx.URL(host="example.com", raw_path=b"/search?query=httpx")
    assert url.path == "/search"
    assert url.query == b"query=httpx"


def test_url_constructor_accepts_raw_path_without_query():
    url = httpx.URL(host="example.com", raw_path=b"/search")
    assert url.path == "/search"
    assert url.query == b""
    assert str(url) == "//example.com/search"


def test_url_constructor_rejects_too_long_component():
    msg = "URL component 'path' too long"
    with pytest.raises(ValueError, match=msg):
        httpx.URL(path="a" * 65537)


def test_url_constructor_rejects_non_printable_ascii_component():
    msg = "Invalid non-printable ASCII character in URL path component, '\\n' at position 7."
    with pytest.raises(ValueError, match=re.escape(msg)):
        httpx.URL(path="/search\nresults")


def test_url_copy_with():
    url = httpx.URL("https://www.example.com/")
    url = url.copy_with(path="/path.txt")
    assert str(url) == "https://www.example.com/path.txt"


def test_url_ipv4():
    url = httpx.URL("http://127.0.0.1/")
    assert str(url) == "http://127.0.0.1/"


def test_url_rejects_invalid_ipv4_address():
    msg = re.escape("Invalid IPv4 address: '999.999.999.999'")
    with pytest.raises(ValueError, match=msg):
        httpx.URL(host="999.999.999.999")


def test_url_ipv6():
    url = httpx.URL("http://[::1]/")
    assert str(url) == "http://[::1]/"


def test_url_constructor_escapes_ipv6_host():
    url = httpx.URL(scheme="http", host="::1")
    assert str(url) == "http://[::1]"


def test_url_rejects_invalid_ipv6_address():
    msg = re.escape("Invalid IPv6 address: '[not-an-ip]'")
    with pytest.raises(ValueError, match=msg):
        httpx.URL(host="[not-an-ip]")


# QueryParams


def test_queryparams():
    params = httpx.QueryParams({"color": "black", "size": "medium"})
    assert str(params) == "color=black&size=medium"


def test_queryparams_repr():
    params = httpx.QueryParams({"color": "black", "size": "medium"})
    assert repr(params) == "<QueryParams 'color=black&size=medium'>"


def test_queryparams_list_of_values():
    params = httpx.QueryParams({"filter": ["60GHz", "75GHz", "100GHz"]})
    assert str(params) == "filter=60GHz&filter=75GHz&filter=100GHz"


def test_queryparams_from_str():
    params = httpx.QueryParams("color=black&size=medium")
    assert str(params) == "color=black&size=medium"


def test_queryparams_access():
    params = httpx.QueryParams("sort_by=published&author=natalie")
    assert params["sort_by"] == "published"


def test_queryparams_escaping():
    params = httpx.QueryParams(
        {"email": "user@example.com", "search": "How HTTP works!"}
    )
    assert str(params) == "email=user%40example.com&search=How+HTTP+works%21"


def test_queryparams_empty():
    q = httpx.QueryParams({"a": ""})
    assert str(q) == "a="

    q = httpx.QueryParams("a=")
    assert str(q) == "a="

    q = httpx.QueryParams("a")
    assert str(q) == "a="


def test_queryparams_set():
    q = httpx.QueryParams("a=123")
    q = q.copy_set("a", "456")
    assert q == httpx.QueryParams("a=456")


def test_queryparams_append():
    q = httpx.QueryParams("a=123")
    q = q.copy_append("a", "456")
    assert q == httpx.QueryParams("a=123&a=456")


def test_queryparams_remove():
    q = httpx.QueryParams("a=123")
    q = q.copy_remove("a")
    assert q == httpx.QueryParams("")


def test_queryparams_merge():
    q = httpx.QueryParams("a=123")
    q = q.copy_update({"b": "456"})
    assert q == httpx.QueryParams("a=123&b=456")
    q = q.copy_update({"a": "000", "c": "789"})
    assert q == httpx.QueryParams("a=000&b=456&c=789")


def test_queryparams_are_hashable():
    params = (
        httpx.QueryParams("a=123"),
        httpx.QueryParams({"a": "123"}),
        httpx.QueryParams("b=456"),
        httpx.QueryParams({"b": "456"}),
    )

    assert len(set(params)) == 2


@pytest.mark.parametrize(
    "source",
    [
        "a=123&a=456&b=789",
        {"a": ["123", "456"], "b": "789"},
        {"a": ("123", "456"), "b": "789"},
        [("a", "123"), ("a", "456"), ("b", "789")],
        (("a", "123"), ("a", "456"), ("b", "789")),
    ],
)
def test_queryparams_misc(source):
    q = httpx.QueryParams(source)
    assert "a" in q
    assert "A" not in q
    assert "c" not in q
    assert q["a"] == "123"
    assert q.get("a") == "123"
    assert q.get("nope", default=None) is None
    assert q.get_list("a") == ["123", "456"]
    assert bool(q)

    assert list(q.keys()) == ["a", "b"]
    assert list(q.values()) == ["123", "789"]
    assert list(q.items()) == [("a", "123"), ("b", "789")]
    assert len(q) == 2
    assert list(q) == ["a", "b"]
    assert dict(q) == {"a": "123", "b": "789"}
    assert str(q) == "a=123&a=456&b=789"
    assert httpx.QueryParams({"a": "123", "b": "456"}) == httpx.QueryParams(
        [("a", "123"), ("b", "456")]
    )
    assert httpx.QueryParams({"a": "123", "b": "456"}) == httpx.QueryParams(
        "a=123&b=456"
    )
    assert httpx.QueryParams({"a": "123", "b": "456"}) == httpx.QueryParams(
        {"b": "456", "a": "123"}
    )
    assert httpx.QueryParams() == httpx.QueryParams({})
    assert httpx.QueryParams([("a", "123"), ("a", "456")]) == httpx.QueryParams(
        "a=123&a=456"
    )
    assert httpx.QueryParams({"a": "123", "b": "456"}) != "invalid"

    q = httpx.QueryParams([("a", "123"), ("a", "456")])
    assert httpx.QueryParams(q) == q
