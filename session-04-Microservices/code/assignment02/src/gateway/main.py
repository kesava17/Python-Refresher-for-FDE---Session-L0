"""gateway service: one front door, routing to transactions-service and ledger-service.

Run it with:  poetry run uvicorn gateway.main:app --port 8000

It forwards the correlation id, guards its calls (timeout, retry, circuit breaker), and
degrades cleanly: when the ledger is down, the account view returns a clear note instead of
hanging or failing hard. The account endpoint is a small backend-for-frontend.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI, HTTPException

from common import observability
from common.client import CircuitBreaker, CircuitOpen, resilient_get
from common.config import settings
from contracts.transaction import TransactionIn


def create_app(transactions_url: str | None = None, ledger_url: str | None = None) -> FastAPI:
    """Build the gateway app pointed at the two services (overridable in tests)."""
    transactions_url = transactions_url or settings.transactions_url
    ledger_url = ledger_url or settings.ledger_url
    breaker = CircuitBreaker(threshold=3, cooldown=5.0)
    app = FastAPI(title="gateway", version="1.0")
    observability.install(app, "gateway")

    @app.post("/transactions", status_code=201)
    def submit_transaction(transaction: TransactionIn) -> dict[str, Any]:
        """Forward a transaction to transactions-service, passing the correlation id."""
        cid = observability.current_correlation_id()
        try:
            with httpx.Client(timeout=settings.http_timeout) as client:
                response = client.post(
                    f"{transactions_url}/v1/transactions",
                    json=transaction.model_dump(),
                    headers={"X-Correlation-ID": cid},
                )
                response.raise_for_status()
                created: dict[str, Any] = response.json()
                return created
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="transactions-service unavailable") from exc

    @app.get("/bff/account/{account_id}")
    def account(account_id: str) -> dict[str, Any]:
        """Backend-for-frontend: one tailored call for the account view, degrading cleanly."""
        cid = observability.current_correlation_id()
        try:
            summary = resilient_get(
                f"{ledger_url}/v1/accounts/{account_id}/summary",
                timeout=settings.http_timeout,
                breaker=breaker,
                correlation_id=cid,
            )
        except CircuitOpen:
            return {"account_id": account_id, "summary": None, "note": "temporarily unavailable"}
        except httpx.HTTPError:
            return {"account_id": account_id, "summary": None, "note": "no data yet"}
        return {"account_id": account_id, "summary": summary}

    return app


app = create_app()
