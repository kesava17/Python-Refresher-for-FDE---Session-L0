"""Tests for reviews-query: building the read model from events, and idempotency."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from reviews_query.main import create_app
from reviews_query.store import QueryStore


def _client(tmp_path) -> tuple[TestClient, FileBroker]:
    """Build a query client backed by temp store and broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    app = create_app(store=QueryStore(str(tmp_path / "query.db")), broker=broker)
    return TestClient(app), broker


def test_aggregate_from_events(tmp_path) -> None:
    """Two events for one product produce the right count and average."""
    client, broker = _client(tmp_path)
    broker.publish("review-received", {"id": 1, "product_id": "p1", "rating": 4})
    broker.publish("review-received", {"id": 2, "product_id": "p1", "rating": 2})
    body = client.get("/v1/aggregates/p1").json()
    assert body["count"] == 2
    assert body["average_rating"] == 3.0


def test_unknown_product_is_404(tmp_path) -> None:
    """A product with no reviews returns 404, not a guessed zero."""
    client, _ = _client(tmp_path)
    assert client.get("/v1/aggregates/nope").status_code == 404


def test_consumer_is_idempotent(tmp_path) -> None:
    """A redelivered event (same id) does not double-count."""
    client, broker = _client(tmp_path)
    broker.publish("review-received", {"id": 1, "product_id": "p1", "rating": 5})
    client.get("/v1/aggregates/p1")  # drains id 1 once
    broker.publish("review-received", {"id": 1, "product_id": "p1", "rating": 5})  # duplicate
    body = client.get("/v1/aggregates/p1").json()
    assert body["count"] == 1
