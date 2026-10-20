import pytest

import hip


def test_stream():
    i = hip.Stream()
    with pytest.raises(NotImplementedError):
        i.read()

    with pytest.raises(NotImplementedError):
        i.close()

    with pytest.raises(NotImplementedError):
        i.write(b"hello")


def test_bytestream():
    data = b"abc"
    b = hip.Binary(data)

    with b.open() as s:
        assert s.read() == b"abc"

    with b.open() as s:
        assert s.read(1) == b"a"
        assert s.read(1) == b"b"
        assert s.read(1) == b"c"
        assert s.read(1) == b""


def test_filestream(tmp_path):
    path = tmp_path / "example.txt"
    path.write_bytes(b"hello world")
    f = hip.File(path)

    with f.open() as s:
        assert s.read() == b"hello world"

    with f.open() as s:
        assert s.read(5) == b"hello"
        assert s.read(5) == b" worl"
        assert s.read(5) == b"d"
        assert s.read(5) == b""

    with f.open() as s:
        assert s.read(5) == b"hello"


def test_multipartstream(tmp_path):
    path = tmp_path / "example.txt"
    path.write_bytes(b"hello world" + b"x" * 50)

    expected = b"".join(
        [
            b"--boundary\r\n",
            b'Content-Disposition: form-data; name="email"\r\n',
            b"\r\n",
            b"heya@example.com\r\n",
            b"--boundary\r\n",
            b'Content-Disposition: form-data; name="upload"; filename="example.txt"\r\n',
            b"\r\n",
            b"hello world" + (b"x" * 50) + b"\r\n",
            b"--boundary--\r\n",
        ]
    )

    form = [("email", "heya@example.com")]
    files = [("upload", hip.File(path))]
    multipart = hip.MultiPart(form, files, boundary="boundary")

    with multipart.open() as s:
        assert s.read() == expected

    with multipart.open() as s:
        assert s.read(50) == expected[:50]
        assert s.read(50) == expected[50:100]
        assert s.read(50) == expected[100:150]
        assert s.read(50) == expected[150:200]
        assert s.read(50) == expected[200:250]

    with multipart.open() as s:
        assert s.read(50) == expected[:50]
        assert s.read(50) == expected[50:100]
        assert s.read(50) == expected[100:150]
        assert s.read(50) == expected[150:200]
        s.close()  # test close during open file
