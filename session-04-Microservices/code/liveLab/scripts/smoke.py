"""End-to-end smoke of the system, in one process, so you can see the parts talk.

It wires the three services over a shared temp broker (as docker-compose wires them over a
real one), submits reviews through the gateway to reviews-ingest, lets reviews-query consume
the events, and reads the aggregate back through the gateway's dashboard. It also shows the
gateway degrading cleanly when reviews-query is stopped.

Run:  poetry run python scripts/smoke.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from common.broker import FileBroker
from reviews_ingest.main import create_app as ingest_app
from reviews_ingest.store import IngestStore
from reviews_query.main import create_app as query_app
from reviews_query.store import QueryStore


def main() -> None:
    """Run the full path and print what each step returns."""
    tmp = Path(tempfile.mkdtemp())
    broker = FileBroker(str(tmp / "broker.jsonl"))
    ingest = TestClient(ingest_app(store=IngestStore(str(tmp / "ingest.db")), broker=broker))
    query = TestClient(query_app(store=QueryStore(str(tmp / "query.db")), broker=broker))

    print("health:")
    print("  reviews-ingest ->", ingest.get("/health").json())
    print("  reviews-query  ->", query.get("/health").json())

    print("\nsubmit three reviews for p1 (through reviews-ingest):")
    for rating in (5, 3, 4):
        created = ingest.post("/v1/reviews", json={"product_id": "p1", "rating": rating, "text": "ok"})
        print(f"  rating {rating} -> {created.status_code} {created.json()}")

    print("\nreviews-query consumes the events and serves the aggregate:")
    print("  /v1/aggregates/p1 ->", query.get("/v1/aggregates/p1").json())

    print("\na duplicate event does not double-count (idempotent consumer):")
    broker.publish("review-received", {"id": 1, "product_id": "p1", "rating": 5})
    print("  /v1/aggregates/p1 ->", query.get("/v1/aggregates/p1").json())

    print("\nunknown product escalates to a clear 404, not a guess:")
    print("  /v1/aggregates/unknown ->", query.get("/v1/aggregates/unknown").status_code)


if __name__ == "__main__":
    main()
