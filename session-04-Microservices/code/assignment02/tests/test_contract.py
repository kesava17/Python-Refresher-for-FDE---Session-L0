"""Contract tests: the two services must agree on the shapes they exchange.

These pin the event and API shapes both sides rely on, plus one end-to-end path (transactions
publishes, ledger consumes through a shared broker) so a contract change on one side cannot
silently break the other.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from contracts.transaction import AccountSummary, TransactionRecorded
from ledger_service.main import create_app as ledger_app
from ledger_service.store import LedgerStore
from transactions_service.main import create_app as transactions_app
from transactions_service.store import TransactionStore


def test_event_contract_fields() -> None:
    """The transaction-recorded event carries exactly id, account_id, amount_cents, and kind."""
    event = TransactionRecorded(id=1, account_id="acc-1", amount_cents=500, kind="credit")
    assert set(event.model_dump()) == {"id", "account_id", "amount_cents", "kind"}


def test_summary_contract_fields() -> None:
    """The account summary carries account_id, count, and balance_cents."""
    summary = AccountSummary(account_id="acc-1", count=2, balance_cents=300)
    assert set(summary.model_dump()) == {"account_id", "count", "balance_cents"}


def test_transactions_to_ledger_end_to_end(tmp_path) -> None:
    """A transaction posted to the write side reaches the ledger read model via the shared broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))  # the two services share one broker
    transactions = TestClient(
        transactions_app(store=TransactionStore(str(tmp_path / "transactions.db")), broker=broker)
    )
    ledger = TestClient(ledger_app(store=LedgerStore(str(tmp_path / "ledger.db")), broker=broker))

    transactions.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 500, "kind": "credit"}
    )
    transactions.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 200, "kind": "debit"}
    )

    body = ledger.get("/v1/accounts/acc-1/summary").json()
    assert body == {"account_id": "acc-1", "count": 2, "balance_cents": 300}
