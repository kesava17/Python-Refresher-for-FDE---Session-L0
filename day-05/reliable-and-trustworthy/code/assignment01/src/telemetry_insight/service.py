"""The service layer (Day 3): the summary logic, with its data source injected.

This is the heart of the maintainable refactor. The counting logic lives in one place,
`summarize_rows`. The `DeviceSummaryService` holds a ReadingSource that is handed to it from
outside (dependency injection), so it never decides where the data comes from. That single
seam is what lets a test feed in-memory rows while the real application feeds a CSV file,
with the logic untouched in both cases.
"""

from __future__ import annotations

from collections.abc import Iterator

from telemetry_insight.decorators import timed
from telemetry_insight.models import ReadingParseError, parse_reading
from telemetry_insight.sources import ReadingSource


def summarize_rows(rows: Iterator[dict[str, str]]) -> dict[str, int]:
    """Count valid readings and distinct devices, rejecting bad rows honestly (from Day 4)."""
    readings = 0
    devices: set[str] = set()
    rejected = 0
    for row in rows:
        try:
            reading = parse_reading(row)
        except ReadingParseError:
            rejected += 1  # count it and move on, instead of crashing
            continue
        readings += 1
        devices.add(reading.device_id)
    return {"readings": readings, "devices": len(devices), "rejected": rejected}


class DeviceSummaryService:
    """Summarizes readings from any ReadingSource. The source is injected, not built here."""

    def __init__(self, source: ReadingSource) -> None:
        # The service depends on the ReadingSource contract, not on a file or a database.
        # Whatever satisfies the protocol can be passed in.
        self._source = source

    @timed("summary")
    def summarize(self) -> dict[str, int]:
        # All the service does is drive the injected source through the shared logic.
        return summarize_rows(self._source.rows())
