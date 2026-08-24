"""The API at the edge (Day 5): a versioned, validated HTTP surface over the service.

FastAPI plus pydantic give us the two habits from Section 1.1 for free. The pydantic model
validates incoming JSON at the boundary (a value of 999 is rejected with a 422 before our code
runs), and the `/v1` prefix versions the contract. FastAPI also generates an OpenAPI document at
`/openapi.json`, which is the machine-readable contract other teams build against. On top of that
sit the practical pieces a real API needs: a paginated list, a signed webhook we can trust, and a
trace id that ties a request's logs together as it crosses services.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from telemetry_insight.service import summarize_rows

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class ReadingIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    device_id: str = Field(min_length=1)
    value: float = Field(ge=-50, le=150)  # a value outside -50 to 150 is rejected with a 422


class ReadingAccepted(BaseModel):
    """The response contract, checked on the way out."""

    status: str


class ReadingOut(BaseModel):
    """One reading as returned in a listing."""

    device_id: str
    value: float


class ReadingPage(BaseModel):
    """A single page of readings, plus the paging information to fetch the next one."""

    items: list[ReadingOut]
    total: int
    limit: int
    offset: int


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="telemetry-insight", version="0.5.0")
    store: list[dict[str, str]] = []

    @app.middleware("http")
    async def add_trace_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Reuse the caller's trace id if it sent one, otherwise start a new one. Passing it back
        # (and, in real code, logging it) lets one request be followed across every service.
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        response = await call_next(request)
        response.headers["x-trace-id"] = trace_id
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        # A liveness route so other systems can check the service is up.
        return {"status": "ok"}

    @app.post("/v1/readings", status_code=201, response_model=ReadingAccepted)
    def ingest(reading: ReadingIn) -> ReadingAccepted:
        # By the time we reach here, reading is already valid: the edge rejected any bad input.
        store.append({"device_id": reading.device_id, "value": str(reading.value)})
        return ReadingAccepted(status="accepted")

    @app.get("/v1/readings", response_model=ReadingPage)
    def list_readings(limit: int = 20, offset: int = 0) -> ReadingPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [ReadingOut(device_id=row["device_id"], value=float(row["value"])) for row in page]
        return ReadingPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        # Summarize whatever has been ingested so far, reusing the Day 3 shared logic.
        return summarize_rows(iter(store))

    @app.post("/v1/webhooks/reading", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        store.append({"device_id": str(payload["device_id"]), "value": str(payload["value"])})
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "telemetry_insight.api:app".
app = create_app()
