"""Tests for reviews-ingest: validation, storage, and publishing an event."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from reviews_ingest.main import create_app
from reviews_ingest.store import IngestStore


def _client(tmp_path) -> tuple[TestClient, FileBroker]:
    """Build an ingest client backed by temp store and broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    app = create_app(store=IngestStore(str(tmp_path / "ingest.db")), broker=broker)
    return TestClient(app), broker


def test_create_review_ok(tmp_path) -> None:
    """A valid review is stored and its id returned."""
    client, _ = _client(tmp_path)
    response = client.post("/v1/reviews", json={"product_id": "p1", "rating": 5, "text": "great"})
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_create_review_rejects_bad_rating(tmp_path) -> None:
    """A rating outside 1 to 5 is rejected at the boundary with 422."""
    client, _ = _client(tmp_path)
    response = client.post("/v1/reviews", json={"product_id": "p1", "rating": 7, "text": "x"})
    assert response.status_code == 422


def test_create_publishes_event(tmp_path) -> None:
    """Storing a review publishes a review-received event carrying its details."""
    client, broker = _client(tmp_path)
    client.post("/v1/reviews", json={"product_id": "p1", "rating": 4, "text": "ok"})
    seen: list[dict] = []
    broker.drain("review-received", seen.append)
    assert seen and seen[0]["product_id"] == "p1" and seen[0]["rating"] == 4


def test_health(tmp_path) -> None:
    """The health endpoint reports the service as ok."""
    client, _ = _client(tmp_path)
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["service"] == "reviews-ingest"
