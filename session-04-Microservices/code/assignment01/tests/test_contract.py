"""Contract tests: the two services must agree on the shapes they exchange.

These pin the event and API shapes both sides rely on, plus one end-to-end path (ingest
publishes, rollup consumes through a shared broker) so a contract change on one side cannot
silently break the other.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from contracts.reading import ReadingReceived, Rollup
from telemetry_ingest.main import create_app as ingest_app
from telemetry_ingest.store import IngestStore
from telemetry_rollup.main import create_app as rollup_app
from telemetry_rollup.store import RollupStore


def test_event_contract_fields() -> None:
    """The reading-received event carries exactly id, device_id, and value."""
    event = ReadingReceived(id=1, device_id="d1", value=21.5)
    assert set(event.model_dump()) == {"id", "device_id", "value"}


def test_rollup_contract_fields() -> None:
    """The rollup carries device_id, count, and average_value."""
    rollup = Rollup(device_id="d1", count=2, average_value=3.0)
    assert set(rollup.model_dump()) == {"device_id", "count", "average_value"}


def test_ingest_to_rollup_end_to_end(tmp_path) -> None:
    """A reading posted to ingest reaches the rollup read model through the shared broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))  # the two services share one broker
    ingest = TestClient(ingest_app(store=IngestStore(str(tmp_path / "ingest.db")), broker=broker))
    rollup = TestClient(rollup_app(store=RollupStore(str(tmp_path / "rollup.db")), broker=broker))

    ingest.post("/v1/readings", json={"device_id": "d1", "value": 5.0, "ts": "2026-09-01T10:00:00Z"})
    ingest.post("/v1/readings", json={"device_id": "d1", "value": 3.0, "ts": "2026-09-01T10:01:00Z"})

    body = rollup.get("/v1/rollup/d1").json()
    assert body == {"device_id": "d1", "count": 2, "average_value": 4.0}
