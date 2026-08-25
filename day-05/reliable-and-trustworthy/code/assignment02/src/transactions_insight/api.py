"""The API at the edge (Day 5): a versioned, validated HTTP surface over the service.

FastAPI plus pydantic give us the two habits from Section 1.1 for free. The pydantic model
validates incoming JSON at the boundary (a non-positive amount is rejected with a 422 before
our code runs), and the `/v1` prefix versions the contract. The scoring route then leans on the
native CRC32 from native.py to turn a validated request into one stable, checksum-derived number.
FastAPI also generates an OpenAPI document at `/openapi.json`, the machine-readable contract
other teams build against. Beyond scoring, a real API needs a few more practical pieces: a
response model checked on the way out, a paginated list, a signed webhook we can trust, and a
trace id that ties one request's logs together as it crosses services.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from transactions_insight.dependability import (
    Capacity,
    Metrics,
    TransactionStore,
    get_logger,
    log_event,
)
from transactions_insight.native import crc32_native

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class TransactionIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    account_id: str = Field(min_length=1)  # an empty account id is rejected with a 422
    amount: float = Field(gt=0)  # money in rupees; a non-positive amount is rejected with a 422
    currency: str = Field(min_length=3, max_length=3)  # a code like "US" (too short) fails here
    # A per-transaction idempotency key (optional). A caller may send the key here in the body
    # instead of the Idempotency-Key header. Scoring ignores it; only the write path uses it.
    idempotency_key: str | None = Field(default=None)


class ScoreOut(BaseModel):
    """The scoring response contract, checked on the way out."""

    account_id: str
    score: int


class TransactionOut(BaseModel):
    """One accepted transaction as returned in a listing."""

    account_id: str
    amount: float
    currency: str


class TransactionPage(BaseModel):
    """A single page of transactions, plus the paging information to fetch the next one."""

    items: list[TransactionOut]
    total: int
    limit: int
    offset: int


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="transactions-insight", version="0.6.0")
    # The dependability layer: an exactly-once store, a capacity gauge for readiness, a metrics
    # collector, and the shared structured logger. Each app instance owns its own set, so the
    # tests stay independent.
    store = TransactionStore()
    capacity = Capacity()
    metrics = Metrics()
    logger = get_logger()

    @app.middleware("http")
    async def observe(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # One middleware does the cross-cutting work for every request: it carries the trace id,
        # tracks in-flight load for readiness, times the call, and records one metric and one
        # structured log line. Reuse the caller's trace id if it sent one, otherwise start a new
        # one, so a single request can be followed across every service.
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        capacity.acquire()
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # A crash is never allowed to be invisible: record it as an error and log it before
            # re-raising. The finally block still frees the capacity slot.
            duration_ms = (time.perf_counter() - start) * 1000
            metrics.record(duration_ms, 500)
            log_event(logger, logging.ERROR, "request.error", trace_id, duration_ms, 500)
            raise
        finally:
            capacity.release()
        duration_ms = (time.perf_counter() - start) * 1000
        metrics.record(duration_ms, response.status_code)
        log_event(logger, logging.INFO, "request", trace_id, duration_ms, response.status_code)
        response.headers["x-trace-id"] = trace_id
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        # Liveness: is the process up. This stays a plain, always-200 check, separate from
        # readiness below, so a load balancer can tell "up" apart from "ready for more work".
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> Response:
        # Readiness: can the service take more work right now. When in-flight load reaches the
        # capacity limit, we report 503 so callers back off instead of piling on and losing work.
        if capacity.is_ready():
            return PlainTextResponse('{"status": "ready"}', media_type="application/json")
        return PlainTextResponse(
            '{"status": "saturated"}', status_code=503, media_type="application/json"
        )

    @app.get("/metrics")
    def metrics_endpoint() -> Response:
        # Plain-text SLI metrics: request count, error count, and a duration summary. Hand-rolled
        # so there is no heavy metrics dependency to install or run.
        return PlainTextResponse(metrics.render())

    @app.post("/v1/score", response_model=ScoreOut)
    def score(txn: TransactionIn) -> ScoreOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        # We fold the three fields into one byte string and hand it to the native checksum,
        # so the same request always yields the same score. This is the interop routine at work.
        payload = f"{txn.account_id}:{txn.amount}:{txn.currency}".encode()
        return ScoreOut(account_id=txn.account_id, score=crc32_native(payload) % 1000)

    @app.post("/v1/transactions", status_code=201, response_model=TransactionOut)
    def submit(
        txn: TransactionIn,
        idempotency_key: str | None = Header(default=None),
    ) -> TransactionOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        # The idempotency key can arrive in the Idempotency-Key header or in the body; the header
        # wins if both are sent. With a key, a retry (including one after a lost response) records
        # exactly one transaction and returns the same result, so an account is never charged
        # twice. Without a key, each call records a new transaction as before.
        key = idempotency_key or txn.idempotency_key
        record = {
            "account_id": txn.account_id,
            "amount": str(txn.amount),
            "currency": txn.currency,
        }
        stored, _created = store.add(record, key=key)
        return TransactionOut(
            account_id=stored["account_id"],
            amount=float(stored["amount"]),
            currency=stored["currency"],
        )

    @app.get("/v1/transactions", response_model=TransactionPage)
    def list_transactions(limit: int = 20, offset: int = 0) -> TransactionPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        rows = store.all()
        page = rows[offset : offset + limit]
        items = [
            TransactionOut(
                account_id=row["account_id"],
                amount=float(row["amount"]),
                currency=row["currency"],
            )
            for row in page
        ]
        return TransactionPage(items=items, total=len(rows), limit=limit, offset=offset)

    @app.post("/v1/webhooks/transaction", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        # Route the webhook write through the same all-or-nothing store, so an inbound event is
        # recorded whole or not at all. A webhook id, when present, doubles as an idempotency key
        # so a redelivered event is recorded only once.
        key = str(payload["id"]) if "id" in payload else None
        store.add(
            {
                "account_id": str(payload["account_id"]),
                "amount": str(payload["amount"]),
                "currency": str(payload["currency"]),
            },
            key=key,
        )
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "transactions_insight.api:app".
app = create_app()
