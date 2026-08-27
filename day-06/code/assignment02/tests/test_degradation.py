"""The deliverable test: the fan-out stays bounded and complete under a slow dependency."""

from __future__ import annotations

import time

from transactions_insight.enrich import ConcurrencyGauge, enrich_safe

ACCOUNTS = [f"A{i}" for i in range(12)]


def test_degrades_gracefully_when_slow() -> None:
    cap = 4
    gauge = ConcurrencyGauge()

    start = time.perf_counter()
    results = enrich_safe(
        ACCOUNTS, delay=0.15, cap=cap, rate_per_sec=1000.0, timeout=0.05, gauge=gauge
    )
    elapsed = time.perf_counter() - start

    # every transaction gets a result, in order
    assert [r.account_id for r in results] == ACCOUNTS
    assert all(r.risk in {"high", "low", "unavailable"} for r in results)
    # concurrency never exceeded the cap
    assert gauge.max_seen <= cap
    # bounded wall time: about ceil(n / cap) waves of `delay`, not n * delay
    assert elapsed < 1.5


def test_healthy_dependency_returns_real_results() -> None:
    gauge = ConcurrencyGauge()
    results = enrich_safe(
        ACCOUNTS, delay=0.01, cap=4, rate_per_sec=1000.0, timeout=0.5, gauge=gauge
    )
    assert all(r.ok for r in results)
    assert all(r.risk in {"high", "low"} for r in results)
    assert gauge.max_seen <= 4
