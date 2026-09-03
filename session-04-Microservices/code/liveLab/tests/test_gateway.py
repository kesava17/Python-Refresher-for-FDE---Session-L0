"""Tests for the gateway: it degrades cleanly when a downstream service is down."""

from __future__ import annotations

from fastapi.testclient import TestClient

from gateway.main import create_app


def test_dashboard_degrades_when_query_is_down() -> None:
    """With reviews-query unreachable, the dashboard returns a clear note, it does not hang or 500."""
    client = TestClient(create_app(ingest_url="http://127.0.0.1:59998", query_url="http://127.0.0.1:59999"))
    response = client.get("/bff/dashboard/p1")
    assert response.status_code == 200
    body = response.json()
    assert body["summary"] is None
    assert "note" in body


def test_submit_returns_502_when_ingest_is_down() -> None:
    """With reviews-ingest unreachable, submit fails fast with a clear 502, not a hang."""
    client = TestClient(create_app(ingest_url="http://127.0.0.1:59998", query_url="http://127.0.0.1:59999"))
    response = client.post("/reviews", json={"product_id": "p1", "rating": 5, "text": "great"})
    assert response.status_code == 502
