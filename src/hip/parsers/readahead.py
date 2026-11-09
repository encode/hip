from .._streams import Stream
from .exceptions import ProtocolError


class ReadAheadParser:
    """
    A buffered I/O stream, with methods for read-ahead parsing.
    """

    def __init__(self, stream: Stream) -> None:
        self._buffer = b""
        self._stream = stream
        self._chunk_size = 4096

    def _read_some(self) -> bytes:
        if self._buffer:
            ret, self._buffer = self._buffer, b""
            return ret
        return self._stream.read(self._chunk_size)

    def _push_back(self, buffer):
        assert self._buffer == b""
        self._buffer = buffer

    def read(self, size: int) -> bytes:
        """
        Read and return up to 'size' bytes from the stream, with I/O buffering provided.

        * Returns b'' to indicate connection close.
        """
        buffer = bytearray()
        while len(buffer) < size:
            chunk = self._read_some()
            if not chunk:
                break
            buffer.extend(chunk)

        if len(buffer) > size:
            buffer, push_back = buffer[:size], buffer[size:]
            self._push_back(bytes(push_back))
        return bytes(buffer)

    def read_until(
        self,
        marker: bytes,
        max_size: int,
        exc_text: str,
        allow_empty_eof: bool = False,
    ) -> bytes:
        """
        Read and return bytes from the stream, delimited by marker.

        * The marker is not included in the return bytes.
        * The marker is consumed from the I/O stream.
        * Raises `EOFError` if the stream closes before any bytes are read and
          `allow_empty_eof` is set.
        * Raises `ProtocolError` if the stream closes before the marker otherwise.
        * Raises `ProtocolError` if marker did not occur within 'max_size + len(marker)' bytes.
        """
        buffer = bytearray()
        while len(buffer) <= max_size:
            chunk = self._read_some()
            if not chunk:
                # EOF is only clean if no part of the line has arrived.
                if allow_empty_eof and not buffer:
                    raise EOFError
                # stream closed before marker found.
                raise ProtocolError(f"Stream closed early {exc_text}.")
            start_search = max(len(buffer) - len(marker), 0)
            buffer.extend(chunk)
            index = buffer.find(marker, start_search)

            if index > max_size:
                # marker was found, though 'max_size' exceeded.
                raise ProtocolError(f"Exceeded maximum size {exc_text}")
            elif index >= 0:
                endindex = index + len(marker)
                self._push_back(bytes(buffer[endindex:]))
                return bytes(buffer[:index])

        raise ProtocolError(f"Exceeded maximum size {exc_text}")
