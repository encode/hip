class BytesParser:
    """
    A parser following the Sans-IO design pattern. 

    Provides parsing operations for "read some data" and
    "read some data up until a fixed delimiter".

    Used by the HTTP parsing to handle parsing the different
    sections of the request and response.
    """

    def __init__(self):
        self._buffer = bytearray()
        self._closed = False
        self._cursor = 0

    def read_some(self, max_size: int) -> bytes | None:
        """
        Returns up to `max_size` bytes.
        Returns b'' to indicate the end of the stream.
        Removes the returned data from the buffer.

        Returns `None` to indicate feed required.
        """
        if not self._buffer:
            if self._closed:
                return b''
            return None

        read, unread = self._buffer[:max_size], self._buffer[max_size:]
        self._buffer = bytearray(unread)
        return bytes(read)


    def read_until(self, marker: bytes, max_size: int) -> bytes | None:
        """
        Returns data up to and excluding the designated `marker`.
        Returns at most `max_size` bytes.
        Removes both the returned data and the marker from the buffer.

        Returns `None` to indicate feed required.

        Raises a `ParseError` if the marker cannot be found.
        """
        if self._cursor >= len(self._buffer):
            if self._closed:
                raise ...
            return None

        start_point = self._cursor
        end_point = self._cursor + max_size + len(marker)
        idx = self._buffer.find(marker, start_point, end_point)
        if idx < 0:
            self._cursor += max_size
            return None

        read, unread = self._buffer[:idx], self._buffer[idx + len(marker):]
        self._buffer = bytearray(unread)
        self._cursor = 0
        return bytes(read)

    def feed(self, data: bytes) -> None:
        """
        Feed `data` bytes to the parser.
        Feed b'' to indicate the end of the stream.
        """
        if data:
            if self._closed:
                raise ValueError('Attempted to feed data to a closed parser.')
            self._buffer.extend(data)
        else:
            self._closed = True

    # def read_is_eof(self) -> bool | None:
    #     """
    #     Returns True to indicate the end of the stream.
    #     Returns False to indicate the st
    #     Does not remove any data from the buffer.
    
    #     Returns `None` to indicate feed required.
    #     """
