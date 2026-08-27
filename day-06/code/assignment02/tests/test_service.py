"""Day 3 proof: the service works with any source, and the strategy is swappable.

Two seams are exercised here. First, the data source: a CSV file and an in-memory list reach
the same service and produce the same summary. Second, the categorization strategy: the same
transactions, categorized two different ways, yield different breakdowns while the ledger
total stays identical, because only the labelling changed.
"""

from __future__ import annotations

from pathlib import Path

from transactions_insight.service import LedgerService
from transactions_insight.sources import (
    CsvTransactionSource,
    InMemoryTransactionSource,
)
from transactions_insight.strategies import ByCurrencyStrategy, BySizeStrategy

# Five valid INR rows plus two bad ones, mirroring the shape of the sample file.
ROWS = [
    {"account_id": "A1", "amount": "120.50", "currency": "INR"},  # 12050 paise: large
    {"account_id": "A1", "amount": "80.00", "currency": "INR"},  # 8000 paise: small
    {"account_id": "A2", "amount": "15.00", "currency": "INR"},  # 1500 paise: small
    {"account_id": "A2", "amount": "300.00", "currency": "INR"},  # 30000 paise: large
    {"account_id": "A3", "amount": "45.75", "currency": "INR"},  # 4575 paise: small
    {"account_id": "A3", "amount": "-5.00", "currency": "INR"},  # bad: not positive
    {"account_id": "A4", "amount": "10.00", "currency": "USD"},  # bad: unsupported
]
CSV_TEXT = (
    "account_id,ts,amount,currency\n"
    "A1,2026-01-01T09:15:00,120.50,INR\n"
    "A1,2026-01-01T11:02:00,80.00,INR\n"
    "A2,2026-01-01T12:40:00,15.00,INR\n"
    "A2,2026-01-01T18:20:00,300.00,INR\n"
    "A3,2026-01-01T20:05:00,45.75,INR\n"
    "A3,2026-01-01T21:10:00,-5.00,INR\n"
    "A4,2026-01-01T22:00:00,10.00,USD\n"
)
EXPECTED_SUMMARY = {"transactions": 5, "accounts": 3, "rejected": 2}


def test_service_with_in_memory_source() -> None:
    # No file, no disk: the in-memory source satisfies the same TransactionSource contract.
    service = LedgerService(InMemoryTransactionSource(ROWS), BySizeStrategy())
    assert service.summarize() == EXPECTED_SUMMARY


def test_swapping_source_keeps_the_same_result(tmp_path: Path) -> None:
    # The same data reaches the service two ways: from a CSV file, and from memory.
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    from_file = LedgerService(CsvTransactionSource(str(sample)), BySizeStrategy()).summarize()
    from_memory = LedgerService(InMemoryTransactionSource(ROWS), BySizeStrategy()).summarize()

    # The seam works: the service logic was untouched; only the injected source differed.
    assert from_file == from_memory == EXPECTED_SUMMARY


def test_swapping_strategy_changes_breakdown_not_the_total() -> None:
    # Same source, same transactions; only the injected strategy differs between the two runs.
    source = InMemoryTransactionSource(ROWS)

    by_size = LedgerService(source, BySizeStrategy())
    by_currency = LedgerService(source, ByCurrencyStrategy())

    size_breakdown = by_size.categorize_all()
    currency_breakdown = by_currency.categorize_all()

    # The breakdowns differ: size splits large from small, currency buckets by code.
    assert size_breakdown == {"large": 2, "small": 3}
    assert currency_breakdown == {"INR": 5}
    assert size_breakdown != currency_breakdown

    # The ledger total is a property of the transactions, not of how we labelled them, so it
    # is identical no matter which strategy was injected.
    expected_total = 12050 + 8000 + 1500 + 30000 + 4575
    assert by_size.last_total() == by_currency.last_total() == expected_total
