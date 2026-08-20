# Day 3 Live Lab: Make reviews-insight Maintainable

## What we're building

You already have the Day 2 `reviews-insight` service: it streams a CSV of reviews in constant
memory. It works, but it is tangled. The CLI opens the file, the parsing, and the counting all sit
in one function that knows where the data lives. Change the source and you rewrite the logic. In the
next 30 minutes you make it **maintainable**, and you prove it with numbers:

1. Introduce a **data-source seam**: a `ReviewSource` Protocol and two interchangeable
   implementations, so the service depends on a shape rather than a concrete file reader.
2. Move the summary logic into a **service with its source injected**: the counting lives in one
   place, and the service is handed its source from outside instead of building one.
3. Add **one decorator** for a cross-cutting concern (timing), applied by name to `summarize()`,
   without touching the logic it wraps.
4. Make the **CLI a thin composition root**: build the CSV source, inject it, print. All the real
   work lives in the service.
5. **Prove the seam**: a test swaps the source from a CSV file to an in-memory list with zero change
   to the service, and both give the same result. That is the proof.

Work in order. Copy, paste, run. After each step there is one line on what happened and why it
matters. Start from your Day 2 project folder (`reviews-insight`), with everything green.

Ground rules, same as before: everything Python runs through `poetry run`; run commands from
inside the project folder.

---

## Step 1: Introduce the ReviewSource seam

Right now the service knows it reads a CSV file. That knowledge is a chain: as long as the logic
holds the file path, the file path holds the logic. Break the chain by depending on a shape instead.
Create `src/reviews_insight/sources.py`:

```python
"""The data-source seam (new on Day 3): a small Protocol, and two interchangeable sources.

A Protocol describes a contract by its shape: any object that has a `rows()` method
returning review rows counts as a ReviewSource, with no base class to inherit. This is
what lets the service depend on the contract, not on where the data actually comes from.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol

from reviews_insight.data import open_records


class ReviewSource(Protocol):
    """The contract the service depends on: something that can hand over review rows."""

    def rows(self) -> Iterator[dict[str, str]]:
        """Yield raw review rows, one dictionary at a time."""
        ...


class CsvReviewSource:
    """A ReviewSource backed by a CSV file on disk. Used in the real application."""

    def __init__(self, path: str) -> None:
        self._path = path

    def rows(self) -> Iterator[dict[str, str]]:
        # open_records is a context manager that streams rows and always closes the file.
        # Yielding from inside the `with` keeps the file open only while it is being read.
        with open_records(self._path) as stream:
            yield from stream


class InMemoryReviewSource:
    """A ReviewSource backed by a list already in memory. Ideal for tests: no file needed."""

    def __init__(self, rows: Sequence[dict[str, str]]) -> None:
        self._rows = list(rows)

    def rows(self) -> Iterator[dict[str, str]]:
        return iter(self._rows)
```

**What happened.** `ReviewSource` is a `Protocol`: it names one method, `rows()`, and nothing more.
Neither `CsvReviewSource` nor `InMemoryReviewSource` inherits from it, yet both satisfy it, because
each has a matching `rows()` method. That is **structural typing**: an object fits the contract by
its shape, not by its ancestry. The CSV source streams from disk exactly as before; the in-memory
source hands back a list. Two very different sources now offer the same seam, and anything that
depends on `ReviewSource` can use either without knowing which it holds.

---

## Step 2: Move the logic into a service with the source injected

The counting logic should not care where rows come from, and it should live in one place instead of
being copied into every entry point. Create `src/reviews_insight/service.py`:

```python
"""The service layer, new on Day 3: the summary logic, with its data source injected.

New this day: the counting logic moves into one place (`summarize_rows`), and `SummaryService`
receives a `ReviewSource` from outside (dependency injection) instead of building one. That seam
lets a test feed in-memory rows while the real app feeds a CSV file, with the logic unchanged.
"""

from __future__ import annotations

from collections.abc import Iterator

from reviews_insight.decorators import timed
from reviews_insight.models import parse_review
from reviews_insight.sources import ReviewSource


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count reviews and distinct products from a stream of rows."""
    reviews = 0
    products: set[str] = set()
    for row in rows:
        review = parse_review(row)
        reviews += 1
        products.add(review.product_id)
    return {"reviews": reviews, "products": len(products)}


class SummaryService:
    """Summarizes reviews from any ReviewSource. The source is injected, not built here."""

    def __init__(self, source: ReviewSource) -> None:
        # The service depends on the ReviewSource contract, not on a file or a database.
        self._source = source

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())
```

**What happened.** `summarize_rows` holds the counting logic, once, with no knowledge of files
or sources. `SummaryService` takes a `ReviewSource` in its constructor and stores it: it is **handed**
its source rather than building one, which is **dependency injection**. The `summarize` method does
nothing but drive that injected source through the shared logic. This is **separation of concerns**:
where the data comes from (the source) is now a separate decision from what to do with it (the
logic), and neither one has to change when the other does.

---

## Step 3: Add one decorator, used sparingly

Timing a call is a concern that many methods share, but none of them should be cluttered with a
stopwatch. Put it in one place and apply it by name. Create `src/reviews_insight/decorators.py`:

```python
"""A single decorator for a cross-cutting concern (new on Day 3): timing, used sparingly.

Timing is a concern that many methods share but none of them should be cluttered with. A
decorator lets us add it in one place and apply it by name, without editing the logic it
wraps. The typing (ParamSpec plus TypeVar) preserves the wrapped function's signature, so
mypy still checks callers exactly as before.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(label: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that prints how long the wrapped call took, labelled by `label`."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)  # keep the wrapped function's name and docstring
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                # `finally` runs whether the call returned or raised, so the timing is
                # always reported, even on failure.
                elapsed_ms = (time.perf_counter() - start) * 1000
                print(f"[timed] {label}: {elapsed_ms:.1f} ms")

        return wrapper

    return decorator
```

**What happened.** `timed` adds one measurement in one place, and `@timed("summary")` on the service
turns it on by name without a single edit to the counting logic. Note that this is **one**
decorator, for a concern (timing) that genuinely cuts across methods. Decorators are easy to overuse,
and a stack of them hides the real work behind layers of wrapping. One, applied where it is
genuinely needed, keeps the power without the clutter. The `ParamSpec` and `TypeVar` typing preserves the wrapped
signature, so mypy still checks callers of `summarize` exactly as before.

---

## Step 4: Make the CLI a thin composition root

With the logic in the service and the source behind a seam, the CLI has almost nothing left to do.
Its job is to assemble the pieces and print. Open `src/reviews_insight/cli.py` and make it read:

```python
"""Command line entry point (new on Day 3: a thin composition root).

New this day: the CLI no longer holds the logic. It builds the concrete source, injects it into
the service, and prints. All the real work lives in the service.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from reviews_insight.config import Config
from reviews_insight.service import SummaryService
from reviews_insight.sources import CsvReviewSource


def summarize(records: list[dict[str, str]]) -> dict[str, int]:
    """Day 1: summarize a list of records held in memory."""
    products = {record["product_id"] for record in records}
    return {"reviews": len(records), "products": len(products)}


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
    reviews = 0
    products: set[str] = set()
    for record in records:
        reviews += 1
        products.add(record["product_id"])
    return {"reviews": reviews, "products": len(products)}


def main() -> None:
    parser = argparse.ArgumentParser(description="reviews-insight")
    parser.add_argument("command", choices=["summary"], help="what to do")
    parser.parse_args()

    config = Config.from_env()

    # Composition root: build the source, inject it into the service, run it.
    source = CsvReviewSource(config.data_path)
    service = SummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"reviews : {result['reviews']}")
    print(f"products: {result['products']}")


if __name__ == "__main__":
    main()
```

Run the summary:

```bash
poetry run reviews summary
```

You will see:

```text
[timed] summary: 0.3 ms
[dev] reviews-insight
reviews : 5
products: 3
```

**What happened.** `main` now does four small things: read the config, build a `CsvReviewSource`,
inject it into a `SummaryService`, and print the result. That is a **composition root**: the one place
that decides which concrete pieces to assemble. The surface stays small on
purpose, because the CLI is where change is riskiest: it is the seam between the outside world and
the code, and the less logic it carries, the less can break when the entry point changes. The
`[timed] summary` line is the decorator reporting from the service, the counts are unchanged, and
the day-3 layers are working end to end.

---

## Step 5: Prove the seam

The whole point of the refactor is that the service does not care where its rows come from. Prove it:
feed the same data through two completely different sources and show the service gives the same
answer, untouched. Create `tests/test_service.py`:

```python
"""Day 3 proof: the service works with any source, and swapping the source needs no logic change."""

from __future__ import annotations

from pathlib import Path

from reviews_insight.service import SummaryService
from reviews_insight.sources import CsvReviewSource, InMemoryReviewSource

ROWS = [
    {"product_id": "P1", "rating": "5"},
    {"product_id": "P1", "rating": "4"},
    {"product_id": "P2", "rating": "3"},
]
CSV_TEXT = "product_id,rating,text\nP1,5,great\nP1,4,good\nP2,3,ok\n"


def test_service_with_in_memory_source() -> None:
    # No file, no disk: the in-memory source satisfies the same ReviewSource contract.
    service = SummaryService(InMemoryReviewSource(ROWS))
    assert service.summarize() == {"reviews": 3, "products": 2}


def test_swapping_source_keeps_the_same_result(tmp_path: Path) -> None:
    # The same data reaches the service two ways: from a CSV file, and from memory.
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    from_file = SummaryService(CsvReviewSource(str(sample))).summarize()
    from_memory = SummaryService(InMemoryReviewSource(ROWS)).summarize()

    # The seam works: the service logic was untouched; only the injected source differed.
    assert from_file == from_memory == {"reviews": 3, "products": 2}
```

Then run the gate:

```bash
poetry run pytest -q
poetry run ruff check .
poetry run mypy src
git add .
git commit -m "day 3: source seam, injected service, one decorator, thin CLI"
```

**What happened.** The first test builds a `SummaryService` around an `InMemoryReviewSource`: no file,
no disk, just a list, and the service summarizes it. The second test is **the proof of the seam**: it
sends the same data to the service two ways, once from a real CSV file on disk and once from memory,
and asserts both give the identical result. The service code was not touched between the two runs;
only the injected source differed. That is what dependency injection buys: the source is swappable,
the logic is stable, and the test can reach the logic without a file at all. The gate is green and
the maintainable layers are committed on top of the Day 2 service.

---

## You should see

Run through this recap. If each line matches, Day 3's lab is done.

- `poetry run reviews summary` prints the timing line and the counts, with no crash:

  ```text
  [timed] summary: 0.3 ms
  [dev] reviews-insight
  reviews : 5
  products: 3
  ```

- `poetry run pytest -q` reports **8 passed**: the earlier tests still pass, and the new model and
  service tests prove the frozen value object and the seam.
- `poetry run ruff check .` and `poetry run mypy src` are both clean.
- The key point: the source was **swapped from a CSV file to an in-memory list with no change to the
  service logic**, both gave the same result, and mypy stayed clean because both sources satisfy the
  same `ReviewSource` contract by shape.

That is the Day 3 layer: the same small service is now built from parts that each do one thing. The
source sits behind a Protocol, the logic sits in a service that is handed its source, one decorator
carries the timing, and the CLI just wires the pieces together. The design choices (depend on a shape
not a file; inject the source; add cross-cutting concerns sparingly; keep the entry point thin)
are what make it maintainable, and the source-swap test proves the seam holds without a single line of
logic changing.
