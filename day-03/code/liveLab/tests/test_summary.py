"""Tests for reviews-insight: eager summary, streaming summary, and enrichment."""

from __future__ import annotations

from pathlib import Path

from reviews_insight.cli import summarize, summarize_stream
from reviews_insight.data import load_records, open_records
from reviews_insight.enrich import enrich_concurrent, enrich_serial

CSV_TEXT = "product_id,rating,text\nP1,5,great\nP1,4,good\nP2,3,ok\n"


def test_load_and_summarize(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"reviews": 3, "products": 2}


def test_stream_matches_eager(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    with open_records(str(sample)) as stream:
        assert summarize_stream(stream) == {"reviews": 3, "products": 2}


def test_concurrent_matches_serial() -> None:
    product_ids = [f"P{i}" for i in range(20)]
    assert enrich_concurrent(product_ids) == enrich_serial(product_ids)
