import io

from ._content import Content
from ._headers import Headers
from ._parsers import HTTPParser
from ._streams import Stream


__all__ = ['RequestContent', 'ResponseContent', 'HTTPStream']


class RequestContent(Content):
    def __init__(self, parser: HTTPParser):
        self._parser = parser

    def open(self) -> Stream:
        return HTTPStream(self._parser, is_response=False)

    def headers(self) -> Headers:
        return Headers()


class ResponseContent(Content):
    def __init__(self, parser: HTTPParser):
        self._parser = parser

    def open(self) -> Stream:
        return HTTPStream(self._parser, is_response=True)

    def headers(self) -> Headers:
        return Headers()


class HTTPStream(Stream):
    def __init__(self, parser: HTTPParser, is_response: bool):
        self._parser = parser
        self._is_response = is_response
        self._buffer = io.BytesIO()

    def read(self, size=-1) -> bytes:
        sections = []
        length = 0

        # If we have any data in the buffer read that and clear the buffer.
        buffered = self._buffer.read()
        if buffered:
            sections.append(buffered)
            length += len(buffered)
            self._buffer.seek(0)
            self._buffer.truncate(0)

        # Read each chunk in turn.
        while (size < 0) or (length < size):
            section = self._parser.recv_body()
            sections.append(section)
            length += len(section)
            if section == b'':
                break

        # If we've more data than requested, then push some back into the buffer.
        output = b''.join(sections)
        if size > -1 and len(output) > size:
            output, remainder = output[:size], output[size:]
            self._buffer.write(remainder)
            self._buffer.seek(0)

        return output

    def close(self) -> None:
        self._buffer.close()
        if self._is_response:
            self._parser.complete()
