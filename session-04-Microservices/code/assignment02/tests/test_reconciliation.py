"""Reconciliation test: the ledger balance equals credits minus debits, to the paise.

This is the correctness-critical property of the domain. Money moves through the system as
integer minor units the whole way, so the summed balance the ledger serves must match the
arithmetic on the recorded transactions exactly, with no float rounding anywhere.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from ledger_service.main import create_app as ledger_app
from ledger_service.store import LedgerStore
from transactions_service.main import create_app as transactions_app
from transactions_service.store import TransactionStore

# A mixed run of credits and debits for one account, in integer minor units (paise).
_LEDGER_RUN = [
    ("credit", 100_00),
    ("debit", 30_00),
    ("credit", 5_50),
    ("debit", 1_25),
    ("credit", 12_75),
]


def test_balance_equals_credits_minus_debits(tmp_path) -> None:
    """Post a mixed run through the write side and confirm the ledger reconciles exactly."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    transactions = TestClient(
        transactions_app(store=TransactionStore(str(tmp_path / "transactions.db")), broker=broker)
    )
    ledger = TestClient(ledger_app(store=LedgerStore(str(tmp_path / "ledger.db")), broker=broker))

    for kind, amount_cents in _LEDGER_RUN:
        transactions.post(
            "/v1/transactions",
            json={"account_id": "acc-1", "amount_cents": amount_cents, "kind": kind},
        )

    expected_balance = sum(
        amount_cents if kind == "credit" else -amount_cents for kind, amount_cents in _LEDGER_RUN
    )
    body = ledger.get("/v1/accounts/acc-1/summary").json()
    assert body["count"] == len(_LEDGER_RUN)
    assert body["balance_cents"] == expected_balance
    assert isinstance(body["balance_cents"], int)  # money stays an integer, never a float


def test_balance_reconciles_against_the_listed_transactions(tmp_path) -> None:
    """The ledger balance matches the sum over the transactions the write side lists back."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    transactions = TestClient(
        transactions_app(store=TransactionStore(str(tmp_path / "transactions.db")), broker=broker)
    )
    ledger = TestClient(ledger_app(store=LedgerStore(str(tmp_path / "ledger.db")), broker=broker))

    for kind, amount_cents in _LEDGER_RUN:
        transactions.post(
            "/v1/transactions",
            json={"account_id": "acc-1", "amount_cents": amount_cents, "kind": kind},
        )

    recorded = transactions.get("/v1/transactions/acc-1").json()
    reconciled = sum(
        row["amount_cents"] if row["kind"] == "credit" else -row["amount_cents"] for row in recorded
    )
    summary = ledger.get("/v1/accounts/acc-1/summary").json()
    assert summary["balance_cents"] == reconciled
