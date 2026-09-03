"""Tests for transactions-service: validation, storage, listing, and publishing an event."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from transactions_service.main import create_app
from transactions_service.store import TransactionStore


def _client(tmp_path) -> tuple[TestClient, FileBroker]:
    """Build a transactions client backed by temp store and broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    app = create_app(store=TransactionStore(str(tmp_path / "transactions.db")), broker=broker)
    return TestClient(app), broker


def test_create_transaction_ok(tmp_path) -> None:
    """A valid transaction is stored and its id returned."""
    client, _ = _client(tmp_path)
    response = client.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 500, "kind": "credit"}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_create_transaction_rejects_non_positive_amount(tmp_path) -> None:
    """An amount of zero or below is rejected at the boundary with 422."""
    client, _ = _client(tmp_path)
    response = client.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 0, "kind": "credit"}
    )
    assert response.status_code == 422


def test_create_transaction_rejects_unknown_kind(tmp_path) -> None:
    """A kind outside credit or debit is rejected at the boundary with 422."""
    client, _ = _client(tmp_path)
    response = client.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 500, "kind": "refund"}
    )
    assert response.status_code == 422


def test_create_publishes_event(tmp_path) -> None:
    """Storing a transaction publishes a transaction-recorded event carrying its details."""
    client, broker = _client(tmp_path)
    client.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 750, "kind": "debit"}
    )
    seen: list[dict] = []
    broker.drain("transaction-recorded", seen.append)
    assert seen and seen[0]["account_id"] == "acc-1"
    assert seen[0]["amount_cents"] == 750 and seen[0]["kind"] == "debit"


def test_list_transactions_for_account(tmp_path) -> None:
    """The list endpoint returns an account's transactions, oldest first."""
    client, _ = _client(tmp_path)
    client.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 500, "kind": "credit"}
    )
    client.post(
        "/v1/transactions", json={"account_id": "acc-1", "amount_cents": 200, "kind": "debit"}
    )
    client.post(
        "/v1/transactions", json={"account_id": "acc-2", "amount_cents": 900, "kind": "credit"}
    )
    body = client.get("/v1/transactions/acc-1").json()
    assert [t["amount_cents"] for t in body] == [500, 200]
    assert [t["kind"] for t in body] == ["credit", "debit"]


def test_health(tmp_path) -> None:
    """The health endpoint reports the service as ok."""
    client, _ = _client(tmp_path)
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["service"] == "transactions-service"
