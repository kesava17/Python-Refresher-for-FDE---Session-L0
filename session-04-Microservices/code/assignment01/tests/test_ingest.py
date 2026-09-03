"""Tests for telemetry-ingest: validation, storage, and publishing an event."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from telemetry_ingest.main import create_app
from telemetry_ingest.store import IngestStore


def _client(tmp_path) -> tuple[TestClient, FileBroker]:
    """Build an ingest client backed by temp store and broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    app = create_app(store=IngestStore(str(tmp_path / "ingest.db")), broker=broker)
    return TestClient(app), broker


def test_create_reading_ok(tmp_path) -> None:
    """A valid reading is stored and its id returned."""
    client, _ = _client(tmp_path)
    response = client.post(
        "/v1/readings", json={"device_id": "d1", "value": 21.5, "ts": "2026-09-01T10:00:00Z"}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_create_reading_rejects_missing_device(tmp_path) -> None:
    """An empty device_id is rejected at the boundary with 422."""
    client, _ = _client(tmp_path)
    response = client.post(
        "/v1/readings", json={"device_id": "", "value": 21.5, "ts": "2026-09-01T10:00:00Z"}
    )
    assert response.status_code == 422


def test_create_publishes_event(tmp_path) -> None:
    """Storing a reading publishes a reading-received event carrying its details."""
    client, broker = _client(tmp_path)
    client.post(
        "/v1/readings", json={"device_id": "d1", "value": 21.5, "ts": "2026-09-01T10:00:00Z"}
    )
    seen: list[dict] = []
    broker.drain("reading-received", seen.append)
    assert seen and seen[0]["device_id"] == "d1" and seen[0]["value"] == 21.5


def test_health(tmp_path) -> None:
    """The health endpoint reports the service as ok."""
    client, _ = _client(tmp_path)
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["service"] == "telemetry-ingest"
