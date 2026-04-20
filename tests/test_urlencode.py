import hx


def test_urlencode():
    qs = "a=name%40example.com&a=456&b=7+8+9&c"
    d = hx.urldecode(qs)
    assert d == {
        "a": ["name@example.com", "456"],
        "b": ["7 8 9"],
        "c": [""]
    }


def test_urldecode():
    d = {
        "a": ["name@example.com", "456"],
        "b": ["7 8 9"],
        "c": [""]
    }
    qs = hx.urlencode(d)
    assert qs == "a=name%40example.com&a=456&b=7+8+9&c="


def test_urlencode_empty():
    qs = ""
    d = hx.urldecode(qs)
    assert d == {}


def test_urldecode_empty():
    d = {}
    qs = hx.urlencode(d)
    assert qs == ""
