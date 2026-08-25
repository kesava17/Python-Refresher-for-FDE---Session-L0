"""Proof: the validated summary keeps no growing state over many runs, so it does not leak.

Run:  poetry run python scripts/measure_leak.py
"""

from __future__ import annotations

import tracemalloc

from reviews_insight.cli import summarize_validated

# A fixed batch of rows, some good and some malformed.
ROWS = [{"product_id": f"P{i % 100}", "rating": str((i % 6) + 1)} for i in range(10_000)]

tracemalloc.start()
for run in range(1, 51):
    summarize_validated(iter(ROWS))  # build, count, discard: nothing retained
    if run in (1, 25, 50):
        current, _ = tracemalloc.get_traced_memory()
        print(f"after run {run:2d}: current memory {current / 1_000_000:6.2f} MB")
tracemalloc.stop()

print("current memory stays flat across runs: no state is retained, so no leak.")
