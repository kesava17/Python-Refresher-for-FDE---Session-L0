"""Dependability-layer tests, tuned for the telemetry domain (durability under load).

These prove the four dependability behaviors added on top of the interoperable base:
idempotency on ingest, load shedding through bounded concurrency, graceful sink degradation
under fault injection, and a readiness route that reflects real capacity.
"""

from __future__ import annotations

import asyncio

import httpx
from fastapi.testclient import TestClient

from telemetry_insight.api import create_app
from telemetry_insight.sink import forward_or_buffer


def _client(**kwargs: object) -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app(**kwargs))  # type: ignore[arg-type]


def test_idempotent_ingest_stores_once() -> None:
    client = _client()
    reading = {"device_id": "D1", "value": 20.5}
    headers = {"Idempotency-Key": "dedupe-1"}
    # The same reading redelivered with the same key must be stored only once.
    first = client.post("/v1/readings", json=reading, headers=headers)
    second = client.post("/v1/readings", json=reading, headers=headers)
    assert first.status_code == 201
    assert first.json()["status"] == "accepted"
    assert second.json()["status"] == "duplicate"  # the redelivery is recognized
    assert client.get("/v1/insight").json()["readings"] == 1  # not stored twice


def test_load_shedding_returns_429_when_full() -> None:
    app = create_app(max_concurrent=2)
    client = TestClient(app)
    capacity = app.state.capacity
    # Simulate two units of accepted work already in flight by filling both slots.
    assert capacity.try_acquire() is True
    assert capacity.try_acquire() is True
    # With no free capacity, excess ingest is shed fast with a 429.
    shed = client.post("/v1/readings", json={"device_id": "D1", "value": 20.0})
    assert shed.status_code == 429
    # Free the slots (the accepted work finished) and ingest succeeds again.
    capacity.release()
    capacity.release()
    ok = client.post("/v1/readings", json={"device_id": "D1", "value": 20.0})
    assert ok.status_code == 201


def test_sink_degrades_gracefully_on_timeout() -> None:
    # Fault injection: a mock sink client whose post always times out.
    class _TimingOutClient:
        async def post(self, *args: object, **kwargs: object) -> httpx.Response:
            raise httpx.TimeoutException("sink too slow")

    reading: dict[str, object] = {"device_id": "D1", "value": 20.0}
    # Test the async function directly with asyncio.run plus the mock, no pytest-asyncio needed.
    outcome = asyncio.run(forward_or_buffer(reading, _TimingOutClient()))  # type: ignore[arg-type]
    # Ingest degrades gracefully: the reading is buffered, marked not forwarded, never raised.
    assert outcome["forwarded"] is False
    assert outcome["device_id"] == "D1"


def test_ready_returns_200_with_free_capacity() -> None:
    client = _client()
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_ready_returns_503_when_no_capacity() -> None:
    app = create_app(max_concurrent=1)
    client = TestClient(app)
    # Fill the only slot: readiness must now report no free capacity with a 503.
    app.state.capacity.try_acquire()
    resp = client.get("/ready")
    assert resp.status_code == 503
    assert resp.json()["status"] == "unavailable"


def test_metrics_expose_request_and_error_counts() -> None:
    client = _client()
    client.get("/health")
    body = client.get("/metrics").text
    # Hand-rolled plain-text SLI metrics: counts and a duration summary are present.
    assert "telemetry_requests_total" in body
    assert "telemetry_errors_total" in body
    assert "telemetry_request_duration_ms_sum" in body
