import contextlib
import contextvars
import time
import typing

__all__ = ["sleep", "timeout"]


_timeout_stack: contextvars.ContextVar[tuple[float, ...]] = contextvars.ContextVar(
    "timeout_context", default=()
)


@contextlib.contextmanager
def timeout(duration: float) -> typing.Iterator[None]:
    """
    A context managed timeout API.

    with timeout(1.0):
        ...
    """
    now = time.monotonic()
    until = now + duration
    stack = (until, *_timeout_stack.get())
    token = _timeout_stack.set(stack)
    try:
        yield
    finally:
        _timeout_stack.reset(token)


def get_current_timeout() -> float | None:
    stack = _timeout_stack.get()
    if not stack:
        return None
    soonest = min(stack)
    now = time.monotonic()
    remaining = soonest - now
    if remaining <= 0.0:
        raise TimeoutError()
    return remaining


def sleep(dur: float):
    """
    A `sleep()` implementation that is aware of the current timeout context.
    """
    remaining = get_current_timeout()
    if remaining is None or dur < remaining:
        time.sleep(dur)
    else:
        time.sleep(dur - remaining)
        raise TimeoutError()
