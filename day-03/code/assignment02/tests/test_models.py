"""Tests for the Day 3 value object and the account ledger."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from transactions_insight.models import AccountLedger, Transaction, parse_transaction


def test_transaction_is_frozen() -> None:
    txn = Transaction(account_id="A1", amount_paise=100, currency="INR")
    with pytest.raises(FrozenInstanceError):
        txn.amount_paise = 200  # type: ignore[misc]  # frozen: cannot reassign


def test_transactions_compare_by_value() -> None:
    assert Transaction("A1", 100, "INR") == Transaction("A1", 100, "INR")
    assert Transaction("A1", 100, "INR") != Transaction("A1", 200, "INR")


def test_parse_builds_a_transaction() -> None:
    row = {"account_id": "A1", "amount": "120.50", "currency": "INR"}
    assert parse_transaction(row) == Transaction("A1", 12050, "INR")


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
