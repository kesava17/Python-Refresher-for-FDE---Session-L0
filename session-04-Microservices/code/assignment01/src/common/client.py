"""A guarded HTTP client for calls between services.

Every remote call gets a timeout, a retry with backoff for transient errors, and a simple
circuit breaker that stops calling a dependency after repeated failures and lets it recover.
This is how one service survives another being slow or down instead of hanging with it.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed


class CircuitOpen(RuntimeError):
    """Raised when the breaker is open, so the caller does not even attempt the call."""


class CircuitBreaker:
    """Track failures to a dependency; open after a threshold, and recover after a cooldown."""

    def __init__(
        self, threshold: int = 3, cooldown: float = 5.0, now: Callable[[], float] = time.monotonic
    ) -> None:
        """Configure the breaker. `now` is injectable so tests do not have to sleep."""
        self.threshold = threshold
        self.cooldown = cooldown
        self._now = now
        self._failures = 0
        self._opened_at: float | None = None

    def is_open(self) -> bool:
        """Return True while the breaker is open. After the cooldown it half-opens for a trial."""
        if self._opened_at is None:
            return False
        if self._now() - self._opened_at >= self.cooldown:
            self._opened_at = None
            self._failures = 0
            return False
        return True

    def record_success(self) -> None:
        """Reset the breaker after a successful call."""
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        """Count a failure, and open the breaker once the threshold is reached."""
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = self._now()

    def guard(self) -> None:
        """Raise `CircuitOpen` if the breaker is currently open."""
        if self.is_open():
            raise CircuitOpen("circuit is open; not calling the failing dependency")


def resilient_get(
    url: str,
    *,
    timeout: float,
    breaker: CircuitBreaker,
    correlation_id: str,
    attempts: int = 3,
) -> dict[str, Any]:
    """GET a URL with a timeout, retries, and the circuit breaker, passing the correlation id.

    Raises `CircuitOpen` immediately if the breaker is open, or an `httpx.HTTPError` if the
    call still fails after its retries. On success the breaker is reset.
    """
    breaker.guard()

    @retry(
        stop=stop_after_attempt(attempts),
        wait=wait_fixed(0),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )
    def _call() -> dict[str, Any]:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, headers={"X-Correlation-ID": correlation_id})
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            return payload

    try:
        data = _call()
    except httpx.HTTPError:
        breaker.record_failure()
        raise
    breaker.record_success()
    return data
