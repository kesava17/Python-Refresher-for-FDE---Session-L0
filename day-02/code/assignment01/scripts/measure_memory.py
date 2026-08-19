"""Compare peak memory: eager load versus streaming summary, on the big file.

Run scripts/make_big.py first to create data/telemetry_big.csv.
"""

from __future__ import annotations

import tracemalloc

from telemetry_insight.cli import summarize_stream
from telemetry_insight.data import load_records, open_records

PATH = "data/telemetry_big.csv"


def _summarize_eager(rows: list[dict[str, str]]) -> dict[str, int]:
    devices = {row["device_id"] for row in rows}
    return {"readings": len(rows), "devices": len(devices)}


tracemalloc.start()
_summarize_eager(load_records(PATH))  # eager: builds a full in-memory list
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()

with open_records(PATH) as stream:  # streaming: one row at a time
    summarize_stream(stream)
_, stream_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"eager peak    : {eager_peak / 1_000_000:8.1f} MB")
print(f"streaming peak: {stream_peak / 1_000_000:8.1f} MB")
print(f"reduction     : {eager_peak / max(stream_peak, 1):8.0f}x")
