"""Tests for the transactions-insight summary."""

from __future__ import annotations

from pathlib import Path

from transactions_insight.cli import summarize
from transactions_insight.data import load_records


def test_load_and_summarize(tmp_path: Path) -> None:
    csv_text = "account_id,amount,currency\nA1,250.00,INR\nA1,90.50,INR\nA2,1200.00,INR\n"
    sample = tmp_path / "sample.csv"
    sample.write_text(csv_text, encoding="utf-8")

    records = load_records(str(sample))
    assert len(records) == 3
    assert summarize(records) == {"transactions": 3, "accounts": 2, "total": 1540.5}
