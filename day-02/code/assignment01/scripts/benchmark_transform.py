"""Benchmark the CPU-bound transform: serial vs threads vs processes.

Run scripts/make_big.py first to create data/telemetry_big.csv.

Expect: threads roughly tie serial (the GIL blocks CPU parallelism), while processes
beat both, up to the number of cores. That is the whole lesson of this assignment.
"""

from __future__ import annotations

import time

from telemetry_insight.data import open_records
from telemetry_insight.transform import (
    chunk_values,
    run_processes,
    run_serial,
    run_threads,
)

PATH = "data/telemetry_big.csv"
CHUNK = 2000
NUM_CHUNKS = 24  # keep the benchmark to a few seconds serial


def main() -> None:
    with open_records(PATH) as stream:
        wanted = CHUNK * NUM_CHUNKS
        values = [float(row["value"]) for _, row in zip(range(wanted), stream)]
    chunks = chunk_values(iter(values), CHUNK)

    start = time.perf_counter()
    run_serial(chunks)
    serial = time.perf_counter() - start

    start = time.perf_counter()
    run_threads(chunks, workers=8)
    threads = time.perf_counter() - start

    start = time.perf_counter()
    run_processes(chunks, workers=8)
    processes = time.perf_counter() - start

    print(f"serial   : {serial:6.2f}s")
    print(f"threads  : {threads:6.2f}s  ({serial / max(threads, 1e-6):.1f}x vs serial)")
    print(f"processes: {processes:6.2f}s  ({serial / max(processes, 1e-6):.1f}x vs serial)")
    print("threads do not help (CPU-bound + GIL); processes do (own interpreter each).")


if __name__ == "__main__":
    main()
