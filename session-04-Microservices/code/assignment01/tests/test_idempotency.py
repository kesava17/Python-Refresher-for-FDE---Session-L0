"""The replay proof: at-least-once delivery means duplicates, so the consumer must be idempotent.

At-least-once delivery guarantees an event arrives, but it can arrive more than once. This
test publishes an event, drains it, then republishes the SAME id and drains again, and
asserts the rollup (count and average value) has not moved. That is the property that makes
the asynchronous read model safe under redelivery.
"""

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


def test_replayed_event_does_not_change_the_rollup(tmp_path) -> None:
    """Publishing the same event id twice leaves count and average value unchanged."""
    client, broker = _client(tmp_path)

    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 10.0})
    broker.publish("reading-received", {"id": 2, "device_id": "d1", "value": 20.0})
    first = client.get("/v1/rollup/d1").json()  # drains ids 1 and 2 once
    assert first["count"] == 2
    assert first["average_value"] == 15.0

    # A redelivery of an already-processed id (at-least-once delivery in action).
    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 10.0})
    second = client.get("/v1/rollup/d1").json()  # drains again; the duplicate is skipped

    assert second["count"] == first["count"]
    assert second["average_value"] == first["average_value"]


def test_second_drain_applies_nothing_after_replay(tmp_path) -> None:
    """A drain over only duplicate events reports zero applied, proving nothing was re-folded."""
    client, broker = _client(tmp_path)
    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 7.0})
    client.post("/internal/drain")  # applies id 1

    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 7.0})  # same id
    assert client.post("/internal/drain").json() == {"applied": 0}
