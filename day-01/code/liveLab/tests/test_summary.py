"""Tests for the reviews-insight summary."""

from __future__ import annotations

from pathlib import Path

from reviews_insight.cli import summarize
from reviews_insight.data import load_records


def test_load_and_summarize(tmp_path: Path) -> None:
    csv_text = "product_id,rating,text\nP1,5,great\nP1,4,good\nP2,3,ok\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"reviews": 3, "products": 2}
