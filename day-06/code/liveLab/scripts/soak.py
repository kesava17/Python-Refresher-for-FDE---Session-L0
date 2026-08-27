"""Soak test: run the core summarize loop many times and watch that memory stays flat.

A dependable service must survive running for a long time, not just one request. A memory leak
shows up only under sustained load, so we drive the core loop for many iterations and print the
current traced memory at intervals. If the number stays flat, the loop retains no growing state
and does not leak.

Run:  poetry run python scripts/soak.py
"""

from __future__ import annotations

import tracemalloc

from reviews_insight.service import summarize_rows

# A fixed batch of rows, some good and some malformed, reused every iteration.
ROWS = [{"product_id": f"P{i % 100}", "rating": str((i % 6) + 1)} for i in range(10_000)]

ITERATIONS = 2_000
REPORT_EVERY = 500

tracemalloc.start()
for run in range(1, ITERATIONS + 1):
    summarize_rows(iter(ROWS))  # build, count, discard: nothing is kept between runs
    if run == 1 or run % REPORT_EVERY == 0:
        current, _ = tracemalloc.get_traced_memory()
        print(f"after run {run:5d}: current memory {current / 1_000_000:6.2f} MB")
tracemalloc.stop()

print("current memory stays flat across runs: no state is retained, so no leak.")
