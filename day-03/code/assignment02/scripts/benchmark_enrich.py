"""Benchmark: serial versus the safe concurrent fan-out, on a healthy (fast) dependency.

On a healthy dependency the concurrent version wins clearly; the safety machinery
(cap, rate limit, timeout) costs almost nothing here, and pays off when the
dependency is slow (see the degradation test).
"""

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
