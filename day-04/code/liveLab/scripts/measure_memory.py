"""Compare peak memory: eager load versus streaming, on the big file.

Run scripts/make_big.py first to create data/reviews_big.csv.
"""

from __future__ import annotations

import tracemalloc

from reviews_insight.cli import summarize, summarize_stream
from reviews_insight.data import load_records, open_records

PATH = "data/reviews_big.csv"

tracemalloc.start()
summarize(load_records(PATH))  # eager: builds a full in-memory list
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()

with open_records(PATH) as stream:  # streaming: one row at a time
    summarize_stream(stream)
_, stream_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"eager peak    : {eager_peak / 1_000_000:8.1f} MB")
print(f"streaming peak: {stream_peak / 1_000_000:8.1f} MB")
print(f"reduction     : {eager_peak / max(stream_peak, 1):8.0f}x")
