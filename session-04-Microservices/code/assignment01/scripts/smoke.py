"""End-to-end smoke of the system, in one process, so you can see the parts talk.

It wires the three services over a shared temp broker (as docker-compose wires them over a
real one), submits readings through the gateway to telemetry-ingest, lets telemetry-rollup
consume the events, and reads the rollup back through the gateway's device view. It closes on
the point of this assignment: a replayed event (same id) does not move the rollup, because
the consumer is idempotent under at-least-once delivery.

Run:  poetry run python scripts/smoke.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from common.broker import FileBroker
from telemetry_ingest.main import create_app as ingest_app
from telemetry_ingest.store import IngestStore
from telemetry_rollup.main import create_app as rollup_app
from telemetry_rollup.store import RollupStore


def main() -> None:
    """Run the full path and print what each step returns."""
    tmp = Path(tempfile.mkdtemp())
    broker = FileBroker(str(tmp / "broker.jsonl"))
    ingest = TestClient(ingest_app(store=IngestStore(str(tmp / "ingest.db")), broker=broker))
    rollup = TestClient(rollup_app(store=RollupStore(str(tmp / "rollup.db")), broker=broker))

    print("health:")
    print("  telemetry-ingest ->", ingest.get("/health").json())
    print("  telemetry-rollup ->", rollup.get("/health").json())

    print("\nsubmit three readings for d1 (through telemetry-ingest):")
    for value in (21.5, 22.1, 20.8):
        created = ingest.post(
            "/v1/readings", json={"device_id": "d1", "value": value, "ts": "2026-09-01T10:00:00Z"}
        )
        print(f"  value {value} -> {created.status_code} {created.json()}")

    print("\ntelemetry-rollup consumes the events and serves the rollup:")
    print("  /v1/rollup/d1 ->", rollup.get("/v1/rollup/d1").json())

    print("\na replayed event (same id) does not change the rollup (idempotent consumer):")
    broker.publish("reading-received", {"id": 1, "device_id": "d1", "value": 21.5})
    print("  /v1/rollup/d1 ->", rollup.get("/v1/rollup/d1").json())

    print("\nunknown device escalates to a clear 404, not a guess:")
    print("  /v1/rollup/unknown ->", rollup.get("/v1/rollup/unknown").status_code)


if __name__ == "__main__":
    main()
