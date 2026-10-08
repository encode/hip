import re

import pytest

import hip


def test_url():
    url = hip.URL("https://www.example.com/")
    assert str(url) == "https://www.example.com/"


def test_url_repr():
    url = hip.URL("https://www.example.com/")
    assert repr(url) == "<URL 'https://www.example.com/'>"


def test_url_params():
    url = hip.URL("https://www.example.com/", params={"a": "b", "c": "d"})
    assert str(url) == "https://www.example.com/?a=b&c=d"


def test_url_normalisation():
    url = hip.URL("https://www.EXAMPLE.com:443/./path/../main")
    assert str(url) == "https://www.example.com/main"


def test_url_relative():
    url = hip.URL("/README.md")
    assert str(url) == "/README.md"


def test_url_rejects_absolute_url_path_without_leading_slash():
    msg = "For absolute URLs, path must be empty or begin with '/'"
    with pytest.raises(ValueError, match=msg):
        hip.URL(scheme="https", host="example.com", path="relative")


def test_url_rejects_relative_path_starting_with_double_slash():
    msg = "Relative URLs cannot have a path starting with '//'"
    with pytest.raises(ValueError, match=msg):
        hip.URL(path="//relative/path")


def test_url_rejects_relative_path_starting_with_colon():
    msg = "Relative URLs cannot have a path starting with ':'"
    with pytest.raises(ValueError, match=msg):
        hip.URL(path=":relative")


def test_url_escaping():
    url = hip.URL("https://example.com/path to here?search=🦋")
    assert str(url) == "https://example.com/path%20to%20here?search=%F0%9F%A6%8B"


def test_url_already_escaped():
    url = hip.URL("https://example.com/path%20to%20here?search=%F0%9F%A6%8B")
    assert str(url) == "https://example.com/path%20to%20here?search=%F0%9F%A6%8B"


def test_url_components():
    url = hip.URL(scheme="https", host="example.com", path="/")
    assert str(url) == "https://example.com/"


def test_url_properties():
    url = hip.URL(
        "HTTPS://jo%40email.com:a%20secret@muller.de:1234/pa%20th?search=ab#anchorlink"
    )

    assert url.scheme == "https"
    assert url.username == "jo@email.com"
    assert url.password == "a secret"
    assert url.userinfo == b"jo%40email.com:a%20secret"
    assert url.host == "muller.de"
    assert url.netloc == "muller.de:1234"
    assert url.port == 1234
    assert url.path == "/pa th"
    assert url.query == b"search=ab"
    assert url.fragment == "anchorlink"
    assert url.is_absolute_url
    assert not url.is_relative_url


def test_url_constructor_invalid_kwarg():
    msg = "'hostname' is an invalid keyword argument for URL()"
    with pytest.raises(TypeError, match=msg):
        hip.URL("https://example.com", hostname="api.example.com")


def test_url_constructor_invalid_kwarg_type():
    msg = "Argument 'port' must be int but got str"
    with pytest.raises(TypeError, match=msg):
        hip.URL("https://example.com", port="443")


def test_url_constructor_accepts_byte_query():
    url = hip.URL("https://example.com", query=b"search=hip")
    assert str(url) == "https://example.com?search=hip"


def test_url_rejects_invalid_type():
    msg = "Invalid type for url.  Expected str or hip.URL, got <class 'int'>: 123"
    with pytest.raises(TypeError, match=msg):
        hip.URL(123)


def test_url_target_includes_query():
    url = hip.URL("https://example.com/search?query=hip")
    assert "/search?query=hip" == url.target


def test_url_constructor_rejects_invalid_scheme():
    msg = "Invalid URL component 'scheme'"
    with pytest.raises(ValueError, match=msg):
        hip.URL(scheme="1http")


def test_url_rejects_too_long_url():
    url = "https://example.com/" + ("a" * 65536)
    msg = "URL too long!"
    with pytest.raises(ValueError, match=msg):
        hip.URL(url)


def test_url_rejects_non_printable_ascii_character():
    msg = "Invalid non-printable ASCII character in URL, '\\n' at position 24."
    with pytest.raises(ValueError, match=re.escape(msg)):
        hip.URL("https://example.com/path\nname")


def test_url_constructor_accepts_netloc():
    url = hip.URL(netloc="example.com:8080")
    assert url.host == "example.com"
    assert url.port == 8080
    assert str(url) == "//example.com:8080"


def test_url_constructor_builds_userinfo_from_username_and_password():
    url = hip.URL(
        host="example.com", port=8080, username="user@example.com", password="a secret"
    )
    assert url.userinfo == b"user%40example.com:a%20secret"


def test_url_constructor_accepts_raw_path():
    url = hip.URL(host="example.com", raw_path=b"/search?query=hip")
    assert url.path == "/search"
    assert url.query == b"query=hip"


def test_url_constructor_accepts_raw_path_without_query():
    url = hip.URL(host="example.com", raw_path=b"/search")
    assert url.path == "/search"
    assert url.query == b""
    assert str(url) == "//example.com/search"


def test_url_constructor_rejects_too_long_component():
    msg = "URL component 'path' too long"
    with pytest.raises(ValueError, match=msg):
        hip.URL(path="a" * 65537)


def test_url_constructor_rejects_non_printable_ascii_component():
    msg = "Invalid non-printable ASCII character in URL path component, '\\n' at position 7."
    with pytest.raises(ValueError, match=re.escape(msg)):
        hip.URL(path="/search\nresults")


def test_url_copy_with():
    url = hip.URL("https://www.example.com/")
    url = url.copy_with(path="/path.txt")
    assert str(url) == "https://www.example.com/path.txt"


def test_url_join():
    url = hip.URL("https://www.example.com/test")
    assert url.join("/new/path") == "https://www.example.com/new/path"


def test_urls_are_hashable_and_comparable():
    urls = {hip.URL("https://example.com/"): "example"}

    assert urls[hip.URL("https://example.com/")] == "example"
    assert hip.URL("https://example.com/") != "https://other.example.com/"


def test_url_copy_set_param():
    url = hip.URL("https://example.com/search?a=1")
    assert str(url.copy_set_param("a", "2")) == "https://example.com/search?a=2"


def test_url_copy_append_param():
    url = hip.URL("https://example.com/search?a=1")
    assert str(url.copy_append_param("a", "2")) == "https://example.com/search?a=1&a=2"


def test_url_copy_remove_param():
    url = hip.URL("https://example.com/search?a=1&a=2")
    assert str(url.copy_remove_param("a")) == "https://example.com/search"


def test_url_copy_merge_params():
    url = hip.URL("https://example.com/search?a=1")
    assert (
        str(url.copy_merge_params({"page": "2"}))
        == "https://example.com/search?a=1&page=2"
    )


def test_url_ipv4():
    url = hip.URL("http://127.0.0.1/")
    assert str(url) == "http://127.0.0.1/"


def test_url_rejects_invalid_ipv4_address():
    msg = re.escape("Invalid IPv4 address: '999.999.999.999'")
    with pytest.raises(ValueError, match=msg):
        hip.URL(host="999.999.999.999")


def test_url_ipv6():
    url = hip.URL("http://[::1]/")
    assert str(url) == "http://[::1]/"


def test_url_constructor_escapes_ipv6_host():
    url = hip.URL(scheme="http", host="::1")
    assert str(url) == "http://[::1]"


def test_url_rejects_invalid_ipv6_address():
    msg = re.escape("Invalid IPv6 address: '[not-an-ip]'")
    with pytest.raises(ValueError, match=msg):
        hip.URL(host="[not-an-ip]")


# QueryParams


def test_queryparams():
    params = hip.QueryParams({"color": "black", "size": "medium"})
    assert str(params) == "color=black&size=medium"


def test_queryparams_repr():
    params = hip.QueryParams({"color": "black", "size": "medium"})
    assert repr(params) == "<QueryParams 'color=black&size=medium'>"


def test_queryparams_list_of_values():
    params = hip.QueryParams({"filter": ["60GHz", "75GHz", "100GHz"]})
    assert str(params) == "filter=60GHz&filter=75GHz&filter=100GHz"


def test_queryparams_from_str():
    params = hip.QueryParams("color=black&size=medium")
    assert str(params) == "color=black&size=medium"


def test_queryparams_access():
    params = hip.QueryParams("sort_by=published&author=natalie")
    assert params["sort_by"] == "published"


def test_queryparams_escaping():
    params = hip.QueryParams({"email": "user@example.com", "search": "How HTTP works!"})
    assert str(params) == "email=user%40example.com&search=How+HTTP+works%21"


def test_queryparams_empty():
    q = hip.QueryParams({"a": ""})
    assert str(q) == "a="

    q = hip.QueryParams("a=")
    assert str(q) == "a="

    q = hip.QueryParams("a")
    assert str(q) == "a="


def test_queryparams_set():
    q = hip.QueryParams("a=123")
    q = q.copy_set("a", "456")
    assert q == hip.QueryParams("a=456")


def test_queryparams_append():
    q = hip.QueryParams("a=123")
    q = q.copy_append("a", "456")
    assert q == hip.QueryParams("a=123&a=456")


def test_queryparams_remove():
    q = hip.QueryParams("a=123")
    q = q.copy_remove("a")
    assert q == hip.QueryParams("")


def test_queryparams_merge():
    q = hip.QueryParams("a=123")
    q = q.copy_update({"b": "456"})
    assert q == hip.QueryParams("a=123&b=456")
    q = q.copy_update({"a": "000", "c": "789"})
    assert q == hip.QueryParams("a=000&b=456&c=789")


def test_queryparams_are_hashable():
    params = (
        hip.QueryParams("a=123"),
        hip.QueryParams({"a": "123"}),
        hip.QueryParams("b=456"),
        hip.QueryParams({"b": "456"}),
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
    q = hip.QueryParams(source)
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
    assert hip.QueryParams({"a": "123", "b": "456"}) == hip.QueryParams(
        [("a", "123"), ("b", "456")]
    )
    assert hip.QueryParams({"a": "123", "b": "456"}) == hip.QueryParams("a=123&b=456")
    assert hip.QueryParams({"a": "123", "b": "456"}) == hip.QueryParams(
        {"b": "456", "a": "123"}
    )
    assert hip.QueryParams() == hip.QueryParams({})
    assert hip.QueryParams([("a", "123"), ("a", "456")]) == hip.QueryParams(
        "a=123&a=456"
    )
    assert hip.QueryParams({"a": "123", "b": "456"}) != "invalid"

    q = hip.QueryParams([("a", "123"), ("a", "456")])
    assert hip.QueryParams(q) == q


# Tests previously from 'test_urlencode.py'...
# If we can clean these up without reducing coverage, we should.


def test_urlencode():
    qs = "a=name%40example.com&a=456&b=7+8+9&c"
    qp = hip.QueryParams(qs)
    assert qp.multi_dict() == {
        "a": ["name@example.com", "456"],
        "b": ["7 8 9"],
        "c": [""],
    }


def test_urldecode():
    qp = hip.QueryParams({"a": ["name@example.com", "456"], "b": ["7 8 9"], "c": [""]})
    qs = str(qp)
    assert qs == "a=name%40example.com&a=456&b=7+8+9&c="


def test_urlencode_empty():
    qs = ""
    qp = hip.QueryParams(qs)
    assert qp.multi_dict() == {}


def test_urldecode_empty():
    qp = hip.QueryParams({})
    qs = str(qp)
    assert qs == ""
