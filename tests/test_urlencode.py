import hip


def test_urlencode():
    qs = "a=name%40example.com&a=456&b=7+8+9&c"
    d = hip.urldecode(qs)
    assert d == {"a": ["name@example.com", "456"], "b": ["7 8 9"], "c": [""]}


def test_urldecode():
    d = {"a": ["name@example.com", "456"], "b": ["7 8 9"], "c": [""]}
    qs = hip.urlencode(d)
    assert qs == "a=name%40example.com&a=456&b=7+8+9&c="


def test_urlencode_empty():
    qs = ""
    d = hip.urldecode(qs)
    assert d == {}


def test_urldecode_empty():
    d = {}
    qs = hip.urlencode(d)
    assert qs == ""
