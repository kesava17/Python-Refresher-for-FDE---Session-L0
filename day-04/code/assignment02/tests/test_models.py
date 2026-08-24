"""Tests for the Day 4 reliability layer: validated Transaction and the account ledger."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from transactions_insight.cli import summarize_validated
from transactions_insight.models import (
    AccountLedger,
    Transaction,
    TransactionParseError,
    parse_transaction,
)


def test_transaction_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        Transaction(account_id="A1", amount_paise=-5, currency="INR")  # not positive
    with pytest.raises(ValueError):
        Transaction(account_id="A1", amount_paise=100, currency="USD")  # unsupported
    with pytest.raises(ValueError):
        Transaction(account_id="", amount_paise=100, currency="INR")  # empty id


def test_transaction_is_frozen() -> None:
    txn = Transaction(account_id="A1", amount_paise=100, currency="INR")
    with pytest.raises(FrozenInstanceError):
        txn.amount_paise = 200  # type: ignore[misc]


def test_parse_rejects_malformed_rows() -> None:
    with pytest.raises(TransactionParseError):
        parse_transaction({"account_id": "A1", "amount": "free", "currency": "INR"})
    with pytest.raises(TransactionParseError):
        parse_transaction({"account_id": "A1", "amount": "10.0"})  # missing currency


def test_ledger_total_equals_sum_of_applied() -> None:
    ledger = AccountLedger()
    txns = [
        Transaction("A1", 100, "INR"),
        Transaction("A1", 250, "INR"),
        Transaction("A2", 500, "INR"),
    ]
    for txn in txns:
        ledger.apply(txn)
    # The invariant: the ledger total is exactly the sum of every amount applied.
    assert ledger.total() == sum(txn.amount_paise for txn in txns)
    assert ledger.balance("A1") == 350
    assert ledger.balance("A2") == 500


def test_summarize_counts_good_and_rejects_bad() -> None:
    rows = [
        {"account_id": "A1", "amount": "10.00", "currency": "INR"},
        {"account_id": "A2", "amount": "5.00", "currency": "INR"},
        {"account_id": "A3", "amount": "-5.00", "currency": "INR"},  # bad: not positive
        {"account_id": "A4", "amount": "10.00", "currency": "USD"},  # bad: unsupported
    ]
    result = summarize_validated(iter(rows))
    assert result == {"transactions": 2, "accounts": 2, "rejected": 2}
