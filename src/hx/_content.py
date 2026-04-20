import copy
import json
import os
import typing

from ._streams import Stream, ByteStream, FileStream, MultiPartStream
from ._headers import Headers, parse_opts_header
from ._urlencode import urldecode, urlencode

__all__ = [
    "Binary",
    "Content",
    "Empty",
    # Request Content Types
    "Form",
    "File",
    "Files",
    "JSON",
    "MultiPart",
    # Response Content Types
    "Text",
    "HTML",
]

# https://github.com/nginx/nginx/blob/master/conf/mime.types
_content_types = {
    ".json": "application/json",
    ".js": "application/javascript",
    ".html": "text/html",
    ".css": "text/css",
    ".png": "image/png",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
}


class Content:
    def open(self) -> Stream:
        raise NotImplementedError()

    def headers(self) -> Headers:
        raise NotImplementedError()

    @classmethod
    def parse(self, stream: Stream) -> 'Content':
        raise NotImplementedError()

    def __bytes__(self):
        raise TypeError(f"Content {self.__class__.__name__} does not support a bytes interface.")


class Form(typing.Mapping[str, str], Content):
    """
    HTML form data, as an immutable multi-dict.
    Form parameters, as a multi-dict.
    """

    def __init__(
        self,
        form: (
            typing.Mapping[str, str | typing.Sequence[str]]
            | typing.Sequence[tuple[str, str]]
            | str
            | None
        ) = None,
    ) -> None:
        d: dict[str, list[str]] = {}

        if form is None:
            d = {}
        elif isinstance(form, str):
            d = urldecode(form)
        elif isinstance(form, typing.Mapping):
            # Convert dict inputs like:
            #    {"a": "123", "b": ["456", "789"]}
            # To dict inputs where values are always lists, like:
            #    {"a": ["123"], "b": ["456", "789"]}
            d = {k: [v] if isinstance(v, str) else list(v) for k, v in form.items()}
        else:
            # Convert list inputs like:
            #     [("a", "123"), ("a", "456"), ("b", "789")]
            # To a dict representation, like:
            #     {"a": ["123", "456"], "b": ["789"]}
            for k, v in form:
                d.setdefault(k, []).append(v)

        self._dict = d
        self._content = str(self).encode("ascii")

    # Content API

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_length = len(self._content)
        return Headers({
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": f"{content_length}",
        })

    def __bytes__(self) -> bytes:
        return self._content

    # Dict operations

    def keys(self) -> typing.KeysView[str]:
        return self._dict.keys()

    def values(self) -> typing.ValuesView[str]:
        return {k: v[0] for k, v in self._dict.items()}.values()

    def items(self) -> typing.ItemsView[str, str]:
        return {k: v[0] for k, v in self._dict.items()}.items()

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key in self._dict:
            return self._dict[key][0]
        return default

    # Multi-dict operations

    def multi_items(self) -> list[tuple[str, str]]:
        multi_items: list[tuple[str, str]] = []
        for k, v in self._dict.items():
            multi_items.extend([(k, i) for i in v])
        return multi_items

    def multi_dict(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self._dict.items()}

    def get_list(self, key: str) -> list[str]:
        return list(self._dict.get(key, []))

    # Update operations

    def copy_set(self, key: str, value: str) -> "Form":
        d = self.multi_dict()
        d[key] = [value]
        return Form(d)

    def copy_append(self, key: str, value: str) -> "Form":
        d = self.multi_dict()
        d[key] = d.get(key, []) + [value]
        return Form(d)

    def copy_remove(self, key: str) -> "Form":
        d = self.multi_dict()
        d.pop(key, None)
        return Form(d)

    # Accessors & built-ins

    def __getitem__(self, key: str) -> str:
        return self._dict[key][0]

    def __contains__(self, key: typing.Any) -> bool:
        return key in self._dict

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._dict)

    def __bool__(self) -> bool:
        return bool(self._dict)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Form) and
            sorted(self.multi_items()) == sorted(other.multi_items())
        )

    def __str__(self) -> str:
        return urlencode(self.multi_dict())

    def __repr__(self) -> str:
        return f"<Form {self.multi_items()!r}>"


class File(Content):
    """
    Wrapper class used for files in uploads and multipart requests.
    """

    def __init__(self, path: str):
        self._path = path

    def name(self) -> str:
        return os.path.basename(self._path)

    def open(self) -> Stream:
        return FileStream(self._path)

    def headers(self) -> Headers:
        content_length = os.path.getsize(self._path)

        _, ext = os.path.splitext(self._path)
        content_type = _content_types.get(ext, "application/octet-stream")
        if content_type.startswith('text/'):
            content_type += "; charset='utf-8'"

        return Headers({
            "Content-Type": f"{content_type}",
            "Content-Length": f"{content_length}",
        })

    def __lt__(self, other: typing.Any) -> bool:
        return isinstance(other, File) and other._path < self._path

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, File) and other._path == self._path

    def __repr__(self) -> str:
        return f"<File {self._path!r}>"


class Files(typing.Mapping[str, File], Content):
    """
    File parameters, as a multi-dict.
    """

    def __init__(
        self,
        files: (
            typing.Mapping[str, File | typing.Sequence[File]]
            | typing.Sequence[tuple[str, File]]
            | None
        ) = None,
        boundary: str = ''
    ) -> None:
        d: dict[str, list[File]] = {}

        if files is None:
            d = {}
        elif isinstance(files, typing.Mapping):
            d = {k: [v] if isinstance(v, File) else list(v) for k, v in files.items()}
        else:
            d = {}
            for k, v in files:
                d.setdefault(k, []).append(v)

        self._dict = d
        self._boundary = boundary or os.urandom(16).hex()

    # Standard dict interface
    def keys(self) -> typing.KeysView[str]:
        return self._dict.keys()

    def values(self) -> typing.ValuesView[File]:
        return {k: v[0] for k, v in self._dict.items()}.values()

    def items(self) -> typing.ItemsView[str, File]:
        return {k: v[0] for k, v in self._dict.items()}.items()

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key in self._dict:
            return self._dict[key][0]
        return None

    # Multi dict interface
    def multi_items(self) -> list[tuple[str, File]]:
        multi_items: list[tuple[str, File]] = []
        for k, v in self._dict.items():
            multi_items.extend([(k, i) for i in v])
        return multi_items

    def multi_dict(self) -> dict[str, list[File]]:
        return {k: list(v) for k, v in self._dict.items()}

    def get_list(self, key: str) -> list[File]:
        return list(self._dict.get(key, []))

    # Content interface
    def open(self) -> Stream:
        return MultiPart(files=self).open()

    def headers(self) -> Headers:
        content_type = f"multipart/form-data; boundary={self._boundary}"
        return Headers({
            "Content-Type": f"{content_type}",
            "Transfer-Encoding": "chunked",
        })

    # Builtins
    def __getitem__(self, key: str) -> File:
        return self._dict[key][0]

    def __contains__(self, key: typing.Any) -> bool:
        return key in self._dict

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._dict)

    def __bool__(self) -> bool:
        return bool(self._dict)
 
    def __eq__(self, other: typing.Any) -> bool:
        return (
            isinstance(other, Files) and
            sorted(self.multi_items()) == sorted(other.multi_items())
        )

    def __repr__(self) -> str:
        return f"<Files {self.multi_items()!r}>"


class JSON(Content):
    def __init__(self, data: typing.Any, source: bytes | None = None) -> None:
        self._data = data
        self._content = json.dumps(
            self._data,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False
        ).encode("utf-8") if source is None else source

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_type = "application/json"
        content_length = len(self._content)
        return Headers({
            "Content-Type": f"{content_type}",
            "Content-Length": f"{content_length}",
        })

    @classmethod
    def parse(self, stream: Stream) -> 'Content':
        source = stream.read()
        data = json.loads(source)
        return JSON(data, source)

    # Return the underlying data. Copied to ensure immutability.
    @property
    def value(self) -> typing.Any:
        return copy.deepcopy(self._data)

    # dict and list style accessors, eg. for casting.
    def keys(self) -> typing.KeysView[str]:
        return self._data.keys()

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: typing.Any) -> typing.Any:
        return copy.deepcopy(self._data[key])

    # Built-ins.
    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, JSON):
            return self._data == other._data
        return self._data == other

    def __str__(self) -> str:
        return self._content.decode('utf-8')

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
        return Headers({
            "Content-Type": f"{content_type}",
            "Content-Length": f"{content_length}",
        })

    @classmethod
    def parse(self, stream: Stream) -> Content:
        source = stream.read()
        text = source.decode('utf-8')
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
        return Headers({
            "Content-Type": f"{content_type}",
            "Content-Length": f"{content_length}",
        })

    @classmethod
    def parse(self, stream: Stream) -> Content:
        source = stream.read()
        text = source.decode('utf-8')
        return HTML(text, source)

    def __str__(self) -> str:
        return self._text

    def __bytes__(self) -> bytes:
        return self._content

    def __repr__(self) -> str:
        return f"<HTML {self._text!r}>"


class Binary(Content):
    def __init__(self, content: bytes | None) -> None:
        self._content = b'' if (content is None) else content

    def open(self) -> Stream:
        return ByteStream(self._content)

    def headers(self) -> Headers:
        content_length = len(self._content)
        return Headers({
            "Content-Length": f"{content_length}"
        })

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
        return ByteStream(b'')

    def headers(self) -> Headers:
        return Headers()

    def __bytes__(self) -> bytes:
        return b''

    def __repr__(self) -> str:
        return f"<Empty>"


class MultiPart(Content):
    def __init__(
        self,
        form: (
            Form
            | typing.Mapping[str, str | typing.Sequence[str]]
            | typing.Sequence[tuple[str, str]]
            | str
            | None
        ) = None,
        files: (
            Files
            | typing.Mapping[str, File | typing.Sequence[File]]
            | typing.Sequence[tuple[str, File]]
            | None
        ) = None,
        boundary: str | None = None
    ):
        self._form = form if isinstance(form , Form) else Form(form)
        self._files = files if isinstance(files, Files) else Files(files)
        self._boundary = os.urandom(16).hex() if boundary is None else boundary

    @property
    def form(self) -> Form:
        return self._form

    @property
    def files(self) -> Files:
        return self._files

    def open(self) -> Stream:
        form = [(key, value) for key, value in self._form.items()]
        files = [(key, file._path) for key, file in self._files.items()]
        return MultiPartStream(form, files, boundary=self._boundary)

    def headers(self) -> Headers:
        return Headers({
            "Content-Type": f"multipart/form-data; boundary={self._boundary}",
            "Transfer-Encoding": "chunked",
        })

    def __repr__(self) -> str:
        return f"<MultiPart form={self._form.multi_items()!r}, files={self._files.multi_items()!r}>"


def select_media(choices: dict[str, type[Content]], content_type: str) -> type[Content]:
    # Eg. multipart/form-data; boundary=398hjiun98jhhi87g98h76g8
    ct, _ = parse_opts_header(content_type)
    # Eg. application/json
    main, _, subtype = ct.partition('/')

    if '+' in subtype:
        # RFC 6839. Eg. application/schema+json
        _, _, subtype = subtype.partition('+')

    primary = choices.get(f'{main}/{subtype}')
    if primary is not None:
        return primary

    secondary = choices.get(f'{main}/*')
    if secondary is not None:
        return secondary

    return choices["*/*"]
