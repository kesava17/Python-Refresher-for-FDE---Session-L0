"""Enrich reviews with a category from a (simulated) external catalog service."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout


def fetch_category(product_id: str) -> str:
    """Stand-in for a real network call: it waits, so it is IO-bound."""
    time.sleep(0.02)  # simulate ~20 ms of network latency
    return "priority" if product_id.endswith(("0", "5")) else "standard"


def enrich_serial(product_ids: list[str]) -> list[str]:
    """One call at a time: each waits for the previous to finish."""
    return [fetch_category(pid) for pid in product_ids]


def enrich_concurrent(product_ids: list[str], workers: int = 16) -> list[str]:
    """Overlap the waits with a thread pool. IO-bound, so threads are the right tool."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fetch_category, product_ids))


def fetch_with_retry(product_id: str, attempts: int = 3, timeout: float = 0.5) -> str:
    """A per-call timeout and a bounded retry, so one slow call cannot hang the batch."""
    for attempt in range(1, attempts + 1):
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(fetch_category, product_id)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeout:
                if attempt == attempts:
                    raise
    raise RuntimeError("unreachable")
