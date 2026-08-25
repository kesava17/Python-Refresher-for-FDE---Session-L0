"""The API at the edge: a versioned, validated HTTP surface with a dependability layer.

The interoperable base gave us the two boundary habits: pydantic validates incoming JSON (a
value outside the allowed range is rejected with a 422 before our code runs) and the `/v1`
prefix versions the contract. FastAPI also publishes an OpenAPI document at `/openapi.json`.
On top of that sit a paginated list, a signed webhook, and a trace id.

This topic adds the dependability layer, tuned for the telemetry domain where the pressure is
durability under load and throughput:

- Idempotency on ingest, so a redelivered reading is recognized and not stored twice.
- Load shedding through bounded concurrency, so excess work gets a fast 429 and the accepted
  work keeps meeting its target instead of everything degrading together.
- A downstream sink with a timeout and graceful degradation, so a slow sink never fails ingest.
- A readiness route that reflects real free capacity (503 when there is none), separate from
  plain liveness at `/health`.
- Structured, leveled logging with the trace id, and simple SLI metrics at `/metrics`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from collections.abc import Awaitable, Callable

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from telemetry_insight.observability import Metrics, configure_logging, log_event
from telemetry_insight.service import summarize_rows
from telemetry_insight.sink import forward_or_buffer

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"

# Default ceiling on concurrent ingest work. Beyond this we shed with a 429 rather than let
# every request slow down at once. Small enough to keep latency bounded on modest hardware.
_DEFAULT_MAX_CONCURRENT = 64


class Capacity:
    """A bounded-concurrency gate: at most `limit` units of work in flight at once.

    Load shedding lives here. `try_acquire` returns False when the gate is full, and the
    caller then sheds the request with a fast 429 instead of piling on more work. The readiness
    route reads `free` to report whether the service has capacity to accept anything at all.
    """

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._in_flight = 0

    def try_acquire(self) -> bool:
        # Non-blocking: take a slot if one is free, otherwise report that we are full.
        if self._in_flight >= self._limit:
            return False
        self._in_flight += 1
        return True

    def release(self) -> None:
        # Always paired with a successful try_acquire, in a finally block.
        if self._in_flight > 0:
            self._in_flight -= 1

    @property
    def free(self) -> int:
        return self._limit - self._in_flight

    @property
    def in_flight(self) -> int:
        return self._in_flight


class ReadingIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    device_id: str = Field(min_length=1)
    value: float = Field(ge=-50, le=150)  # a value outside -50 to 150 is rejected with a 422
    # Optional per-reading idempotency key. A redelivery carrying the same key is deduped.
    key: str | None = Field(default=None, min_length=1)


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


def create_app(
    max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
    sink_client: httpx.AsyncClient | None = None,
) -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent.

    `max_concurrent` sets the load-shedding ceiling. `sink_client`, when given, turns on
    downstream forwarding through the sink; left as None (the default in tests) ingest keeps
    everything local and touches no network.
    """
    configure_logging()
    app = FastAPI(title="telemetry-insight", version="0.6.0")
    store: list[dict[str, str]] = []
    # Idempotency ledger: keys we have already stored, so a redelivery is a no-op.
    seen_keys: set[str] = set()
    capacity = Capacity(max_concurrent)
    metrics = Metrics()

    # Expose the moving parts on app.state so tests and operators can inspect real capacity.
    app.state.capacity = capacity
    app.state.metrics = metrics

    @app.middleware("http")
    async def observe(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Reuse the caller's trace id if it sent one, otherwise start a new one, and stash it
        # on request.state so route handlers can log with the same id.
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        request.state.trace_id = trace_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        response.headers["x-trace-id"] = trace_id
        # One SLI sample and one structured log line per request, both carrying the trace id.
        metrics.record(duration_ms, response.status_code)
        log_event(
            "request", trace_id, duration_ms, response.status_code, path=request.url.path
        )
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        # Plain liveness: the process is up and serving. It says nothing about capacity.
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> Response:
        # Readiness reflects real capacity: with no free slot we cannot take new work, so we
        # answer 503 and load balancers route elsewhere until a slot frees up.
        if capacity.free <= 0:
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ready"}, status_code=200)

    @app.get("/metrics")
    def metrics_route() -> Response:
        # Hand-rolled SLI metrics as plain text: request count, error count, duration summary.
        return PlainTextResponse(metrics.render())

    @app.post("/v1/readings", status_code=201, response_model=ReadingAccepted)
    async def ingest(reading: ReadingIn, request: Request) -> ReadingAccepted:
        # Load shedding first: if the gate is full, shed with a fast 429 so accepted work
        # keeps its target instead of everyone slowing down together.
        if not capacity.try_acquire():
            raise HTTPException(status_code=429, detail="load shed: no free capacity")
        try:
            # Idempotency: a key can arrive on the reading or in an Idempotency-Key header.
            # If we have seen it, this is a redelivery, so we recognize it and store nothing.
            key = reading.key or request.headers.get("idempotency-key")
            if key is not None and key in seen_keys:
                return ReadingAccepted(status="duplicate")

            # Optional downstream forwarding. A slow or failing sink degrades to a buffered
            # reading (forwarded False) and never fails ingest.
            if sink_client is not None:
                outcome = await forward_or_buffer(
                    {"device_id": reading.device_id, "value": reading.value}, sink_client
                )
                log_event(
                    "forward",
                    request.state.trace_id,
                    0.0,
                    200,
                    forwarded=outcome["forwarded"],
                )

            store.append({"device_id": reading.device_id, "value": str(reading.value)})
            if key is not None:
                seen_keys.add(key)
            return ReadingAccepted(status="accepted")
        finally:
            # Always release the slot, whether we stored, deduped, or raised.
            capacity.release()

    @app.get("/v1/readings", response_model=ReadingPage)
    def list_readings(limit: int = 20, offset: int = 0) -> ReadingPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [ReadingOut(device_id=row["device_id"], value=float(row["value"])) for row in page]
        return ReadingPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        # Summarize whatever has been ingested so far, reusing the shared service logic.
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
