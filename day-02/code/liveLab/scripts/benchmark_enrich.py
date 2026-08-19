"""Benchmark enrichment: serial versus concurrent, on a sample of reviews.

Run scripts/make_big.py first to create data/reviews_big.csv.
"""

from __future__ import annotations

import time

from reviews_insight.data import open_records
from reviews_insight.enrich import enrich_concurrent, enrich_serial

PATH = "data/reviews_big.csv"
SAMPLE = 400  # 400 reviews * 20 ms each = ~8 s serial

with open_records(PATH) as stream:
    product_ids = [row["product_id"] for _, row in zip(range(SAMPLE), stream)]

start = time.perf_counter()
enrich_serial(product_ids)
serial = time.perf_counter() - start

start = time.perf_counter()
enrich_concurrent(product_ids, workers=16)
concurrent = time.perf_counter() - start

print(f"serial    : {serial:6.2f}s")
print(f"concurrent: {concurrent:6.2f}s")
print(f"speedup   : {serial / max(concurrent, 1e-6):6.1f}x")
