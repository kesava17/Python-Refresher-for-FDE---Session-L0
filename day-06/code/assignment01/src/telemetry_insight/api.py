"""The API at the edge: a versioned, validated HTTP surface with a security layer.

The interoperable base gave us the two boundary habits: pydantic validates incoming JSON (a
value outside the allowed range is rejected with a 422 before our code runs) and the `/v1`
prefix versions the contract. FastAPI also publishes an OpenAPI document at `/openapi.json`.
On top of that sit a paginated list, a signed webhook, and a trace id.

The dependability layer added durability under load: idempotency on ingest, load shedding
through bounded concurrency, a downstream sink with graceful degradation, a readiness route,
structured leveled logging, and simple SLI metrics. All of that still works here.

This topic adds the security layer, keeping every earlier behavior intact:

- Object-level authorization (the fix for a BOLA, a broken-object-level-authorization flaw).
  Each stored reading has an `owner_id`. A single-reading route returns the reading only when
  the caller owns it, and returns 404 otherwise so ids cannot be probed by an outsider.
- Mass-assignment protection: ingest binds only the fields a caller may set. Server-controlled
  fields such as `owner_id` are set on the server, never read from the request body.
- Sensitive-field masking in logs: an optional device-owner contact is never logged raw, only
  in a masked form.
- Structured security events for an authorization denial and a validation rejection.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from collections.abc import Awaitable, Callable

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from telemetry_insight.observability import Metrics, configure_logging, log_event
from telemetry_insight.security import log_security_event, mask_email
from telemetry_insight.service import summarize_rows
from telemetry_insight.sink import forward_or_buffer

# The webhook secret comes from the environment, never hard-coded in the source. Both sides
# (us and the third party that sends the webhook) load the same shared value from their own
# configuration, so both can compute the same signature. The literal here is only a dev
# fallback so the local tests run without extra setup; real deployments set WEBHOOK_SECRET.
_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "shared-webhook-secret").encode("utf-8")

# The header that carries the caller identity. In production this is a validated token; the
# teaching point here is the authorization check, so we read a plain header for the identity.
_CALLER_HEADER = "x-user-id"

# The owner recorded when a request carries no caller identity, so an anonymous ingest still
# stores a valid record and can never accidentally match a real owner.
_ANONYMOUS_OWNER = "anonymous"

# The owner recorded for a signed webhook, which is a server-to-server call with no end user.
_SYSTEM_OWNER = "system"


def _caller_id(request: Request) -> str:
    # Read the caller identity from the header, defaulting to a fixed anonymous value. A real
    # deployment would decode and verify a token here; the authorization check downstream is
    # the same either way.
    return request.headers.get(_CALLER_HEADER) or _ANONYMOUS_OWNER


def _make_record(
    device_id: str, value: object, owner_id: str, contact_email: str = ""
) -> dict[str, str]:
    # Build one stored record with a server-generated id and a server-set owner. Callers never
    # supply the id or the owner, which is what closes the mass-assignment hole.
    return {
        "reading_id": uuid.uuid4().hex,
        "device_id": device_id,
        "value": str(value),
        "owner_id": owner_id,
        "contact_email": contact_email,
    }

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
    """The request contract, and the mass-assignment boundary.

    This model declares exactly the fields a caller is allowed to set. Pydantic ignores any
    other key in the JSON body by default, so a body that also carries `owner_id` or a `status`
    flag has those extra keys dropped here. That is the mass-assignment protection: the server
    binds only these fields, and sets the owner itself after the bind.
    """

    device_id: str = Field(min_length=1)
    value: float = Field(ge=-50, le=150)  # a value outside -50 to 150 is rejected with a 422
    # Optional per-reading idempotency key. A redelivery carrying the same key is deduped.
    key: str | None = Field(default=None, min_length=1)
    # Optional device-owner contact. A caller may set it, but it is sensitive, so it is never
    # logged raw, only in a masked form (see the ingest handler).
    contact_email: str | None = Field(default=None, min_length=1)


class ReadingAccepted(BaseModel):
    """The response contract, checked on the way out."""

    status: str
    # The server-generated id of the stored reading, so the caller can fetch it back later.
    # None on a duplicate, where nothing new was stored.
    id: str | None = None


class ReadingOut(BaseModel):
    """One reading as returned in a listing."""

    device_id: str
    value: float


class ReadingDetail(BaseModel):
    """One reading returned from the owner-scoped single-reading route.

    It carries the `owner_id` so the caller can see who owns it. It never carries the contact
    email, so the sensitive field is not handed back out through this route.
    """

    id: str
    device_id: str
    value: float
    owner_id: str


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
    app = FastAPI(title="telemetry-insight", version="0.7.0")
    # Each stored record now carries a server-generated reading_id and a server-set owner_id
    # alongside the device_id and value, so a reading can be fetched by id and authorized.
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

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: Exception) -> JSONResponse:
        # A rejected body is a security-relevant event: someone sent input the contract does
        # not allow. We record a structured security event (masked caller, no raw body) and
        # return a plain 422 that does not echo the offending input back to the caller.
        trace_id = getattr(request.state, "trace_id", "")
        log_security_event(
            "validation_rejected", trace_id, request.url.path, _caller_id(request), 422
        )
        return JSONResponse({"detail": "validation error"}, status_code=422)

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
            # The owner is taken from the caller identity, never from the request body. Even if
            # the body tried to carry an owner_id, ReadingIn does not bind it, so it is gone.
            owner_id = _caller_id(request)

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

            # Never log the raw contact email. If one was sent, log only its masked form.
            if reading.contact_email is not None:
                log_event(
                    "reading_ingested",
                    request.state.trace_id,
                    0.0,
                    201,
                    device_id=reading.device_id,
                    contact=mask_email(reading.contact_email),
                )

            record = _make_record(
                reading.device_id,
                reading.value,
                owner_id,
                reading.contact_email or "",
            )
            store.append(record)
            if key is not None:
                seen_keys.add(key)
            return ReadingAccepted(status="accepted", id=record["reading_id"])
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

    @app.get("/v1/readings/{reading_id}", response_model=ReadingDetail)
    def get_reading(reading_id: str, request: Request) -> ReadingDetail:
        # Object-level authorization (the BOLA fix). Having a valid id is not enough: the
        # caller must own the record. A caller who is not the owner gets the same 404 as a
        # missing id, so ownership is not revealed and ids cannot be enumerated (fail secure).
        caller = _caller_id(request)
        for row in store:
            if row["reading_id"] != reading_id:
                continue
            if row["owner_id"] != caller:
                # Record the denial as a structured security event with a masked caller.
                log_security_event(
                    "authz_denied",
                    request.state.trace_id,
                    f"reading:{reading_id}",
                    caller,
                    404,
                )
                raise HTTPException(status_code=404, detail="not found")
            return ReadingDetail(
                id=row["reading_id"],
                device_id=row["device_id"],
                value=float(row["value"]),
                owner_id=row["owner_id"],
            )
        # No record with that id at all: the same 404 an outsider sees for a record they do
        # not own, so the two cases are indistinguishable.
        raise HTTPException(status_code=404, detail="not found")

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
        # A signed webhook is a server-to-server call with no end user, so the record is owned
        # by the system, not by any caller. It still gets a server-generated id like any other.
        store.append(
            _make_record(str(payload["device_id"]), payload["value"], _SYSTEM_OWNER)
        )
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "telemetry_insight.api:app".
app = create_app()
