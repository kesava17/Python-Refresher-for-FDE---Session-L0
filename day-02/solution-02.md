# Solution 02 · Fan out transaction lookups, and degrade gracefully

> The full worked solution for Assignment 02. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your Day 1 `transactions-insight` project, green. This solution adds a
concurrent enrichment whose real job is to behave well when the dependency is slow: a
concurrency cap, a rate limit, and a per-call timeout, so the fan-out stays bounded and
still returns a result for every transaction. Use `poetry run` for everything.

## Step 1: the controllable dependency and the safe enricher

Everything lives in one module. Read it top to bottom: a lookup with a dial-able delay, a
thread-safe gauge that records the peak concurrency, a `Result` that marks whether the call
succeeded or fell back, a serial baseline, and the safe fan-out.

**`src/transactions_insight/enrich.py`**

```python
"""Enrich transactions with a lookup from a (simulated) external service."""

from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from dataclasses import dataclass


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

    def __enter__(self) -> ConcurrencyGauge:
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
    """Fan out lookups with a concurrency cap, a rate limit, and a per-call timeout."""
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
```

Where each safety habit lives:

- **Concurrency cap:** `ThreadPoolExecutor(max_workers=cap)`. At most `cap` lookups run at
  once, so you never flood the dependency. The `ConcurrencyGauge` proves the cap holds.
- **Rate limit:** `time.sleep(min_interval)` between submissions, so new calls start no
  faster than `rate_per_sec`, independent of the cap.
- **Timeout:** `future.result(timeout=timeout)`. If a call does not return in time, you
  catch `FuturesTimeout` and record a clean `"unavailable"` fallback instead of hanging.
- **Every transaction gets a result:** the fallback guarantees it, so one slow call cannot
  drop a record.

## Step 2: the degradation test (the deliverable)

This is the proof. Make the dependency slower than the timeout and assert that the run stays
bounded and complete, and that the cap was never exceeded.

**`tests/test_degradation.py`**

```python
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

    assert [r.account_id for r in results] == ACCOUNTS
    assert all(r.risk in {"high", "low", "unavailable"} for r in results)
    assert gauge.max_seen <= cap
    assert elapsed < 1.5  # about ceil(n / cap) waves of `delay`, not n * delay


def test_healthy_dependency_returns_real_results() -> None:
    gauge = ConcurrencyGauge()
    results = enrich_safe(
        ACCOUNTS, delay=0.01, cap=4, rate_per_sec=1000.0, timeout=0.5, gauge=gauge
    )
    assert all(r.ok for r in results)
    assert all(r.risk in {"high", "low"} for r in results)
    assert gauge.max_seen <= 4
```

What the slow test proves:

- **Complete:** there is a result for every account, in order.
- **Bounded concurrency:** `gauge.max_seen <= cap`. The fan-out never exceeded the cap, even
  under stress.
- **Bounded time:** the whole run finishes in well under the time a serial run would take
  (`n * delay`), because the cap runs `cap` calls per wave.

An honest note on the limitation: a Python thread cannot be killed, so the timeout lets you
*move on* from a slow call and record a fallback, but the underlying worker still finishes
its sleep before its slot frees. So the bound is about `ceil(n / cap) * delay`, not
`timeout`. That is a real property of threads worth knowing, and it is why heavy IO systems
eventually reach for async or a broker.

## Step 3: the healthy-dependency benchmark

Show that with a fast dependency the concurrent fan-out wins clearly, and the safety
machinery costs almost nothing.

**`scripts/benchmark_enrich.py`**

```python
"""Benchmark: serial versus the safe concurrent fan-out, on a healthy (fast) dependency."""

from __future__ import annotations

import time

from transactions_insight.enrich import ConcurrencyGauge, enrich_safe, enrich_serial


def main() -> None:
    accounts = [f"A{i}" for i in range(400)]

    start = time.perf_counter()
    enrich_serial(accounts, delay=0.02)
    serial = time.perf_counter() - start

    gauge = ConcurrencyGauge()
    start = time.perf_counter()
    enrich_safe(accounts, delay=0.02, cap=16, rate_per_sec=4000.0, timeout=1.0, gauge=gauge)
    concurrent = time.perf_counter() - start

    print(f"serial         : {serial:6.2f}s")
    print(f"concurrent     : {concurrent:6.2f}s")
    print(f"speedup        : {serial / max(concurrent, 1e-6):6.1f}x")
    print(f"max concurrency: {gauge.max_seen} (cap was 16)")


if __name__ == "__main__":
    main()
```

```bash
poetry run python scripts/benchmark_enrich.py
```

A representative run:

```text
serial         :   8.23s
concurrent     :   0.56s
speedup        :   14.7x
max concurrency: 16 (cap was 16)
```

The concurrent version is about the worker count faster, and the gauge confirms concurrency
stayed at the cap and no higher.

## Step 4: green gate and commit

```bash
poetry run pytest -q          # 2 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "day 2: safe concurrent fan-out with a cap, rate limit, and timeout"
```

## Done when

- Concurrent enrichment beats serial on a healthy dependency, timed.
- Every external call has a timeout and returns a clean fallback when it fires.
- The degradation test proves concurrency never exceeds the cap, every transaction has a
  result, and the run completes in bounded time under a slow dependency.
- `pytest`, `ruff`, and `mypy` are all green, and the layer is committed.

You have built the part that keeps a service alive in production: a fan-out that is fast when
the dependency is healthy, and bounded, complete, and responsive when it is not.
