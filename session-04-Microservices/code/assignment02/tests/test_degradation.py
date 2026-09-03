"""Tests for the gateway: it degrades cleanly when a downstream service is down."""

from __future__ import annotations

from fastapi.testclient import TestClient

from gateway.main import create_app


def _down_gateway() -> TestClient:
    """Build a gateway pointed at two dead ports, so every downstream call fails fast."""
    return TestClient(
        create_app(
            transactions_url="http://127.0.0.1:59998",
            ledger_url="http://127.0.0.1:59999",
        )
    )


def test_account_view_degrades_when_ledger_is_down() -> None:
    """With the ledger unreachable, the account view returns a clear note, not a hang or 500."""
    response = _down_gateway().get("/bff/account/acc-1")
    assert response.status_code == 200
    body = response.json()
    assert body["summary"] is None
    assert "note" in body


def test_submit_returns_502_when_transactions_is_down() -> None:
    """With transactions-service unreachable, submit fails fast with a clear 502, not a hang."""
    response = _down_gateway().post(
        "/transactions", json={"account_id": "acc-1", "amount_cents": 500, "kind": "credit"}
    )
    assert response.status_code == 502
