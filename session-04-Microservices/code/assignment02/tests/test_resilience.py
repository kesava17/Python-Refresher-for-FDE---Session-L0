"""Tests for the resilient client: the circuit breaker opens, then recovers.

The clock is injected so the cooldown is exercised without any real sleeping, which keeps the
suite fast and deterministic.
"""

from __future__ import annotations

import httpx
import pytest

from common.client import CircuitBreaker, CircuitOpen, resilient_get

_DEAD = "http://127.0.0.1:59999/nope"  # nothing listens here, so calls fail fast


def test_circuit_opens_after_repeated_failures() -> None:
    """After the threshold of failures the breaker opens and refuses further calls."""
    clock = [0.0]
    breaker = CircuitBreaker(threshold=2, cooldown=5.0, now=lambda: clock[0])

    for _ in range(2):
        with pytest.raises(httpx.HTTPError):
            resilient_get(_DEAD, timeout=0.2, breaker=breaker, correlation_id="t", attempts=1)

    assert breaker.is_open()
    with pytest.raises(CircuitOpen):
        resilient_get(_DEAD, timeout=0.2, breaker=breaker, correlation_id="t", attempts=1)


def test_circuit_recovers_after_cooldown() -> None:
    """Once the cooldown passes, the breaker half-opens and allows a trial call again."""
    clock = [0.0]
    breaker = CircuitBreaker(threshold=1, cooldown=5.0, now=lambda: clock[0])
    with pytest.raises(httpx.HTTPError):
        resilient_get(_DEAD, timeout=0.2, breaker=breaker, correlation_id="t", attempts=1)
    assert breaker.is_open()

    clock[0] = 6.0  # cooldown elapsed
    assert not breaker.is_open()
