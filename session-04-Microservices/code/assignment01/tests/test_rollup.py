"""Tests for telemetry-rollup: building the read model from events, and the 404 for unknowns."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from telemetry_rollup.main import create_app
from telemetry_rollup.store import RollupStore


def _client(tmp_path) -> tuple[TestClient, FileBroker]:
    """Build a rollup client backed by temp store and broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))
    app = create_app(store=RollupStore(str(tmp_path / "rollup.db")), broker=broker)
    return TestClient(app), broker


def test_rollup_from_events(tmp_path) -> None:
    """Two events for one device produce the right count and average value."""
    client, broker = _client(tmp_path)
    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 4.0})
    broker.publish("reading-received", {"id": 2, "device_id": "d1", "value": 2.0})
    body = client.get("/v1/rollup/d1").json()
    assert body["count"] == 2
    assert body["average_value"] == 3.0


def test_unknown_device_is_404(tmp_path) -> None:
    """A device with no readings returns 404, not a guessed zero."""
    client, _ = _client(tmp_path)
    assert client.get("/v1/rollup/nope").status_code == 404


def test_drain_endpoint_reports_applied(tmp_path) -> None:
    """The internal drain endpoint consumes pending events and reports how many it applied."""
    client, broker = _client(tmp_path)
    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 5.0})
    assert client.post("/internal/drain").json() == {"applied": 1}
    assert client.post("/internal/drain").json() == {"applied": 0}
