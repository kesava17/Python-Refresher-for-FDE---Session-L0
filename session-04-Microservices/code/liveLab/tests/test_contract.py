"""Contract tests: the two services must agree on the shapes they exchange.

These pin the event and API shapes both sides rely on, plus one end-to-end path (ingest
publishes, query consumes through a shared broker) so a contract change on one side cannot
silently break the other.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from contracts.review import Aggregate, ReviewReceived
from reviews_ingest.main import create_app as ingest_app
from reviews_ingest.store import IngestStore
from reviews_query.main import create_app as query_app
from reviews_query.store import QueryStore


def test_event_contract_fields() -> None:
    """The review-received event carries exactly id, product_id, and rating."""
    event = ReviewReceived(id=1, product_id="p1", rating=5)
    assert set(event.model_dump()) == {"id", "product_id", "rating"}


def test_aggregate_contract_fields() -> None:
    """The aggregate carries product_id, count, and average_rating."""
    aggregate = Aggregate(product_id="p1", count=2, average_rating=3.0)
    assert set(aggregate.model_dump()) == {"product_id", "count", "average_rating"}


def test_ingest_to_query_end_to_end(tmp_path) -> None:
    """A review posted to ingest reaches the query read model through the shared broker."""
    broker = FileBroker(str(tmp_path / "broker.jsonl"))  # the two services share one broker
    ingest = TestClient(ingest_app(store=IngestStore(str(tmp_path / "ingest.db")), broker=broker))
    query = TestClient(query_app(store=QueryStore(str(tmp_path / "query.db")), broker=broker))

    ingest.post("/v1/reviews", json={"product_id": "p1", "rating": 5, "text": "great"})
    ingest.post("/v1/reviews", json={"product_id": "p1", "rating": 3, "text": "ok"})

    body = query.get("/v1/aggregates/p1").json()
    assert body == {"product_id": "p1", "count": 2, "average_rating": 4.0}
