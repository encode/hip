import io

from .core.streams import Stream
from .parsers import HTTPParser

__all__ = ["HTTPStream"]


class HTTPStream(Stream):
    def __init__(self, parser: HTTPParser, is_response: bool):
        self._parser = parser
        self._is_response = is_response
        self._buffer = io.BytesIO()
        self._finished = False

    def read(self, size=-1) -> bytes:
        if self._finished:
            return b""

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
            if section == b"":
                self._finished = True
                break

        # If we've more data than requested, then push some back into the buffer.
        output = b"".join(sections)
        if size > -1 and len(output) > size:
            output, remainder = output[:size], output[size:]
            self._buffer.write(remainder)
            self._buffer.seek(0)

        return output

    def close(self) -> None:
        self._buffer.close()
        if self._is_response:
            self._parser.complete()
