import pytest

import hip


def test_timeout_not_expired():
    with hip.backends.timeout(5.0):
        hip.backends.sleep(0.0)


def test_timeout_expired():
    with hip.backends.timeout(0.0), pytest.raises(TimeoutError):
        hip.backends.sleep(0.0)


def test_no_timeout_set():
    hip.backends.sleep(0.0)
