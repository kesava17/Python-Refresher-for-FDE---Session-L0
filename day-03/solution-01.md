# Solution 01 · Make telemetry-insight maintainable

> The full worked solution for Assignment 01. Try the assignment yourself first. This is
> here to check your work, or to unstick you when you're truly stuck.

You start from your `telemetry-insight` project, green, with the Day 2 streaming service in place.
This solution adds the Day 3 maintainable refactor: a `ReadingSource` contract with two
interchangeable implementations, a `DeviceSummaryService` that receives its source instead of
building it, a `timed` decorator that carries the one cross-cutting concern, and a CLI that
shrinks to a thin composition root. Use `poetry run` for everything.

The result you are after: the behaviour is unchanged, `telemetry summary` still prints five
readings across three devices, but the service now depends on a contract, and a
test can swap a CSV file for an in-memory list with no change to the logic.

## Step 1: the source seam

The seam the whole refactor turns on. A `Protocol` describes a source by its shape: anything with a
`rows()` method that yields telemetry rows counts as a `ReadingSource`, with no base class to
inherit. The CSV source streams from disk for the real application; the in-memory source hands over
a list for tests. Both satisfy the same contract without knowing about each other.

**`src/telemetry_insight/sources.py`**

```python
"""The data-source seam (new on Day 3): a small Protocol, and two interchangeable sources.

A Protocol describes a contract by its shape: any object that has a `rows()` method
returning telemetry rows counts as a ReadingSource, with no base class to inherit. This is
what lets the service depend on the contract, not on where the data actually comes from.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol

from telemetry_insight.data import open_records


class ReadingSource(Protocol):
    """The contract the service depends on: something that can hand over telemetry rows."""

    def rows(self) -> Iterator[dict[str, str]]:
        """Yield raw telemetry rows, one dictionary at a time."""
        ...


class CsvReadingSource:
    """A ReadingSource backed by a CSV file on disk. Used in the real application."""

    def __init__(self, path: str) -> None:
        self._path = path

    def rows(self) -> Iterator[dict[str, str]]:
        # open_records is a context manager that streams rows and always closes the file.
        # Yielding from inside the `with` keeps the file open only while it is being read.
        with open_records(self._path) as stream:
            yield from stream


class InMemoryReadingSource:
    """A ReadingSource backed by a list already in memory. Ideal for tests: no file needed."""

    def __init__(self, rows: Sequence[dict[str, str]]) -> None:
        self._rows = list(rows)

    def rows(self) -> Iterator[dict[str, str]]:
        return iter(self._rows)
```

Neither source inherits from `ReadingSource`. They each have a `rows()` method of the right shape,
and for a `Protocol` that is enough. The CSV source `yield from`s inside the `with` block, so the
file stays open only while it is being read and is always closed afterwards. The in-memory source
copies its rows into a list so the caller cannot mutate them mid-iteration.

## Step 2: the service that receives its source

The heart of the maintainable refactor. The counting logic lives once in `summarize_rows`. The
`DeviceSummaryService` holds a `ReadingSource` handed to it from outside, so it never decides where
the data comes from. That single seam is what lets a test feed in-memory rows while the real
application feeds a CSV file, with the logic untouched in both cases.

**`src/telemetry_insight/service.py`**

```python
"""The service layer, new on Day 3: the summary logic, with its data source injected.

New this day: the counting logic moves into one place (`summarize_rows`), and
`DeviceSummaryService` receives a `ReadingSource` from outside (dependency injection) instead of
building one. That seam lets a test feed in-memory rows while the real app feeds a CSV file, with
the logic unchanged.
"""

from __future__ import annotations

from collections.abc import Iterator

from telemetry_insight.decorators import timed
from telemetry_insight.models import parse_reading
from telemetry_insight.sources import ReadingSource


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count readings and distinct devices from a stream of rows."""
    readings = 0
    devices: set[str] = set()
    for row in rows:
        reading = parse_reading(row)
        readings += 1
        devices.add(reading.device_id)
    return {"readings": readings, "devices": len(devices)}


class DeviceSummaryService:
    """Summarizes readings from any ReadingSource. The source is injected, not built here."""

    def __init__(self, source: ReadingSource) -> None:
        # The service depends on the ReadingSource contract, not on a file or a database.
        self._source = source

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())
```

The type of the constructor parameter is `ReadingSource`, the contract, not a concrete class. That
one choice is the whole seam. `summarize_rows` is the counting loop lifted out as a free
function, so the same logic serves every source. The service does nothing but connect the injected
source to that shared logic.

## Step 3: the cross-cutting concern

Timing is a concern many methods share but none of them should be cluttered with. A decorator lets
us add it in one place and apply it by name, without editing the logic it wraps. The typing keeps
the wrapped function's signature intact, so mypy still checks callers exactly as before.

**`src/telemetry_insight/decorators.py`**

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

The `try`/`finally` reports the elapsed time whether the wrapped call returns or raises. `@wraps`
keeps the wrapped function's identity, and `ParamSpec` plus `TypeVar` preserve its type, so
decorating `summarize` costs nothing in type safety.

## Step 4: the thin composition root

The CLI's only jobs now are to read configuration, build the concrete pieces, wire them together,
and print the result. All the real logic lives in the service, so this surface stays small and easy
to read.

**`src/telemetry_insight/cli.py`**

```python
"""Command line entry point (new on Day 3: a thin composition root).

New this day: the CLI no longer holds the logic. It builds the concrete source, injects it into
the service, and prints. All the real work lives in the service.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from telemetry_insight.config import Config
from telemetry_insight.service import DeviceSummaryService
from telemetry_insight.sources import CsvReadingSource


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    """Day 2: summarize a stream without holding the rows, in constant memory."""
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

    # Composition root: build the source, inject it into the service, run it.
    source = CsvReadingSource(config.data_path)
    service = DeviceSummaryService(source)
    result = service.summarize()

    print(f"[{config.environment}] {config.app_name}")
    print(f"readings: {result['readings']}")
    print(f"devices : {result['devices']}")


if __name__ == "__main__":
    main()
```

`main` reads like a wiring diagram: build the source, inject it into the service, ask for the
result, print it. The earlier `summarize_stream` (Day 2) stays as it was. All the counting now
lives once in the service's `summarize_rows`, so there is one counting loop in the codebase, not
copies of it.

## Step 5: run it

```bash
poetry run telemetry summary
```

```text
[timed] summary: 0.2 ms
[dev] telemetry-insight
readings: 5
devices : 3
```

The same five readings across three devices as before. The refactor changed
how the program is built, not what it does. The one visible addition is the `[timed]` line from the
decorator, reporting how long the summary took.

## Step 6: the test that swaps the reader

The deliverable proof. The service is built twice over the same data: once from a CSV file written
to a temporary path, once from an in-memory list. Both `summarize()` calls return the identical
result, and the service logic was never touched between them. Only the injected source differed.

**`tests/test_service.py`**

```python
"""Day 3 proof: the service works with any source, and swapping the source needs no logic change."""

from __future__ import annotations

from pathlib import Path

from telemetry_insight.service import DeviceSummaryService
from telemetry_insight.sources import CsvReadingSource, InMemoryReadingSource

ROWS = [
    {"device_id": "D1", "value": "21.4"},
    {"device_id": "D1", "value": "21.9"},
    {"device_id": "D2", "value": "4.1"},
]
CSV_TEXT = "device_id,ts,value\nD1,t0,21.4\nD1,t1,21.9\nD2,t2,4.1\n"


def test_service_with_in_memory_source() -> None:
    # No file, no disk: the in-memory source satisfies the same ReadingSource contract.
    service = DeviceSummaryService(InMemoryReadingSource(ROWS))
    assert service.summarize() == {"readings": 3, "devices": 2}


def test_swapping_source_keeps_the_same_result(tmp_path: Path) -> None:
    # The same data reaches the service two ways: from a CSV file, and from memory.
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    from_file = DeviceSummaryService(CsvReadingSource(str(sample))).summarize()
    from_memory = DeviceSummaryService(InMemoryReadingSource(ROWS)).summarize()

    # The seam works: the service logic was untouched; only the injected source differed.
    assert from_file == from_memory == {"readings": 3, "devices": 2}
```

The first test proves the mock path stands on its own: an in-memory source, no file, the same
contract. The second is the proof the assignment asks for: the same data reaches the service from a
CSV file and from memory, and the two results are identical because the service depends on the
`ReadingSource` contract, not on where the rows live. That is what makes the code maintainable, and
testable without touching disk.

## Step 7: green gate and commit

```bash
poetry run pytest -q          # all pass
poetry run ruff check .       # All checks passed!
poetry run mypy src           # Success: no issues found
git add .
git commit -m "day 3: refactor telemetry-insight into maintainable layers with an injected source"
```

## Done when

- A `ReadingSource` `Protocol` exists, with a `CsvReadingSource` and an `InMemoryReadingSource` that
  both satisfy it without inheriting from it.
- `DeviceSummaryService` receives its source through its constructor, and `summarize_rows` holds the
  counting logic in one place.
- A `timed` decorator adds timing to `summarize` without touching the counting logic, and mypy still
  checks callers as before.
- `main` is a thin composition root: it builds the source, injects it, runs the service, and prints.
- `telemetry summary` still prints `readings: 5`, `devices : 3`.
- The test swaps a CSV source for an in-memory source with no change to the service, and both give
  the same result.
- `pytest`, `ruff`, and `mypy` are all green, and the layer is committed.

You have shown the Day 3 point: separating a program along its seams leaves the behaviour identical
but makes the code easy to change and easy to test, because the logic no longer depends on where its
data lives.
