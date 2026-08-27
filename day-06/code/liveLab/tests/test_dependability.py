"""Dependability tests: graceful degradation, idempotency, readiness, and SLI metrics.

These cover the operational habits added in the reliable and trustworthy topic. They use the
FastAPI TestClient for the HTTP surface, and test the async enrichment function directly with
asyncio.run and a small fake client, so we do not need pytest-asyncio.
"""

from __future__ import annotations

import asyncio

import httpx
from fastapi.testclient import TestClient

from reviews_insight.api import create_app
from reviews_insight.enrichment import enrich_or_degrade


class _TimeoutClient:
    """A fake enrichment client whose post always times out, to inject a dependency fault."""

    async def post(self, *args: object, **kwargs: object) -> httpx.Response:
        raise httpx.TimeoutException("enrichment timed out")


class _OkClient:
    """A fake enrichment client that answers successfully with an insight."""

    async def post(self, *args: object, **kwargs: object) -> httpx.Response:
        # A request is attached so raise_for_status works, as it would on a real response.
        request = httpx.Request("POST", "http://enrichment.test/enrich")
        return httpx.Response(200, json={"insight": "positive"}, request=request)


def test_fault_injection_degrades_but_still_accepts() -> None:
    # Inject an enrichment client that always times out. The submit must still succeed and the
    # review must come back marked enriched=false, proving the service degrades instead of erroring.
    client = TestClient(create_app(enrichment_client=_TimeoutClient()))
    resp = client.post("/v1/reviews", json={"product_id": "P1", "rating": 5})
    assert resp.status_code == 201
    assert resp.json() == {"status": "accepted", "enriched": False}
    # The review is still stored and counted, so the degraded path loses nothing but the insight.
    assert client.get("/v1/insight").json()["reviews"] == 1


def test_enrich_or_degrade_on_timeout_returns_degraded() -> None:
    # Test the async function directly with asyncio.run, no pytest-asyncio needed.
    review = {"product_id": "P1", "rating": "5"}
    result = asyncio.run(
        enrich_or_degrade(review, _TimeoutClient(), "http://enrichment.invalid/enrich")  # type: ignore[arg-type]
    )
    assert result == {"product_id": "P1", "rating": "5", "insight": None, "enriched": False}


def test_enrich_or_degrade_on_success_returns_enriched() -> None:
    review = {"product_id": "P1", "rating": "5"}
    result = asyncio.run(
        enrich_or_degrade(review, _OkClient(), "http://enrichment.test/enrich")  # type: ignore[arg-type]
    )
    assert result == {"product_id": "P1", "rating": "5", "insight": "positive", "enriched": True}


def test_idempotent_submit_stores_once() -> None:
    # Two submits with the same idempotency key simulate a client retry. Only one review must be
    # stored, and both calls must return the same result: a retry has exactly one effect.
    client = TestClient(create_app(enrichment_client=_OkClient()))
    headers = {"Idempotency-Key": "retry-key-1"}
    first = client.post("/v1/reviews", json={"product_id": "P1", "rating": 5}, headers=headers)
    second = client.post("/v1/reviews", json={"product_id": "P1", "rating": 5}, headers=headers)
    assert first.status_code == 201
    assert second.json() == first.json()
    # Only one stored review, despite two POSTs with the same key.
    assert client.get("/v1/insight").json()["reviews"] == 1


def test_distinct_keys_store_separately() -> None:
    # A different key is a different request, so both are stored. This guards against the
    # idempotency check swallowing genuinely new submissions.
    client = TestClient(create_app(enrichment_client=_OkClient()))
    client.post("/v1/reviews", json={"product_id": "P1", "rating": 5}, headers={"Idempotency-Key": "a"})
    client.post("/v1/reviews", json={"product_id": "P2", "rating": 4}, headers={"Idempotency-Key": "b"})
    assert client.get("/v1/insight").json()["reviews"] == 2


def test_ready_returns_200_normally() -> None:
    # With capacity free, readiness reports 200. Liveness stays a separate, plain check.
    client = TestClient(create_app(enrichment_client=_OkClient()))
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}
    assert client.get("/health").status_code == 200


def test_metrics_exposes_counters() -> None:
    # After a couple of requests, the metrics endpoint reports the SLI counters as plain text.
    client = TestClient(create_app(enrichment_client=_OkClient()))
    client.get("/health")
    client.post("/v1/reviews", json={"product_id": "P1", "rating": 5})
    body = client.get("/metrics").text
    assert "requests_total" in body
    assert "errors_total" in body
    assert "request_duration_ms_sum" in body
