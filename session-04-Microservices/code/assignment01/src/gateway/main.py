"""gateway service: one front door, routing to telemetry-ingest and telemetry-rollup.

Run it with:  poetry run uvicorn gateway.main:app --port 8000

It forwards the correlation id, guards its calls (timeout, retry, circuit breaker), and
degrades cleanly: when a downstream service is down, the device view returns a clear note
instead of hanging or failing hard. The device endpoint is a small backend-for-frontend.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI, HTTPException

from common import observability
from common.client import CircuitBreaker, CircuitOpen, resilient_get
from common.config import settings
from contracts.reading import ReadingIn


def create_app(ingest_url: str | None = None, rollup_url: str | None = None) -> FastAPI:
    """Build the gateway app pointed at the two services (overridable in tests)."""
    ingest_url = ingest_url or settings.ingest_url
    rollup_url = rollup_url or settings.rollup_url
    breaker = CircuitBreaker(threshold=3, cooldown=5.0)
    app = FastAPI(title="gateway", version="1.0")
    observability.install(app, "gateway")

    @app.post("/readings", status_code=201)
    def submit_reading(reading: ReadingIn) -> dict[str, Any]:
        """Forward a reading to telemetry-ingest, passing the correlation id."""
        cid = observability.current_correlation_id()
        try:
            with httpx.Client(timeout=settings.http_timeout) as client:
                response = client.post(
                    f"{ingest_url}/v1/readings",
                    json=reading.model_dump(),
                    headers={"X-Correlation-ID": cid},
                )
                response.raise_for_status()
                created: dict[str, Any] = response.json()
                return created
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="ingest unavailable") from exc

    @app.get("/bff/device/{device_id}")
    def device(device_id: str) -> dict[str, Any]:
        """Backend-for-frontend: one tailored call for the device fragment, degrading cleanly."""
        cid = observability.current_correlation_id()
        try:
            summary = resilient_get(
                f"{rollup_url}/v1/rollup/{device_id}",
                timeout=settings.http_timeout,
                breaker=breaker,
                correlation_id=cid,
            )
        except CircuitOpen:
            return {"device_id": device_id, "summary": None, "note": "temporarily unavailable"}
        except httpx.HTTPError:
            return {"device_id": device_id, "summary": None, "note": "no data yet"}
        return {"device_id": device_id, "summary": summary}

    return app


app = create_app()
