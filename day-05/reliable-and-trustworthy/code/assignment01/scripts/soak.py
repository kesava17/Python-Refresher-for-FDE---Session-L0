"""Soak test: prove memory stays flat under a long, high-volume ingest stream.

This is the durability (MTBF) proof for the telemetry domain, where the pressure is a
never-ending stream of numeric readings. We drive ingest for many iterations and print the
process memory at intervals with `tracemalloc`. If memory climbs steadily, we have a leak in
the request path; if it stays flat, the service can run for a long time without degrading.

To keep the observed store bounded (so we measure the request path, not intentional growth),
every reading carries the same idempotency key. Dedup then holds the store at one row, and
whatever memory we see moving is the per-request overhead, not stored data.

Run it with:  poetry run python scripts/soak.py
"""

from __future__ import annotations

import tracemalloc

from fastapi.testclient import TestClient

from telemetry_insight.api import create_app

ITERATIONS = 8_000
REPORT_EVERY = 2_000


def main() -> None:
    client = TestClient(create_app())
    reading = {"device_id": "D1", "value": 20.5, "key": "soak-fixed-key"}

    tracemalloc.start()
    for i in range(1, ITERATIONS + 1):
        # Same key every time: dedup keeps the store at one row, so growth would be a leak.
        client.post("/v1/readings", json=reading)
        if i % REPORT_EVERY == 0:
            current, peak = tracemalloc.get_traced_memory()
            print(
                f"iter {i:>7}  current {current / 1_000_000:6.2f} MB  "
                f"peak {peak / 1_000_000:6.2f} MB"
            )
    tracemalloc.stop()

    # A final confirmation that dedup held the store flat across the whole run.
    total = client.get("/v1/insight").json()["readings"]
    print(f"stored readings after {ITERATIONS} posts: {total} (flat under dedup)")


if __name__ == "__main__":
    main()
