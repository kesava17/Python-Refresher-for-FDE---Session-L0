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
