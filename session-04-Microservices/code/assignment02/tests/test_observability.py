"""Tests for observability: the correlation id is honoured and echoed."""

from __future__ import annotations

from fastapi.testclient import TestClient

from common.broker import FileBroker
from transactions_service.main import create_app
from transactions_service.store import TransactionStore


def _client(tmp_path) -> TestClient:
    """Build any service client (transactions) to exercise the shared middleware."""
    app = create_app(
        store=TransactionStore(str(tmp_path / "t.db")),
        broker=FileBroker(str(tmp_path / "b.jsonl")),
    )
    return TestClient(app)


def test_correlation_id_is_echoed(tmp_path) -> None:
    """An incoming correlation id comes back on the response."""
    response = _client(tmp_path).get("/health", headers={"X-Correlation-ID": "abc-123"})
    assert response.headers["X-Correlation-ID"] == "abc-123"


def test_correlation_id_is_generated_when_absent(tmp_path) -> None:
    """With no id supplied, the service generates one so the request can still be traced."""
    response = _client(tmp_path).get("/health")
    assert response.headers.get("X-Correlation-ID")
