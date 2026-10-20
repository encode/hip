import os
import tempfile

import pytest

import hip

# HTML


def test_html():
    html = hip.HTML("<html><body>Hello, world</body></html>")

    assert repr(html) == "<HTML '<html><body>Hello, world</body></html>'>"
    assert str(html) == "<html><body>Hello, world</body></html>"
    assert bytes(html) == b"<html><body>Hello, world</body></html>"
    assert html.headers() == {
        "Content-Type": "text/html; charset='utf-8'",
        "Content-Length": "38",
    }
    with html.open() as stream:
        b = stream.read()
        assert b == b"<html><body>Hello, world</body></html>"


# Text


def test_text():
    text = hip.Text("Hello, world")

    assert repr(text) == "<Text 'Hello, world'>"
    assert str(text) == "Hello, world"
    assert bytes(text) == b"Hello, world"
    assert text.headers() == {
        "Content-Type": "text/plain; charset='utf-8'",
        "Content-Length": "12",
    }
    with text.open() as stream:
        b = stream.read()
        assert b == b"Hello, world"


# JSON


def test_json():
    data = hip.JSON({"data": 123})

    assert repr(data) == "<JSON {'data': 123}>"
    assert list(data.keys()) == ["data"]
    assert len(data) == 1
    assert data["data"] == 123
    assert data == hip.JSON({"data": 123})
    assert str(data) == '{"data":123}'
    assert bytes(data) == b'{"data":123}'

    value = data.value
    value["data"] = 456

    assert data.value == {"data": 123}
    assert data.headers() == {
        "Content-Type": "application/json",
        "Content-Length": "12",
    }
    with data.open() as stream:
        b = stream.read()
        assert b == b'{"data":123}'


def test_json_unicode_serialization():
    data = hip.JSON({"name": "Çağdaş"})

    assert str(data) == '{"name":"Çağdaş"}'
    assert bytes(data) == '{"name":"Çağdaş"}'.encode()


# Form


def test_form():
    f = hip.Form("a=123&a=456&b=789")

    assert repr(f) == "<Form [('a', '123'), ('a', '456'), ('b', '789')]>"
    assert str(f) == "a=123&a=456&b=789"
    assert f.multi_dict() == {"a": ["123", "456"], "b": ["789"]}
    with f.open() as stream:
        b = stream.read()
        assert b == b"a=123&a=456&b=789"


def test_form_from_dict():
    f = hip.Form({"a": ["123", "456"], "b": "789"})
    assert str(f) == "a=123&a=456&b=789"
    assert repr(f) == "<Form [('a', '123'), ('a', '456'), ('b', '789')]>"
    assert f.multi_dict() == {"a": ["123", "456"], "b": ["789"]}


def test_form_from_list():
    f = hip.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert str(f) == "a=123&a=456&b=789"
    assert repr(f) == "<Form [('a', '123'), ('a', '456'), ('b', '789')]>"
    assert f.multi_dict() == {"a": ["123", "456"], "b": ["789"]}


def test_empty_form():
    f = hip.Form()
    assert str(f) == ""
    assert repr(f) == "<Form []>"
    assert f.multi_dict() == {}


def test_form_accessors():
    f = hip.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert "a" in f
    assert "A" not in f
    assert "c" not in f
    assert f["a"] == "123"
    assert f.get("a") == "123"
    assert f.get("nope", default=None) is None


def test_form_dict():
    f = hip.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert list(f.keys()) == ["a", "b"]
    assert list(f.values()) == ["123", "789"]
    assert list(f.items()) == [("a", "123"), ("b", "789")]
    assert list(f) == ["a", "b"]
    assert dict(f) == {"a": "123", "b": "789"}


def test_form_multidict():
    f = hip.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert f.get_list("a") == ["123", "456"]
    assert f.multi_items() == [("a", "123"), ("a", "456"), ("b", "789")]
    assert f.multi_dict() == {"a": ["123", "456"], "b": ["789"]}


def test_form_builtins():
    f = hip.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert len(f) == 2
    assert bool(f)
    assert hash(f)
    assert f == hip.Form([("a", "123"), ("a", "456"), ("b", "789")])


def test_form_copy_operations():
    f = hip.Form([("a", "123"), ("a", "456"), ("b", "789")])
    assert f.copy_set("a", "abc") == hip.Form([("a", "abc"), ("b", "789")])
    assert f.copy_append("a", "abc") == hip.Form(
        [("a", "123"), ("a", "456"), ("a", "abc"), ("b", "789")]
    )
    assert f.copy_remove("a") == hip.Form([("b", "789")])


def test_form_encode():
    form = hip.Form({"email": "address@example.com"})
    assert form["email"] == "address@example.com"

    assert bytes(form) == b"email=address%40example.com"
    assert form.headers() == {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "27",
    }


# File


def test_file():
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp:
        temp.write(b"Hello, world")
        temp.seek(0)
        file = hip.File(temp.name)
        assert file.headers() == {
            "Content-Type": "text/plain; charset='utf-8'",
            "Content-Length": "12",
        }
        assert file.name() == os.path.basename(temp.name)
        with file.open() as stream:
            b = stream.read()
            assert b == b"Hello, world"


# Files


def test_empty_files():
    files = hip.Files(boundary="BOUNDARY")
    assert files.multi_dict() == {}
    assert repr(files) == "<Files []>"
    assert files.headers() == {
        "Content-Type": "multipart/form-data; boundary=BOUNDARY",
        "Transfer-Encoding": "chunked",
    }
    with files.open() as stream:
        assert stream.read() == b"--BOUNDARY--\r\n"


def test_files_from_dict():
    f = hip.Files(
        {
            "a": [
                hip.File("123.json"),
                hip.File("456.json"),
            ],
            "b": hip.File("789.json"),
        }
    )
    assert f.multi_dict() == {
        "a": [
            hip.File("123.json"),
            hip.File("456.json"),
        ],
        "b": [
            hip.File("789.json"),
        ],
    }
    assert repr(f) == (
        "<Files [('a', <File '123.json'>), ('a', <File '456.json'>), ('b', <File '789.json'>)]>"
    )


def test_files_from_list():
    f = hip.Files(
        [
            ("a", hip.File("123.json")),
            ("a", hip.File("456.json")),
            ("b", hip.File("789.json")),
        ]
    )
    assert f.multi_dict() == {
        "a": [
            hip.File("123.json"),
            hip.File("456.json"),
        ],
        "b": [
            hip.File("789.json"),
        ],
    }
    assert repr(f) == (
        "<Files [('a', <File '123.json'>), ('a', <File '456.json'>), ('b', <File '789.json'>)]>"
    )


def test_files_accessors():
    f = hip.Files(
        [
            ("a", hip.File("123.json")),
            ("a", hip.File("456.json")),
            ("b", hip.File("789.json")),
        ]
    )
    assert "a" in f
    assert "A" not in f
    assert "c" not in f
    assert f["a"] == hip.File("123.json")
    assert f.get("a") == hip.File("123.json")
    assert f.get("nope", default=None) is None


def test_files_dict():
    f = hip.Files(
        [
            ("a", hip.File("123.json")),
            ("a", hip.File("456.json")),
            ("b", hip.File("789.json")),
        ]
    )
    assert list(f.keys()) == ["a", "b"]
    assert list(f.values()) == [hip.File("123.json"), hip.File("789.json")]
    assert list(f.items()) == [
        ("a", hip.File("123.json")),
        ("b", hip.File("789.json")),
    ]
    assert list(f) == ["a", "b"]
    assert dict(f) == {"a": hip.File("123.json"), "b": hip.File("789.json")}


def test_files_multidict():
    f = hip.Files(
        [
            ("a", hip.File("123.json")),
            ("a", hip.File("456.json")),
            ("b", hip.File("789.json")),
        ]
    )
    assert f.get_list("a") == [
        hip.File("123.json"),
        hip.File("456.json"),
    ]
    assert f.multi_items() == [
        ("a", hip.File("123.json")),
        ("a", hip.File("456.json")),
        ("b", hip.File("789.json")),
    ]
    assert f.multi_dict() == {
        "a": [
            hip.File("123.json"),
            hip.File("456.json"),
        ],
        "b": [
            hip.File("789.json"),
        ],
    }


def test_files_builtins():
    f = hip.Files(
        [
            ("a", hip.File("123.json")),
            ("a", hip.File("456.json")),
            ("b", hip.File("789.json")),
        ]
    )
    assert len(f) == 2
    assert bool(f)
    assert f == hip.Files(
        [
            ("a", hip.File("123.json")),
            ("a", hip.File("456.json")),
            ("b", hip.File("789.json")),
        ]
    )


def test_multipart():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Hello, world")
        f.seek(0)

        multipart = hip.MultiPart(
            form={"email": "me@example.com"},
            files={"upload": hip.File(f.name)},
            boundary="BOUNDARY",
        )
        assert multipart.form["email"] == "me@example.com"
        assert multipart.files["upload"] == hip.File(f.name)

        fname = os.path.basename(f.name).encode("utf-8")

        assert multipart.headers() == {
            "Content-Type": "multipart/form-data; boundary=BOUNDARY",
            "Transfer-Encoding": "chunked",
        }

        with multipart.open() as stream:
            content = stream.read()

        assert content == (
            b"--BOUNDARY\r\n"
            b'Content-Disposition: form-data; name="email"\r\n'
            b"\r\n"
            b"me@example.com\r\n"
            b"--BOUNDARY\r\n"
            b'Content-Disposition: form-data; name="upload"; filename="'
            + fname
            + b'"\r\n'
            b"\r\n"
            b"Hello, world\r\n"
            b"--BOUNDARY--\r\n"
        )


def test_multipart_repr():
    multipart = hip.MultiPart(form={"name": "Alice"})

    assert repr(multipart) == "<MultiPart form=[('name', 'Alice')], files=[]>"


# Content


def test_content():
    content = hip.Content()

    with pytest.raises(NotImplementedError):
        content.open()

    with pytest.raises(NotImplementedError):
        content.headers()

    with pytest.raises(NotImplementedError):
        content.parse(hip.Stream())

    with pytest.raises(TypeError):
        bytes(content)
