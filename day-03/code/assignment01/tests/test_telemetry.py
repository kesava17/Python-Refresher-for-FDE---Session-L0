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
    # Threads give the same answer as serial (they just do not speed CPU work up).
    chunks = [[1.0, 2.0, 3.0], [4.0, 5.0]]
    assert run_threads(chunks) == run_serial(chunks)
