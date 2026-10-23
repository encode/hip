import copy
import json
import typing

from ._headers import Headers, parse_opts_header
from ._streams import ByteStream, Stream

__all__ = [
    "HTML",
    "JSON",
    "Binary",
    "Content",
    "Empty",
    # Response Content Types
    "Text",
]


class Content:
    def open(self) -> Stream:
        raise NotImplementedError()

    def headers(self) -> Headers:
        raise NotImplementedError()

    @classmethod
    def parse(self, stream: Stream) -> "Content":
        raise NotImplementedError()

    def __bytes__(self):
        raise TypeError(
            f"Content {self.__class__.__name__} does not support a bytes interface."
        )


class JSON(Content):
    def __init__(self, data: typing.Any, source: bytes | None = None) -> None:
        self._data = data
        self._content = (
            json.dumps(
                self._data, ensure_ascii=False, separators=(",", ":"), allow_nan=False
            ).encode("utf-8")
            if source is None
            else source
        )

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_type = "application/json"
        content_length = len(self._content)
        return Headers(
            {
                "Content-Type": f"{content_type}",
                "Content-Length": f"{content_length}",
            }
        )

    @classmethod
    def parse(self, stream: Stream) -> "Content":
        source = stream.read()
        data = json.loads(source)
        return JSON(data, source)

    # Return the underlying data. Copied to ensure immutability.
    @property
    def value(self) -> typing.Any:
        return copy.deepcopy(self._data)

    # dict and list style accessors, eg. for casting.
    def keys(self) -> typing.KeysView[str]:
        return self._data.keys()

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: typing.Any) -> typing.Any:
        return copy.deepcopy(self._data[key])

    # Built-ins.
    def __eq__(self, other: object) -> bool:
        if isinstance(other, JSON):
            return self._data == other._data
        return self._data == other

    def __str__(self) -> str:
        return self._content.decode("utf-8")

    def __bytes__(self) -> bytes:
        return self._content

    def __repr__(self) -> str:
        return f"<JSON {self._data!r}>"


class Text(Content):
    def __init__(self, text: str, source: bytes | None = None) -> None:
        self._text = text
        self._content = self._text.encode("utf-8") if source is None else source

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_type = "text/plain; charset='utf-8'"
        content_length = len(self._content)
        return Headers(
            {
                "Content-Type": f"{content_type}",
                "Content-Length": f"{content_length}",
            }
        )

    @classmethod
    def parse(self, stream: Stream) -> Content:
        source = stream.read()
        text = source.decode("utf-8")
        return Text(text, source)

    def __str__(self) -> str:
        return self._text

    def __bytes__(self) -> bytes:
        return self._content

    def __repr__(self) -> str:
        return f"<Text {self._text!r}>"


class HTML(Content):
    def __init__(self, text: str, source: bytes | None = None) -> None:
        self._text = text
        self._content = self._text.encode("utf-8") if source is None else source

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_type = "text/html; charset='utf-8'"
        content_length = len(self._content)
        return Headers(
            {
                "Content-Type": f"{content_type}",
                "Content-Length": f"{content_length}",
            }
        )

    @classmethod
    def parse(self, stream: Stream) -> Content:
        source = stream.read()
        text = source.decode("utf-8")
        return HTML(text, source)

    def __str__(self) -> str:
        return self._text

    def __bytes__(self) -> bytes:
        return self._content

    def __repr__(self) -> str:
        return f"<HTML {self._text!r}>"


class Binary(Content):
    def __init__(self, content: bytes | None) -> None:
        self._content = b"" if (content is None) else content

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_length = len(self._content)
        return Headers({"Content-Length": f"{content_length}"})

    @classmethod
    def parse(self, stream: Stream) -> Content:
        source = stream.read()
        return Binary(source)

    def __bytes__(self) -> bytes:
        return self._content

    def __repr__(self) -> str:
        return f"<Binary {self._content!r}>"


class Empty(Content):
    def __init__(self) -> None:
        pass

    def open(self) -> Stream:
        return ByteStream(b"")

    def headers(self) -> Headers:
        return Headers()

    def __bytes__(self) -> bytes:
        return b""

    def __repr__(self) -> str:
        return "<Empty>"


def select_media(choices: dict[str, type[Content]], content_type: str) -> type[Content]:
    # Eg. multipart/form-data; boundary=398hjiun98jhhi87g98h76g8
    ct, _ = parse_opts_header(content_type)
    # Eg. application/json
    main, _, subtype = ct.partition("/")

    if "+" in subtype:
        # RFC 6839. Eg. application/schema+json
        _, _, subtype = subtype.partition("+")

    primary = choices.get(f"{main}/{subtype}")
    if primary is not None:
        return primary

    secondary = choices.get(f"{main}/*")
    if secondary is not None:
        return secondary

    return choices["*/*"]
