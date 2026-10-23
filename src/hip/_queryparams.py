from __future__ import annotations

import typing

from ._urlencode import urldecode, urlencode

__all__ = ["QueryParams"]


class QueryParams(typing.Mapping[str, str]):
    """
    URL query parameters, as a multi-dict.
    """

    def __init__(
        self,
        params: (
            QueryParams
            | dict[str, str | list[str]]
            | list[tuple[str, str]]
            | str
            | None
        ) = None,
    ) -> None:
        d: dict[str, list[str]] = {}

        if params is None:
            d = {}
        elif isinstance(params, str):
            d = urldecode(params)
        elif isinstance(params, QueryParams):
            d = params.multi_dict()
        elif isinstance(params, dict):
            # Convert dict inputs like:
            #    {"a": "123", "b": ["456", "789"]}
            # To dict inputs where values are always lists, like:
            #    {"a": ["123"], "b": ["456", "789"]}
            d = {k: [v] if isinstance(v, str) else list(v) for k, v in params.items()}
        else:
            # Convert list inputs like:
            #     [("a", "123"), ("a", "456"), ("b", "789")]
            # To a dict representation, like:
            #     {"a": ["123", "456"], "b": ["789"]}
            for k, v in params:
                d.setdefault(k, []).append(v)

        self._dict = d

    def keys(self) -> typing.KeysView[str]:
        """
        Return all the keys in the query params.

        Usage:

        q = hip.QueryParams("a=123&a=456&b=789")
        assert list(q.keys()) == ["a", "b"]
        """
        return self._dict.keys()

    def values(self) -> typing.ValuesView[str]:
        """
        Return all the values in the query params. If a key occurs more than once
        only the first item for that key is returned.

        Usage:

        q = hip.QueryParams("a=123&a=456&b=789")
        assert list(q.values()) == ["123", "789"]
        """
        return {k: v[0] for k, v in self._dict.items()}.values()

    def items(self) -> typing.ItemsView[str, str]:
        """
        Return all items in the query params. If a key occurs more than once
        only the first item for that key is returned.

        Usage:

        q = hip.QueryParams("a=123&a=456&b=789")
        assert list(q.items()) == [("a", "123"), ("b", "789")]
        """
        return {k: v[0] for k, v in self._dict.items()}.items()

    def multi_items(self) -> list[tuple[str, str]]:
        """
        Return all items in the query params. Allow duplicate keys to occur.

        Usage:

        q = hip.QueryParams("a=123&a=456&b=789")
        assert list(q.multi_items()) == [("a", "123"), ("a", "456"), ("b", "789")]
        """
        multi_items: list[tuple[str, str]] = []
        for k, v in self._dict.items():
            multi_items.extend([(k, i) for i in v])
        return multi_items

    def multi_dict(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self._dict.items()}

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """
        Get a value from the query param for a given key. If the key occurs
        more than once, then only the first value is returned.

        Usage:

        q = hip.QueryParams("a=123&a=456&b=789")
        assert q.get("a") == "123"
        """
        if key in self._dict:
            return self._dict[key][0]
        return default

    def get_list(self, key: str) -> list[str]:
        """
        Get all values from the query param for a given key.

        Usage:

        q = hip.QueryParams("a=123&a=456&b=789")
        assert q.get_list("a") == ["123", "456"]
        """
        return list(self._dict.get(key, []))

    def copy_set(self, key: str, value: str) -> QueryParams:
        """
        Return a new QueryParams instance, setting the value of a key.

        Usage:

        q = hip.QueryParams("a=123")
        q = q.set("a", "456")
        assert q == hip.QueryParams("a=456")
        """
        q = QueryParams()
        q._dict = dict(self._dict)
        q._dict[key] = [value]
        return q

    def copy_append(self, key: str, value: str) -> QueryParams:
        """
        Return a new QueryParams instance, setting or appending the value of a key.

        Usage:

        q = hip.QueryParams("a=123")
        q = q.append("a", "456")
        assert q == hip.QueryParams("a=123&a=456")
        """
        q = QueryParams()
        q._dict = dict(self._dict)
        q._dict[key] = q.get_list(key) + [value]
        return q

    def copy_remove(self, key: str) -> QueryParams:
        """
        Return a new QueryParams instance, removing the value of a key.

        Usage:

        q = hip.QueryParams("a=123")
        q = q.remove("a")
        assert q == hip.QueryParams("")
        """
        q = QueryParams()
        q._dict = dict(self._dict)
        q._dict.pop(str(key), None)
        return q

    def copy_update(
        self,
        params: (
            QueryParams | dict[str, str | list[str]] | list[tuple[str, str]] | None
        ) = None,
    ) -> QueryParams:
        """
        Return a new QueryParams instance, updated with.

        Usage:

        q = hip.QueryParams("a=123")
        q = q.copy_update({"b": "456"})
        assert q == hip.QueryParams("a=123&b=456")

        q = hip.QueryParams("a=123")
        q = q.copy_update({"a": "456", "b": "789"})
        assert q == hip.QueryParams("a=456&b=789")
        """
        q = QueryParams(params)
        q._dict = {**self._dict, **q._dict}
        return q

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return sorted(self.multi_items()) == sorted(other.multi_items())

    def __str__(self) -> str:
        return urlencode(self.multi_dict())

    def __repr__(self) -> str:
        return f"<QueryParams {str(self)!r}>"
