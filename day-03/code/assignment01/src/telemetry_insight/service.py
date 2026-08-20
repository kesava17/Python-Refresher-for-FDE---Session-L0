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
