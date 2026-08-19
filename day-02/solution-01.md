# Solution 01 · Make telemetry-insight scale (CPU-bound)

> The full worked solution for Assignment 01. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your Day 1 `telemetry-insight` project, green. This solution adds the Day 2
layer: a streaming summary that stays flat in memory, and a CPU-bound transform run three
ways so you can see, with numbers, that threads do not speed up CPU work (the GIL) but
processes do. Use `poetry run` for everything.

The two results you are after:

- Streaming peak memory far below the eager peak, on a large file.
- The transform faster on a process pool than on a thread pool, with the thread pool roughly
  tying the serial baseline.

## Step 1: stream the summary

Replace the eager-only `data.py` with one that also streams, closing the file even on error.

**`src/telemetry_insight/data.py`**

```python
"""Load telemetry records from a CSV file: eagerly or as a stream."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def load_records(path: str) -> list[dict[str, str]]:
    """Read the whole CSV into a list. Fails clearly if it is missing."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"data file not found: {path}")
    with file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{key: str(value) for key, value in row.items()} for row in reader]


@contextmanager
def open_records(path: str) -> Iterator[Iterator[dict[str, str]]]:
    """Open the CSV and yield a stream of rows. Closes the file on exit, always."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"data file not found: {path}")
    handle = file.open(newline="", encoding="utf-8")
    try:
        reader = csv.DictReader(handle)
        yield ({key: str(value) for key, value in row.items()} for row in reader)
    finally:
        handle.close()
```

And summarize the stream in constant memory in the CLI.

**`src/telemetry_insight/cli.py`**

```python
"""Command line entry point for telemetry-insight."""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from telemetry_insight.config import Config
from telemetry_insight.data import open_records


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Summarize a stream without holding the rows, in constant memory."""
    readings = 0
    devices: set[str] = set()
    for record in records:
        readings += 1
        devices.add(record["device_id"])
    return {"readings": readings, "devices": len(devices)}


def main() -> None:
    parser = argparse.ArgumentParser(description="telemetry-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    parser.parse_args()

    config = Config.from_env()
    with open_records(config.data_path) as stream:
        result = summarize_stream(stream)

    print(f"[{config.environment}] {config.app_name}")
    print(f"readings: {result['readings']}")
    print(f"devices : {result['devices']}")
```

`summarize_stream` keeps only a counter and a set of device ids (a few hundred), never the
rows. That is what makes it flat.

## Step 2: the CPU-bound transform

This is the heart of the assignment. The transform *computes*, it does not wait, so it is
CPU-bound. It is defined at module top level so a `ProcessPoolExecutor` can pickle and run it.

**`src/telemetry_insight/transform.py`**

```python
"""A CPU-bound transform over telemetry readings, run three ways."""

from __future__ import annotations

import math
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

_INNER = 100  # busy-work iterations per value, to make the transform genuinely CPU-bound


def smooth_chunk(values: list[float]) -> float:
    """A deliberately CPU-heavy reduction over a chunk of readings."""
    acc = 0.0
    for value in values:
        for _ in range(_INNER):
            acc += math.sqrt(abs(value) + 1.0) * math.sin(value)
    return acc


def chunk_values(values: Iterator[float], size: int) -> list[list[float]]:
    """Split a stream of values into fixed-size chunks: the unit of parallel work."""
    chunks: list[list[float]] = []
    current: list[float] = []
    for value in values:
        current.append(value)
        if len(current) >= size:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def run_serial(chunks: list[list[float]]) -> list[float]:
    """Baseline: one chunk after another."""
    return [smooth_chunk(chunk) for chunk in chunks]


def run_threads(chunks: list[list[float]], workers: int = 8) -> list[float]:
    """Threads: no real speedup here, because the work is CPU-bound (the GIL)."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(smooth_chunk, chunks))


def run_processes(chunks: list[list[float]], workers: int = 8) -> list[float]:
    """Processes: real parallelism, because each has its own interpreter and GIL."""
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(smooth_chunk, chunks))
```

Two things make the process pool work: `smooth_chunk` is top level (picklable), and the
benchmark that calls it is guarded by `if __name__ == "__main__"` (below), which
`multiprocessing` requires on Windows and macOS.

## Step 3: generate volume

**`scripts/make_big.py`**

```python
"""Generate a large telemetry CSV so memory and speed differences are visible."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


def main(rows: int, path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["device_id", "ts", "value"])
        for i in range(rows):
            device = f"D{i % 200}"  # 200 distinct devices
            value = round(20.0 + 10.0 * math.sin(i / 100.0), 3)
            writer.writerow([device, f"2026-01-01T00:{(i % 60):02d}:00", value])
    print(f"wrote {rows} rows to {path}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    main(count, "data/telemetry_big.csv")
```

```bash
poetry run python scripts/make_big.py 1000000
```

## Step 4: the memory proof

**`scripts/measure_memory.py`**

```python
"""Compare peak memory: eager load versus streaming summary, on the big file."""

from __future__ import annotations

import tracemalloc

from telemetry_insight.cli import summarize_stream
from telemetry_insight.data import load_records, open_records

PATH = "data/telemetry_big.csv"


def _summarize_eager(rows: list[dict[str, str]]) -> dict[str, int]:
    devices = {row["device_id"] for row in rows}
    return {"readings": len(rows), "devices": len(devices)}


tracemalloc.start()
_summarize_eager(load_records(PATH))
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()

with open_records(PATH) as stream:
    summarize_stream(stream)
_, stream_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"eager peak    : {eager_peak / 1_000_000:8.1f} MB")
print(f"streaming peak: {stream_peak / 1_000_000:8.1f} MB")
print(f"reduction     : {eager_peak / max(stream_peak, 1):8.0f}x")
```

```bash
poetry run python scripts/measure_memory.py
```

You will see the eager peak in the hundreds of megabytes and the streaming peak near zero,
a reduction of hundreds to thousands of times (exact numbers vary by machine and row count).
That is the streaming proof.

## Step 5: the benchmark, and the point

**`scripts/benchmark_transform.py`**

```python
"""Benchmark the CPU-bound transform: serial vs threads vs processes."""

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
```

```bash
poetry run python scripts/benchmark_transform.py
```

A representative run (yours scales with your core count):

```text
serial   :   0.59s
threads  :   0.59s  (1.0x vs serial)
processes:   0.28s  (2.1x vs serial)
threads do not help (CPU-bound + GIL); processes do (own interpreter each).
```

That is the whole lesson in three lines. Threads tie serial, because only one thread runs
Python bytecode at a time and this work is all Python computation. Processes beat both,
because each process has its own interpreter and its own GIL, so they genuinely run in
parallel. On a machine with more cores the process speedup grows toward the core count.

## Step 6: the test

Keep the test fast: prove the streaming summary and that threads give the *same answer* as
serial (they just do not run faster). No process pool in the test.

**`tests/test_telemetry.py`**

```python
"""Tests for telemetry-insight: streaming summary and the CPU-bound transform."""

from __future__ import annotations

from pathlib import Path

from telemetry_insight.cli import summarize_stream
from telemetry_insight.data import load_records, open_records
from telemetry_insight.transform import run_serial, run_threads

CSV_TEXT = "device_id,ts,value\nD1,t0,1.0\nD1,t1,2.0\nD2,t2,3.0\nD3,t3,4.0\nD3,t4,5.0\n"


def test_stream_summary(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")
    with open_records(str(sample)) as stream:
        assert summarize_stream(stream) == {"readings": 5, "devices": 3}


def test_stream_matches_eager(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")
    eager = load_records(str(sample))
    with open_records(str(sample)) as stream:
        streamed = summarize_stream(stream)
    assert streamed["readings"] == len(eager)
    assert streamed["devices"] == 3


def test_threads_match_serial() -> None:
    chunks = [[1.0, 2.0, 3.0], [4.0, 5.0]]
    assert run_threads(chunks) == run_serial(chunks)
```

## Step 7: green gate and commit

```bash
poetry run pytest -q          # 3 passed
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "day 2: streaming summary, and CPU-bound transform across processes"
```

## Done when

- The streaming summary runs over a million-plus-row file with a near-zero memory peak.
- `measure_memory.py` shows the streaming peak far below the eager peak.
- `benchmark_transform.py` shows processes clearly faster than serial, and threads not.
- The one-line explanation in the output states why: CPU-bound work plus the GIL means
  threads cannot parallelize it, but separate processes can.
- `pytest`, `ruff`, and `mypy` are all green, and the layer is committed.

You have shown the Day 2 point for compute-heavy work: streaming is always right for memory,
and escaping the GIL with processes is what actually parallelizes the computation.
