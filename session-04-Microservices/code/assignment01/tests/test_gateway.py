"""Tests for the gateway: it degrades cleanly when a downstream service is down."""

from __future__ import annotations

from fastapi.testclient import TestClient

from gateway.main import create_app


def test_device_view_degrades_when_rollup_is_down() -> None:
    """With telemetry-rollup unreachable, the device view returns a clear note, it does not hang or 500."""
    client = TestClient(
        create_app(ingest_url="http://127.0.0.1:59998", rollup_url="http://127.0.0.1:59999")
    )
    response = client.get("/bff/device/d1")
    assert response.status_code == 200
    body = response.json()
    assert body["summary"] is None
    assert "note" in body


def test_submit_returns_502_when_ingest_is_down() -> None:
    """With telemetry-ingest unreachable, submit fails fast with a clear 502, not a hang."""
    client = TestClient(
        create_app(ingest_url="http://127.0.0.1:59998", rollup_url="http://127.0.0.1:59999")
    )
    response = client.post(
        "/readings", json={"device_id": "d1", "value": 21.5, "ts": "2026-09-01T10:00:00Z"}
    )
    assert response.status_code == 502
