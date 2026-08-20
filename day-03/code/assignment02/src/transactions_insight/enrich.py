"""Enrich transactions with a lookup from a (simulated) external service.

The focus here is safety under a slow dependency: a concurrency cap, a rate limit, and a
per-call timeout, so the fan-out stays bounded and still completes for every transaction.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from dataclasses import dataclass
from typing import Self


def lookup(account_id: str, delay: float = 0.02) -> str:
    """Stand-in for a real external call: waits `delay` seconds, then returns a risk band."""
    time.sleep(delay)
    return "high" if account_id.endswith(("0", "5")) else "low"


class ConcurrencyGauge:
    """Track in-flight calls and the maximum ever seen at once (thread-safe)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current = 0
        self.max_seen = 0

    def __enter__(self) -> Self:
        with self._lock:
            self._current += 1
            self.max_seen = max(self.max_seen, self._current)
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        with self._lock:
            self._current -= 1


@dataclass(frozen=True)
class Result:
    account_id: str
    risk: str
    ok: bool  # False when the call timed out and the fallback was used


def _guarded_lookup(account_id: str, delay: float, gauge: ConcurrencyGauge) -> str:
    with gauge:
        return lookup(account_id, delay)


def enrich_serial(account_ids: list[str], delay: float = 0.02) -> list[Result]:
    """Baseline: one lookup at a time."""
    return [Result(acc, lookup(acc, delay), True) for acc in account_ids]


def enrich_safe(
    account_ids: list[str],
    delay: float = 0.02,
    cap: int = 8,
    rate_per_sec: float = 200.0,
    timeout: float = 0.5,
    gauge: ConcurrencyGauge | None = None,
) -> list[Result]:
    """Fan out lookups with a concurrency cap, a rate limit, and a per-call timeout.

    Every account gets a result: a real one, or a clean "unavailable" fallback when the
    call did not return within the timeout. Concurrency never exceeds `cap`.
    """
    if gauge is None:
        gauge = ConcurrencyGauge()
    min_interval = 1.0 / rate_per_sec
    results: dict[int, Result] = {}

    with ThreadPoolExecutor(max_workers=cap) as pool:
        futures: dict[Future[str], tuple[int, str]] = {}
        for index, account in enumerate(account_ids):
            future = pool.submit(_guarded_lookup, account, delay, gauge)
            futures[future] = (index, account)
            time.sleep(min_interval)  # rate limit: pace how fast new calls start
        for future, (index, account) in futures.items():
            try:
                results[index] = Result(account, future.result(timeout=timeout), True)
            except FuturesTimeout:
                results[index] = Result(account, "unavailable", False)

    return [results[index] for index in range(len(account_ids))]
