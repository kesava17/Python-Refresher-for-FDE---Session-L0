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
