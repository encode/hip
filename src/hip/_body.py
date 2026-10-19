import io
import zlib

from ._parsers import HTTPParser
from ._streams import Stream

__all__ = ["HTTPStream", "GZipStream"]


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


class GZipStream(Stream):
    def __init__(self, stream: Stream):
        self._stream = stream
        # Adding 16 enables gzip header and trailer handling.
        self._decoder = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
        self._finished = False
        self._buffer = bytearray()

    def read(self, size=-1) -> bytes:
        while (size < 0 or len(self._buffer) < size) and not self._finished:
            compressed = self._stream.read(8192)

            try:
                if compressed:
                    decoded = self._decoder.decompress(compressed)
                else:
                    decoded = self._decoder.flush()
            except zlib.error as exc:
                raise ValueError("Invalid gzip response content.") from exc

            if not compressed:
                if not self._decoder.eof:
                    raise ValueError("Invalid gzip response content.")
                self._finished = True

            self._buffer.extend(decoded)
        if size < 0:
            output = bytes(self._buffer)
            self._buffer.clear()
        else:
            output = bytes(self._buffer[:size])
            del self._buffer[:size]

        return output

    def close(self) -> None:
        self._stream.close()
