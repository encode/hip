from __future__ import annotations

import typing

from ._queryparams import QueryParams
from ._urlencode import unquote
from ._urlparse import urlparse

__all__ = ["URL"]


class URL:
    """
    The components of a URL are broken down like this:

       https://jo%40email.com:a%20secret@müller.de:1234/pa%20th?search=ab#anchorlink
    [scheme]   [  username  ] [password] [ host ][port][ path ] [ query ] [fragment]
               [       userinfo        ] [   netloc   ][    raw_path    ]

    Note that:

    * `url.scheme` is normalized to always be lowercased.

    * `url.host` is normalized to always be lowercased. Internationalized domain
      names are represented in unicode, without IDNA encoding applied. For instance:

      url = hip.URL("http://中国.icom.museum")
      assert url.host == "中国.icom.museum"
      url = hip.URL("http://xn--fiqs8s.icom.museum")
      assert url.host == "中国.icom.museum"

    * `url.raw_host` is normalized to always be lowercased, and is IDNA encoded.

      url = hip.URL("http://中国.icom.museum")
      assert url.raw_host == b"xn--fiqs8s.icom.museum"
      url = hip.URL("http://xn--fiqs8s.icom.museum")
      assert url.raw_host == b"xn--fiqs8s.icom.museum"

    * `url.port` is either None or an integer. URLs that include the default port for
      "http", "https", "ws", "wss", and "ftp" schemes have their port
      normalized to `None`.

      assert hip.URL("http://example.com") == hip.URL("http://example.com:80")
      assert hip.URL("http://example.com").port is None
      assert hip.URL("http://example.com:80").port is None

    * `url.userinfo` is raw bytes, without URL escaping. Usually you'll want to work
      with `url.username` and `url.password` instead, which handle the URL escaping.

    * `url.raw_path` is raw bytes of both the path and query, without URL escaping.
      This portion is used as the target when constructing HTTP requests. Usually you'll
      want to work with `url.path` instead.

    * `url.query` is raw bytes, without URL escaping. A URL query string portion can
      only be properly URL escaped when decoding the parameter names and values
      themselves.
    """

    def __init__(self, url: URL | str = "", **kwargs: typing.Any) -> None:
        if kwargs:
            allowed = {
                "scheme": str,
                "username": str,
                "password": str,
                "userinfo": bytes,
                "host": str,
                "port": int,
                "netloc": str,
                "path": str,
                "query": bytes,
                "raw_path": bytes,
                "fragment": str,
                "params": object,
            }

            # Perform type checking for all supported keyword arguments.
            for key, value in kwargs.items():
                if key not in allowed:
                    message = f"{key!r} is an invalid keyword argument for URL()"
                    raise TypeError(message)
                if value is not None and not isinstance(value, allowed[key]):
                    expected = allowed[key].__name__
                    seen = type(value).__name__
                    message = f"Argument {key!r} must be {expected} but got {seen}"
                    raise TypeError(message)
                if isinstance(value, bytes):
                    kwargs[key] = value.decode("ascii")

            if "params" in kwargs:
                # Replace any "params" keyword with the raw "query" instead.
                #
                # Ensure that empty params use `kwargs["query"] = None` rather
                # than `kwargs["query"] = ""`, so that generated URLs do not
                # include an empty trailing "?".
                params = kwargs.pop("params")
                kwargs["query"] = None if not params else str(QueryParams(params))

        if isinstance(url, str):
            self._uri_reference = urlparse(url, **kwargs)
        elif isinstance(url, URL):
            self._uri_reference = url._uri_reference.copy_with(**kwargs)
        else:
            raise TypeError(
                "Invalid type for url.  Expected str or hip.URL,"
                f" got {type(url)}: {url!r}"
            )

    @property
    def scheme(self) -> str:
        """
        The URL scheme, such as "http", "https".
        Always normalised to lowercase.
        """
        return self._uri_reference.scheme

    @property
    def userinfo(self) -> bytes:
        """
        The URL userinfo as a raw bytestring.
        For example: b"jo%40email.com:a%20secret".
        """
        return self._uri_reference.userinfo.encode("ascii")

    @property
    def username(self) -> str:
        """
        The URL username as a string, with URL decoding applied.
        For example: "jo@email.com"
        """
        userinfo = self._uri_reference.userinfo
        return unquote(userinfo.partition(":")[0])

    @property
    def password(self) -> str:
        """
        The URL password as a string, with URL decoding applied.
        For example: "a secret"
        """
        userinfo = self._uri_reference.userinfo
        return unquote(userinfo.partition(":")[2])

    @property
    def host(self) -> str:
        """
        The URL host as a string.
        Always normalized to lowercase. Possibly IDNA encoded.

        Examples:

        url = hip.URL("http://www.EXAMPLE.org")
        assert url.host == "www.example.org"

        url = hip.URL("http://中国.icom.museum")
        assert url.host == "xn--fiqs8s"

        url = hip.URL("http://xn--fiqs8s.icom.museum")
        assert url.host == "xn--fiqs8s"

        url = hip.URL("https://[::ffff:192.168.0.1]")
        assert url.host == "::ffff:192.168.0.1"
        """
        return self._uri_reference.host

    @property
    def port(self) -> int | None:
        """
        The URL port as an integer.

        Note that the URL class performs port normalization as per the WHATWG spec.
        Default ports for "http", "https", "ws", "wss", and "ftp" schemes are always
        treated as `None`.

        For example:

        assert hip.URL("http://www.example.com") == hip.URL("http://www.example.com:80")
        assert hip.URL("http://www.example.com:80").port is None
        """
        return self._uri_reference.port

    @property
    def netloc(self) -> str:
        """
        Either `<host>` or `<host>:<port>` as bytes.
        Always normalized to lowercase, and IDNA encoded.

        This property may be used for generating the value of a request
        "Host" header.
        """
        return self._uri_reference.netloc

    @property
    def path(self) -> str:
        """
        The URL path as a string. Excluding the query string, and URL decoded.

        For example:

        url = hip.URL("https://example.com/pa%20th")
        assert url.path == "/pa th"
        """
        path = self._uri_reference.path or "/"
        return unquote(path)

    @property
    def query(self) -> bytes:
        """
        The URL query string, as raw bytes, excluding the leading b"?".

        This is necessarily a bytewise interface, because we cannot
        perform URL decoding of this representation until we've parsed
        the keys and values into a QueryParams instance.

        For example:

        url = hip.URL("https://example.com/?filter=some%20search%20terms")
        assert url.query == b"filter=some%20search%20terms"
        """
        query = self._uri_reference.query or ""
        return query.encode("ascii")

    @property
    def params(self) -> QueryParams:
        """
        The URL query parameters, neatly parsed and packaged into an immutable
        multidict representation.
        """
        return QueryParams(self._uri_reference.query)

    @property
    def target(self) -> str:
        """
        The complete URL path and query string as raw bytes.
        Used as the target when constructing HTTP requests.

        For example:

        GET /users?search=some%20text HTTP/1.1
        Host: www.example.org
        Connection: close
        """
        target = self._uri_reference.path or "/"
        if self._uri_reference.query is not None:
            target += "?" + self._uri_reference.query
        return target

    @property
    def fragment(self) -> str:
        """
        The URL fragments, as used in HTML anchors.
        As a string, without the leading '#'.
        """
        return unquote(self._uri_reference.fragment or "")

    @property
    def is_absolute_url(self) -> bool:
        """
        Return `True` for absolute URLs such as 'http://example.com/path',
        and `False` for relative URLs such as '/path'.
        """
        # We don't use `.is_absolute` from `rfc3986` because it treats
        # URLs with a fragment portion as not absolute.
        # What we actually care about is if the URL provides
        # a scheme and hostname to which connections should be made.
        return bool(self._uri_reference.scheme and self._uri_reference.host)

    @property
    def is_relative_url(self) -> bool:
        """
        Return `False` for absolute URLs such as 'http://example.com/path',
        and `True` for relative URLs such as '/path'.
        """
        return not self.is_absolute_url

    def copy_with(self, **kwargs: typing.Any) -> URL:
        """
        Copy this URL, returning a new URL with some components altered.
        Accepts the same set of parameters as the components that are made
        available via properties on the `URL` class.

        For example:

        url = hip.URL("https://www.example.com").copy_with(
            username="jo@gmail.com", password="a secret"
        )
        assert url == "https://jo%40email.com:a%20secret@www.example.com"
        """
        return URL(self, **kwargs)

    def copy_set_param(self, key: str, value: typing.Any = None) -> URL:
        return self.copy_with(params=self.params.copy_set(key, value))

    def copy_append_param(self, key: str, value: typing.Any = None) -> URL:
        return self.copy_with(params=self.params.copy_append(key, value))

    def copy_remove_param(self, key: str) -> URL:
        return self.copy_with(params=self.params.copy_remove(key))

    def copy_merge_params(
        self,
        params: QueryParams | dict[str, str | list[str]] | list[tuple[str, str]] | None,
    ) -> URL:
        return self.copy_with(params=self.params.copy_update(params))

    def join(self, url: URL | str) -> URL:
        """
        Return an absolute URL, using this URL as the base.

        Eg.

        url = hip.URL("https://www.example.com/test")
        url = url.join("/new/path")
        assert url == "https://www.example.com/new/path"
        """
        from urllib.parse import urljoin

        return URL(urljoin(str(self), str(URL(url))))

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (URL, str)) and str(self) == str(URL(other))

    def __str__(self) -> str:
        return str(self._uri_reference)

    def __repr__(self) -> str:
        return f"<URL {str(self)!r}>"
