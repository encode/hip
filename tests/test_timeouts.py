import hip

import pytest


def test_timeout_not_expired():
    with hip.timeout(5.0):
        hip.sleep(0.0)


def test_timeout_expired():
    with hip.timeout(0.0):
        with pytest.raises(TimeoutError):
            hip.sleep(0.0)


def test_no_timeout_set():
    hip.sleep(0.0)
