import pytest

import hip


def test_bytes_parser():
    p = hip.parsers.BytesParser()

    # Feed some data, then half-close the buffer.
    p.feed(b"abc")
    p.feed(b"defg")
    p.feed(b"")

    # Test a sequence of reads.
    assert p.read_some(10) == b"abcdefg"
    assert p.read_some(10) == b""
    assert p.read_some(10) == b""


def test_bytes_parser_partial_reads():
    p = hip.parsers.BytesParser()

    # Feed some data, then half-close the buffer.
    p.feed(b"abc")
    p.feed(b"defg")
    p.feed(b"")

    # Test a sequence of reads.
    with pytest.raises(ValueError):
        p.read_some(0)

    assert p.read_some(1) == b"a"
    assert p.read_some(2) == b"bc"
    assert p.read_some(3) == b"def"
    assert p.read_some(4) == b"g"
    assert p.read_some(5) == b""
    assert p.read_some(6) == b""


def test_bytes_parser_feed_after_close():
    p = hip.parsers.BytesParser()

    # Feed some data, then half-close the buffer.
    p.feed(b"abc")
    p.feed(b"defg")
    p.feed(b"")

    # Buffer is half-closed, cannot feed any more data.
    with pytest.raises(ValueError):
        assert p.feed(b"...")


def test_bytes_parser_need_feeds():
    p = hip.parsers.BytesParser()

    # Parser needs some I/O feeding to the buffer
    assert p.read_some(1) is None
    p.feed(b"abc")
    assert p.read_some(1) == b"a"
    assert p.read_some(2) == b"bc"

    # Parser needs some I/O feeding to the buffer
    assert p.read_some(3) is None
    p.feed(b"defg")

    assert p.read_some(3) == b"def"
    assert p.read_some(4) == b"g"

    # Parser needs some I/O feeding to the buffer
    assert p.read_some(5) is None
    p.feed(b"")
    assert p.read_some(5) == b""
    assert p.read_some(6) == b""


def test_bytes_parser_read_until():
    p = hip.parsers.BytesParser()

    # Feed some data, then half-close the buffer.
    p.feed(b"GET / HTTP/1.0\r\n")
    p.feed(b"Host: example.com\r\n")
    p.feed(b"Connection: close\r\n")
    p.feed(b"\r\n")
    p.feed(b"")

    # Parse the different components of the requst
    request = p.read_until(b"\r\n", max_size=5_000)
    headers = p.read_until(b"\r\n\r\n", max_size=10_000)
    content = p.read_some(max_size=10_000)

    assert request == b"GET / HTTP/1.0"
    assert headers == b"Host: example.com\r\nConnection: close"
    assert content == p.read_some(max_size=10_000)


def test_bytes_parser_read_until_needs_feeds():
    p = hip.parsers.BytesParser()

    # Parser needs some I/O feeding to the buffer
    assert p.read_until(b"\r\n", max_size=5_000) is None
    p.feed(b"GET / HTTP/1.0\r\n")
    # Request line is complete
    assert p.read_until(b"\r\n", max_size=5_000) == b"GET / HTTP/1.0"

    # Parser needs some I/O feeding to the buffer
    assert p.read_until(b"\r\n\r\n", max_size=10_000) is None
    p.feed(b"Host: example.com\r\n")
    # Parser needs some I/O feeding to the buffer
    assert p.read_until(b"\r\n\r\n", max_size=10_000) is None
    p.feed(b"Connection: close\r\n")
    # Parser needs some I/O feeding to the buffer
    assert p.read_until(b"\r\n\r\n", max_size=10_000) is None
    p.feed(b"\r\n")
    # Request headers are complete
    assert (
        p.read_until(b"\r\n\r\n", max_size=10_000)
        == b"Host: example.com\r\nConnection: close"
    )

    # Parser needs some I/O feeding to the buffer
    assert p.read_some(max_size=10_000) is None
    p.feed(b"")
    # Reques is complete
    assert p.read_some(max_size=10_000) == b""


def test_bytes_parser_read_until_exception():
    p = hip.parsers.BytesParser()
    p.feed(b"")

    with pytest.raises(hip.parsers.ParseError):
        assert p.read_until(b"\r\n", max_size=5_000)
