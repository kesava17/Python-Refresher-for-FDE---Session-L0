"""Tests for the telemetry-insight summary."""

from __future__ import annotations

from pathlib import Path

from telemetry_insight.cli import summarize
from telemetry_insight.data import load_records


def test_load_and_summarize(tmp_path: Path) -> None:
    csv_text = "device_id,ts,value\nD1,2026-01-01T00:00:00,1.0\nD1,2026-01-01T00:01:00,2.0\nD2,2026-01-01T00:00:00,3.0\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"readings": 3, "devices": 2}
