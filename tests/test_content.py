import httpx
import os
import tempfile
import pytest


# HTML

def test_html():
    html = httpx.HTML("<html><body>Hello, world</body></html>")

    assert str(html) == '<html><body>Hello, world</body></html>'
    assert bytes(html) == b'<html><body>Hello, world</body></html>'
    assert html.headers() == {
        "Content-Type": "text/html; charset='utf-8'",
        "Content-Length": "38",
    }


# Text

def test_text():
    text = httpx.Text("Hello, world")

    assert str(text) == 'Hello, world'
    assert bytes(text) == b'Hello, world'
    assert text.headers() == {
        "Content-Type": "text/plain; charset='utf-8'",
        "Content-Length": "12",
    }


# JSON

def test_json():
    data = httpx.JSON({'data': 123})

    assert bytes(data) == b'{"data":123}'
    assert data.headers() == {
        "Content-Type": "application/json",
        "Content-Length": "12",
    }


# Form

def test_form():
    f = httpx.Form("a=123&a=456&b=789")

    assert str(f) == "a=123&a=456&b=789"
    assert repr(f) == "<Form [('a', '123'), ('a', '456'), ('b', '789')]>"
    assert f.multi_dict() == {
        "a": ["123", "456"],
        "b": ["789"]
    }


def test_form_from_dict():
    f = httpx.Form({
        "a": ["123", "456"],
        "b": "789"
    })
    assert str(f) == "a=123&a=456&b=789"
    assert repr(f) == "<Form [('a', '123'), ('a', '456'), ('b', '789')]>"
    assert f.multi_dict() == {
        "a": ["123", "456"],
        "b": ["789"]
    }


def test_form_from_list():
    f = httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert str(f) == "a=123&a=456&b=789"
    assert repr(f) == "<Form [('a', '123'), ('a', '456'), ('b', '789')]>"
    assert f.multi_dict() == {
        "a": ["123", "456"],
        "b": ["789"]
    }


def test_empty_form():
    f = httpx.Form()
    assert str(f) == ''
    assert repr(f) == "<Form []>"
    assert f.multi_dict() == {}


def test_form_accessors():
    f = httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert "a" in f
    assert "A" not in f
    assert "c" not in f
    assert f["a"] == "123"
    assert f.get("a") == "123"
    assert f.get("nope", default=None) is None


def test_form_dict():
    f = httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert list(f.keys()) == ["a", "b"]
    assert list(f.values()) == ["123", "789"]
    assert list(f.items()) == [("a", "123"), ("b", "789")]
    assert list(f) == ["a", "b"]
    assert dict(f) == {"a": "123", "b": "789"}


def test_form_multidict():
    f = httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert f.get_list("a") == ["123", "456"]
    assert f.multi_items() == [("a", "123"), ("a", "456"), ("b", "789")]
    assert f.multi_dict() == {"a": ["123", "456"], "b": ["789"]}


def test_form_builtins():
    f = httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert len(f) == 2
    assert bool(f)
    assert hash(f)
    assert f == httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])


def test_form_copy_operations():
    f = httpx.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert f.copy_set("a", "abc") == httpx.Form([("a", "abc"), ("b", "789")])
    assert f.copy_append("a", "abc") == httpx.Form([("a", "123"), ("a", "456"), ("a", "abc"), ("b", "789")])
    assert f.copy_remove("a") == httpx.Form([("b", "789")])


def test_form_encode():
    form = httpx.Form({'email': 'address@example.com'})
    assert form['email'] == "address@example.com"

    assert bytes(form) == b"email=address%40example.com"
    assert form.headers() == {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "27",
    }


# Files

def test_files():
    f = httpx.Files()
    assert f.multi_dict() == {}
    assert repr(f) == "<Files []>"


def test_files_from_dict():
    f = httpx.Files({
        "a": [
            httpx.File("123.json"),
            httpx.File("456.json"),
        ],
        "b": httpx.File("789.json")
    })
    assert f.multi_dict() == {
        "a": [
            httpx.File("123.json"),
            httpx.File("456.json"),
        ],
        "b": [
            httpx.File("789.json"),
        ]
    }
    assert repr(f) == (
        "<Files [('a', <File '123.json'>), ('a', <File '456.json'>), ('b', <File '789.json'>)]>"
    )



def test_files_from_list():
    f = httpx.Files([
        ("a", httpx.File("123.json")),
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json"))
    ])
    assert f.multi_dict() == {
        "a": [
            httpx.File("123.json"),
            httpx.File("456.json"),
        ],
        "b": [
            httpx.File("789.json"),
        ]
    }
    assert repr(f) == (
        "<Files [('a', <File '123.json'>), ('a', <File '456.json'>), ('b', <File '789.json'>)]>"
    )


def test_files_accessors():
    f = httpx.Files([
        ("a", httpx.File("123.json")),
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json"))
    ])
    assert "a" in f
    assert "A" not in f
    assert "c" not in f
    assert f["a"] == httpx.File("123.json")
    assert f.get("a") == httpx.File("123.json")
    assert f.get("nope", default=None) is None


def test_files_dict():
    f = httpx.Files([
        ("a", httpx.File("123.json")),
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json"))
    ])
    assert list(f.keys()) == ["a", "b"]
    assert list(f.values()) == [httpx.File("123.json"), httpx.File("789.json")]
    assert list(f.items()) == [("a", httpx.File("123.json")), ("b", httpx.File("789.json"))]
    assert list(f) == ["a", "b"]
    assert dict(f) == {"a": httpx.File("123.json"), "b": httpx.File("789.json")}


def test_files_multidict():
    f = httpx.Files([
        ("a", httpx.File("123.json")),
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json"))
    ])
    assert f.get_list("a") == [
        httpx.File("123.json"),
        httpx.File("456.json"),
    ]
    assert f.multi_items() == [
        ("a", httpx.File("123.json")), 
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json")),
    ]
    assert f.multi_dict() == {
        "a": [
            httpx.File("123.json"),
            httpx.File("456.json"),
        ],
        "b": [
            httpx.File("789.json"),
        ]
    }


def test_files_builtins():
    f = httpx.Files([
        ("a", httpx.File("123.json")),
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json"))
    ])
    assert len(f) == 2
    assert bool(f)
    assert f == httpx.Files([
        ("a", httpx.File("123.json")),
        ("a", httpx.File("456.json")),
        ("b", httpx.File("789.json")),
    ])


def test_multipart():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Hello, world")
        f.seek(0)

        multipart = httpx.MultiPart(
            form={'email': 'me@example.com'},
            files={'upload': httpx.File(f.name)},
            boundary='BOUNDARY',
        )
        assert multipart.form['email'] == "me@example.com"
        assert multipart.files['upload'] == httpx.File(f.name)

        fname = os.path.basename(f.name).encode('utf-8')

        assert multipart.headers() == {
            "Content-Type": "multipart/form-data; boundary=BOUNDARY",
            "Transfer-Encoding": "chunked",
        }

        stream = multipart.open()
        content = stream.read()
        assert content == (
            b'--BOUNDARY\r\n'
            b'Content-Disposition: form-data; name="email"\r\n'
            b'\r\n'
            b'me@example.com\r\n'
            b'--BOUNDARY\r\n'
            b'Content-Disposition: form-data; name="upload"; filename="' + fname + b'"\r\n'
            b'\r\n'
            b'Hello, world\r\n'
            b'--BOUNDARY--\r\n'
        )
