import hx
import pytest


def test_url():
    url = hx.URL('https://www.example.com/')
    assert str(url) == "https://www.example.com/"


def test_url_repr():
    url = hx.URL('https://www.example.com/')
    assert repr(url) == "<URL 'https://www.example.com/'>"


def test_url_params():
    url = hx.URL('https://www.example.com/', params={"a": "b", "c": "d"})
    assert str(url) == "https://www.example.com/?a=b&c=d"


def test_url_normalisation():
    url = hx.URL('https://www.EXAMPLE.com:443/path/../main')
    assert str(url) == 'https://www.example.com/main'


def test_url_relative():
    url = hx.URL('/README.md')
    assert str(url) == '/README.md'


def test_url_escaping():
    url = hx.URL('https://example.com/path to here?search=🦋')
    assert str(url) == 'https://example.com/path%20to%20here?search=%F0%9F%A6%8B'


def test_url_components():
    url = hx.URL(scheme="https", host="example.com", path="/")
    assert str(url) == 'https://example.com/'


# QueryParams

def test_queryparams():
    params = hx.QueryParams({"color": "black", "size": "medium"})
    assert str(params) == 'color=black&size=medium'


def test_queryparams_repr():
    params = hx.QueryParams({"color": "black", "size": "medium"})
    assert repr(params) == "<QueryParams 'color=black&size=medium'>"


def test_queryparams_list_of_values():
    params = hx.QueryParams({"filter": ["60GHz", "75GHz", "100GHz"]})
    assert str(params) == 'filter=60GHz&filter=75GHz&filter=100GHz'


def test_queryparams_from_str():
    params = hx.QueryParams("color=black&size=medium")
    assert str(params) == 'color=black&size=medium'


def test_queryparams_access():
    params = hx.QueryParams("sort_by=published&author=natalie")
    assert params["sort_by"] == 'published'


def test_queryparams_escaping():
    params = hx.QueryParams({"email": "user@example.com", "search": "How HTTP works!"})
    assert str(params) == 'email=user%40example.com&search=How+HTTP+works%21'


def test_queryparams_empty():
    q = hx.QueryParams({"a": ""})
    assert str(q) == "a="

    q = hx.QueryParams("a=")
    assert str(q) == "a="

    q = hx.QueryParams("a")
    assert str(q) == "a="


def test_queryparams_set():
    q = hx.QueryParams("a=123")
    q = q.copy_set("a", "456")
    assert q == hx.QueryParams("a=456")


def test_queryparams_append():
    q = hx.QueryParams("a=123")
    q = q.copy_append("a", "456")
    assert q == hx.QueryParams("a=123&a=456")


def test_queryparams_remove():
    q = hx.QueryParams("a=123")
    q = q.copy_remove("a")
    assert q == hx.QueryParams("")


def test_queryparams_merge():
    q = hx.QueryParams("a=123")
    q = q.copy_update({"b": "456"})
    assert q == hx.QueryParams("a=123&b=456")
    q = q.copy_update({"a": "000", "c": "789"})
    assert q == hx.QueryParams("a=000&b=456&c=789")


def test_queryparams_are_hashable():
    params = (
        hx.QueryParams("a=123"),
        hx.QueryParams({"a": "123"}),
        hx.QueryParams("b=456"),
        hx.QueryParams({"b": "456"}),
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
    q = hx.QueryParams(source)
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
    assert hx.QueryParams({"a": "123", "b": "456"}) == hx.QueryParams(
        [("a", "123"), ("b", "456")]
    )
    assert hx.QueryParams({"a": "123", "b": "456"}) == hx.QueryParams(
        "a=123&b=456"
    )
    assert hx.QueryParams({"a": "123", "b": "456"}) == hx.QueryParams(
        {"b": "456", "a": "123"}
    )
    assert hx.QueryParams() == hx.QueryParams({})
    assert hx.QueryParams([("a", "123"), ("a", "456")]) == hx.QueryParams(
        "a=123&a=456"
    )
    assert hx.QueryParams({"a": "123", "b": "456"}) != "invalid"

    q = hx.QueryParams([("a", "123"), ("a", "456")])
    assert hx.QueryParams(q) == q
