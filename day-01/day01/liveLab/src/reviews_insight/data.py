"""Load records from a CSV file."""

from __future__ import annotations

import csv
from pathlib import Path


def load_records(path: str) -> list[dict[str, str]]:
    """Read the CSV file into a list of dicts. Fail clearly if it is missing."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"data file not found: {path}")
    with file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{key: str(value) for key, value in row.items()} for row in reader]
