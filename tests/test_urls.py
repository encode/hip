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


def test_url_escaping():
    url = httpx.URL("https://example.com/path to here?search=🦋")
    assert str(url) == "https://example.com/path%20to%20here?search=%F0%9F%A6%8B"


def test_url_already_escaped():
    url = httpx.URL("https://example.com/path%20to%20here?search=%F0%9F%A6%8B")
    assert str(url) == "https://example.com/path%20to%20here?search=%F0%9F%A6%8B"


def test_url_components():
    url = httpx.URL(scheme="https", host="example.com", path="/")
    assert str(url) == "https://example.com/"


def test_url_properties():
    url = httpx.URL(
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
        httpx.URL("https://example.com", hostname="api.example.com")


def test_url_constructor_invalid_kwarg_type():
    msg = "Argument 'port' must be int but got str"
    with pytest.raises(TypeError, match=msg):
        httpx.URL("https://example.com", port="443")


def test_url_constructor_accepts_byte_query():
    url = httpx.URL("https://example.com", query=b"search=httpx")
    assert str(url) == "https://example.com?search=httpx"


def test_url_rejects_invalid_type():
    msg = "Invalid type for url.  Expected str or httpx.URL, got <class 'int'>: 123"
    with pytest.raises(TypeError, match=msg):
        httpx.URL(123)


def test_url_target_includes_query():
    url = httpx.URL("https://example.com/search?query=httpx")
    assert "/search?query=httpx" == url.target


def test_url_copy_with():
    url = httpx.URL("https://www.example.com/")
    url = url.copy_with(path="/path.txt")
    assert str(url) == "https://www.example.com/path.txt"


def test_url_join():
    url = httpx.URL("https://www.example.com/test")
    assert url.join("/new/path") == "https://www.example.com/new/path"


def test_urls_are_hashable_and_comparable():
    urls = {httpx.URL("https://example.com/"): "example"}

    assert urls[httpx.URL("https://example.com/")] == "example"
    assert httpx.URL("https://example.com/") != "https://other.example.com/"


def test_url_copy_set_param():
    url = httpx.URL("https://example.com/search?a=1")
    assert str(url.copy_set_param("a", "2")) == "https://example.com/search?a=2"


def test_url_copy_append_param():
    url = httpx.URL("https://example.com/search?a=1")
    assert str(url.copy_append_param("a", "2")) == "https://example.com/search?a=1&a=2"


def test_url_copy_remove_param():
    url = httpx.URL("https://example.com/search?a=1&a=2")
    assert str(url.copy_remove_param("a")) == "https://example.com/search"


def test_url_copy_merge_params():
    url = httpx.URL("https://example.com/search?a=1")
    assert (
        str(url.copy_merge_params({"page": "2"}))
        == "https://example.com/search?a=1&page=2"
    )


def test_url_ipv4():
    url = httpx.URL("http://127.0.0.1/")
    assert str(url) == "http://127.0.0.1/"


def test_url_ipv6():
    url = httpx.URL("http://[::1]/")
    assert str(url) == "http://[::1]/"


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
