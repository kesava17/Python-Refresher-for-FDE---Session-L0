# Day 2 Live Lab: Make reviews-insight Performant

## What we're building

You already have the Day 1 `reviews-insight` service: it loads a CSV of reviews into a list and
prints a summary. That is fine for five rows and fatal for fifty million. In the next 30 minutes
you make it **performant and scalable**, and you prove both with numbers:

1. Replace the eager load with a **streaming pass** that summarizes in constant memory, behind a
   **context-managed** source.
2. Measure the memory of the eager path versus the streaming path on a large file. The streaming
   peak stays flat. That is proof one.
3. Add a **concurrent enrichment** (a simulated external catalog lookup per review) with a
   timeout and a retry, and benchmark serial versus concurrent. Concurrent finishes far sooner.
   That is proof two.

Work in order. Copy, paste, run. After each step there is one line on what happened and why it
matters. Start from your Day 1 project folder (`reviews-insight`), with everything green.

Ground rules, same as Day 1: everything Python runs through `poetry run`; run commands from
inside the project folder.

---

## Step 1: Generate a large data file

To see a memory difference you need real volume. Generate a big CSV next to the small one.

Create `scripts/make_big.py`:

```python
"""Generate a large reviews CSV so memory and speed differences are visible."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

WORDS = ["great", "good", "average", "poor", "excellent", "broke", "fantastic", "ok"]


def main(rows: int, path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["product_id", "rating", "text"])
        for i in range(rows):
            product = f"P{i % 500}"  # 500 distinct products
            writer.writerow([product, (i % 5) + 1, f"{WORDS[i % len(WORDS)]} product number {i}"])
    print(f"wrote {rows} rows to {path}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    main(count, "data/reviews_big.csv")
```

Generate two million rows:

```bash
poetry run python scripts/make_big.py 2000000
```

**What happened.** You now have `data/reviews_big.csv` with two million rows across 500
products. Big enough that loading it all at once costs real memory, which is exactly what we
want to measure.

---

## Step 2: Add a streaming, context-managed loader

Open `src/reviews_insight/data.py`. Keep the Day 1 `load_records` (we will compare against it)
and add a streaming reader below it.

```python
"""Load records from a CSV file: eagerly (Day 1) or as a stream (Day 2)."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def load_records(path: str) -> list[dict[str, str]]:
    """Day 1: read the whole CSV into a list. Fails clearly if it is missing."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"data file not found: {path}")
    with file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{key: str(value) for key, value in row.items()} for row in reader]


@contextmanager
def open_records(path: str) -> Iterator[Iterator[dict[str, str]]]:
    """Day 2: open the CSV and yield a stream of rows. Closes the file on exit, always."""
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

**What happened.** `open_records` is both a context manager and a generator source: the `with`
guarantees the file is closed even on error, and the yielded generator hands out one row at a
time instead of building a list. Nothing is held in memory but the current row.

---

## Step 3: Summarize in constant memory

Open `src/reviews_insight/cli.py`. Keep the Day 1 `summarize` and add a streaming version that
folds the rows into a running total and a set of product ids.

```python
from collections.abc import Iterator


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Summarize a stream without holding the rows: constant memory."""
    reviews = 0
    products: set[str] = set()
    for record in records:
        reviews += 1
        products.add(record["product_id"])
    return {"reviews": reviews, "products": len(products)}
```

**What happened.** This holds only a counter and the set of distinct products (500 of them), not
the two million rows. Memory is bounded by the number of distinct products, not the file size.

---

## Step 4: Prove the memory is flat

Create `scripts/measure_memory.py` to compare the two paths on the big file.

```python
"""Compare peak memory: eager load versus streaming, on the big file."""

from __future__ import annotations

import tracemalloc

from reviews_insight.cli import summarize, summarize_stream
from reviews_insight.data import load_records, open_records

PATH = "data/reviews_big.csv"

tracemalloc.start()
summarize(load_records(PATH))  # eager: builds a 2M-row list
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()

with open_records(PATH) as stream:  # streaming: one row at a time
    summarize_stream(stream)
_, stream_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"eager peak    : {eager_peak / 1_000_000:8.1f} MB")
print(f"streaming peak: {stream_peak / 1_000_000:8.1f} MB")
print(f"reduction     : {eager_peak / stream_peak:8.0f}x")
```

Run it:

```bash
poetry run python scripts/measure_memory.py
```

You will see something like (exact numbers vary by machine):

```text
eager peak    :    900.0 MB
streaming peak:      0.1 MB
reduction     :     9000x
```

**What happened.** The eager path built a list of two million dicts and paid hundreds of
megabytes for it. The streaming path held one row at a time and stayed flat. This is **proof
one**: the memory difference is measured, not claimed. On real data, the eager version is the
one that gets an out-of-memory kill in production.

---

## Step 5: Add a simulated external enrichment

Real insight needs more than counts. Add an enrichment that looks up each product's category
from an external catalog service, one call per review. Create `src/reviews_insight/enrich.py`:

```python
"""Enrich reviews with a category from a (simulated) external catalog service."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout


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
```

**What happened.** `fetch_category` waits (it sleeps, standing in for a network call), so it is
IO-bound, which is why threads will speed it up. `enrich_concurrent` overlaps the waits;
`fetch_with_retry` shows the safety habits: a timeout so a call cannot hang forever, and a
bounded retry.

---

## Step 6: Benchmark serial versus concurrent

Create `scripts/benchmark_enrich.py`:

```python
"""Benchmark enrichment: serial versus concurrent, on a sample of reviews."""

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
print(f"speedup   : {serial / concurrent:6.1f}x")
```

Run it:

```bash
poetry run python scripts/benchmark_enrich.py
```

You will see roughly:

```text
serial    :   8.10s
concurrent:   0.55s
speedup   :   14.7x
```

**What happened.** Serial made 400 calls of 20 ms each, one after another, about 8 seconds.
Concurrent ran 16 at a time, overlapping the waits, and finished in well under a second. This is
**proof two**: the speedup is measured. Note the speedup is roughly the number of workers,
because the work is pure waiting. If `fetch_category` were CPU-bound instead, this same thread
pool would give almost nothing, and you would switch to a process pool.

---

## Step 7: Wire the streaming summary into the CLI

Make streaming the default path for the `summary` command. In `cli.py`, update `main` to use the
context-managed stream:

```python
    config = Config.from_env()

    if args.command == "summary":
        with open_records(config.data_path) as stream:
            result = summarize_stream(stream)
        print(f"[{config.environment}] {config.app_name}")
        print(f"reviews : {result['reviews']}")
        print(f"products: {result['products']}")
```

Remember to import `open_records` and `summarize_stream`. Run it against the big file:

```bash
DATA_PATH=data/reviews_big.csv poetry run reviews summary
```

```text
[dev] reviews-insight
reviews : 2000000
products: 500
```

**What happened.** The command summarized two million rows without ever holding them in memory.
Same output shape as Day 1, now scalable.

---

## Step 8: Green gate and commit

Add a test for the streaming path in `tests/test_summary.py`:

```python
def test_stream_matches_eager(tmp_path: Path) -> None:
    csv_text = "product_id,rating,text\nP1,5,great\nP1,4,good\nP2,3,ok\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    from reviews_insight.cli import summarize_stream
    from reviews_insight.data import open_records

    with open_records(str(sample)) as stream:
        assert summarize_stream(stream) == {"reviews": 3, "products": 2}
```

Then run the gate and commit:

```bash
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
git add .
git commit -m "day 2: streaming in constant memory, concurrent enrichment"
```

**What happened.** The new streaming path is covered by a test, the gate is green, and the
performance layer is committed on top of the Day 1 skeleton.

---

## You should see

Run through this recap. If each line matches, Day 2's lab is done.

- `scripts/measure_memory.py` shows the streaming peak far below the eager peak (a large
  reduction factor). Proof one: memory is flat.
- `scripts/benchmark_enrich.py` shows concurrent far faster than serial, roughly the worker
  count. Proof two: the waits overlap.
- `DATA_PATH=data/reviews_big.csv poetry run reviews summary` prints `reviews : 2000000` and
  `products: 500` without a memory spike.
- `poetry run pytest -q`, `ruff check .`, and `mypy src` are all green.
- The commit lands with the gate passing.

That is the Day 2 layer: the same small service now streams in constant memory and enriches
concurrently, with a memory profile and a benchmark to prove it. The design choices (stream, do
not materialize; threads for waiting; a timeout on every call) are what make it scale, and they
were made in the code, not with a profiler afterward.
