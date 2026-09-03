"""Tests for ledger-service: building the summary from events, and idempotency."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from ledger_service.main import create_app
from ledger_service.store import LedgerStore


def _client(tmp_path) -> tuple[TestClient, FileBroker]:
    """Build a ledger client backed by temp store and broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    app = create_app(store=LedgerStore(str(tmp_path / "ledger.db")), broker=broker)
    return TestClient(app), broker


def test_summary_from_events(tmp_path) -> None:
    """A credit and a debit for one account produce the right count and balance."""
    client, broker = _client(tmp_path)
    broker.publish(
        "transaction-recorded",
        {"id": 1, "account_id": "acc-1", "amount_cents": 500, "kind": "credit"},
    )
    broker.publish(
        "transaction-recorded",
        {"id": 2, "account_id": "acc-1", "amount_cents": 200, "kind": "debit"},
    )
    body = client.get("/v1/accounts/acc-1/summary").json()
    assert body["count"] == 2
    assert body["balance_cents"] == 300


def test_unknown_account_is_404(tmp_path) -> None:
    """An account with no transactions returns 404, not a guessed zero balance."""
    client, _ = _client(tmp_path)
    assert client.get("/v1/accounts/nope/summary").status_code == 404


def test_consumer_is_idempotent(tmp_path) -> None:
    """A redelivered event (same id) does not double-count the balance."""
    client, broker = _client(tmp_path)
    broker.publish(
        "transaction-recorded",
        {"id": 1, "account_id": "acc-1", "amount_cents": 500, "kind": "credit"},
    )
    client.get("/v1/accounts/acc-1/summary")  # drains id 1 once
    broker.publish(
        "transaction-recorded",
        {"id": 1, "account_id": "acc-1", "amount_cents": 500, "kind": "credit"},
    )  # duplicate
    body = client.get("/v1/accounts/acc-1/summary").json()
    assert body["count"] == 1
    assert body["balance_cents"] == 500
