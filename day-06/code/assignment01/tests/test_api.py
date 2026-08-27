"""Day 5 contract tests: the API validates at the edge and exposes a real, versioned contract."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from telemetry_insight.api import create_app

_WEBHOOK_SECRET = b"shared-webhook-secret"  # must match the secret the app uses


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _sign(body: bytes) -> str:
    return hmac.new(_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()


def test_health_route() -> None:
    assert _client().get("/health").json() == {"status": "ok"}


def test_ingest_valid_then_insight() -> None:
    client = _client()
    assert client.post("/v1/readings", json={"device_id": "D1", "value": 20.5}).status_code == 201
    client.post("/v1/readings", json={"device_id": "D1", "value": 21.0})
    client.post("/v1/readings", json={"device_id": "D2", "value": 19.0})
    assert client.get("/v1/insight").json() == {"readings": 3, "devices": 2, "rejected": 0}


def test_bad_input_is_rejected_at_the_edge() -> None:
    client = _client()
    # A value of 999 is outside -50 to 150, so pydantic rejects it before our code runs.
    assert client.post("/v1/readings", json={"device_id": "D1", "value": 999}).status_code == 422
    # An empty device_id fails the min_length rule the same way.
    assert client.post("/v1/readings", json={"device_id": "", "value": 20.0}).status_code == 422


def test_openapi_contract_exists() -> None:
    # FastAPI generates the machine-readable contract; the versioned route is in it.
    doc = _client().get("/openapi.json").json()
    assert "/v1/readings" in doc["paths"]


def test_list_readings_is_paginated() -> None:
    client = _client()
    for i in range(5):
        client.post("/v1/readings", json={"device_id": f"D{i}", "value": 20.0})
    page = client.get("/v1/readings", params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 5  # the total is reported so the caller can page through
    assert page["limit"] == 2
    assert page["offset"] == 2
    assert len(page["items"]) == 2  # only one page is returned, not all five


def test_webhook_accepts_a_valid_signature() -> None:
    client = _client()
    body = json.dumps({"device_id": "D9", "value": 22.0}).encode("utf-8")
    resp = client.post("/v1/webhooks/reading", content=body, headers={"x-signature": _sign(body)})
    assert resp.status_code == 201
    assert client.get("/v1/insight").json()["readings"] == 1


def test_webhook_rejects_a_forged_signature() -> None:
    client = _client()
    body = json.dumps({"device_id": "D9", "value": 22.0}).encode("utf-8")
    resp = client.post("/v1/webhooks/reading", content=body, headers={"x-signature": "forged"})
    assert resp.status_code == 401  # a bad signature is refused before the payload is used
    assert client.get("/v1/insight").json()["readings"] == 0


def test_trace_id_is_returned_and_echoed() -> None:
    client = _client()
    # With no trace id sent, the server generates one and returns it.
    assert client.get("/health").headers.get("x-trace-id")
    # With a trace id sent, the server echoes the same one back, so the request can be followed.
    resp = client.get("/health", headers={"x-trace-id": "abc123"})
    assert resp.headers["x-trace-id"] == "abc123"
