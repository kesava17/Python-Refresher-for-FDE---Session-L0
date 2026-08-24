"""Day 5 contract tests: the API validates at the edge and exposes a real, versioned contract."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from transactions_insight.api import create_app

_WEBHOOK_SECRET = b"shared-webhook-secret"  # must match the secret the app uses


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _sign(body: bytes) -> str:
    return hmac.new(_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()


def test_health_route() -> None:
    assert _client().get("/health").json() == {"status": "ok"}


def test_score_valid_returns_int_score() -> None:
    client = _client()
    response = client.post(
        "/v1/score", json={"account_id": "A1", "amount": 10.0, "currency": "INR"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["account_id"] == "A1"
    # The score is a stable, checksum-derived integer in the range 0 to 999.
    assert isinstance(body["score"], int)
    assert 0 <= body["score"] < 1000


def test_bad_input_is_rejected_at_the_edge() -> None:
    client = _client()
    # A non-positive amount fails the gt=0 rule before our code runs.
    assert (
        client.post(
            "/v1/score", json={"account_id": "A1", "amount": -5, "currency": "INR"}
        ).status_code
        == 422
    )
    # A currency code of "US" is too short for the min_length=3 rule.
    assert (
        client.post(
            "/v1/score", json={"account_id": "A1", "amount": 10.0, "currency": "US"}
        ).status_code
        == 422
    )
    # An empty account_id fails the min_length=1 rule the same way.
    assert (
        client.post(
            "/v1/score", json={"account_id": "", "amount": 10.0, "currency": "INR"}
        ).status_code
        == 422
    )


def test_openapi_contract_exists() -> None:
    # FastAPI generates the machine-readable contract; the versioned route is in it.
    doc = _client().get("/openapi.json").json()
    assert "/v1/score" in doc["paths"]


def test_list_transactions_is_paginated() -> None:
    client = _client()
    for i in range(5):
        client.post(
            "/v1/transactions", json={"account_id": f"A{i}", "amount": 10.0, "currency": "INR"}
        )
    page = client.get("/v1/transactions", params={"limit": 2, "offset": 2}).json()
    assert page["total"] == 5  # the total is reported so the caller can page through
    assert page["limit"] == 2
    assert page["offset"] == 2
    assert len(page["items"]) == 2  # only one page is returned, not all five


def test_webhook_accepts_a_valid_signature() -> None:
    client = _client()
    body = json.dumps({"account_id": "A9", "amount": 25.0, "currency": "INR"}).encode("utf-8")
    resp = client.post(
        "/v1/webhooks/transaction", content=body, headers={"x-signature": _sign(body)}
    )
    assert resp.status_code == 201
    assert client.get("/v1/transactions").json()["total"] == 1


def test_webhook_rejects_a_forged_signature() -> None:
    client = _client()
    body = json.dumps({"account_id": "A9", "amount": 25.0, "currency": "INR"}).encode("utf-8")
    resp = client.post("/v1/webhooks/transaction", content=body, headers={"x-signature": "forged"})
    assert resp.status_code == 401  # a bad signature is refused before the payload is used
    assert client.get("/v1/transactions").json()["total"] == 0


def test_trace_id_is_returned_and_echoed() -> None:
    client = _client()
    # With no trace id sent, the server generates one and returns it.
    assert client.get("/health").headers.get("x-trace-id")
    # With a trace id sent, the server echoes the same one back, so the request can be followed.
    resp = client.get("/health", headers={"x-trace-id": "abc123"})
    assert resp.headers["x-trace-id"] == "abc123"
