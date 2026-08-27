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
import os
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field

from transactions_insight.dependability import (
    Capacity,
    Metrics,
    TransactionStore,
    get_logger,
    log_event,
)
from transactions_insight.native import crc32_native
from transactions_insight.security import log_security_event

# The webhook secret is read from the environment, never hard-coded, so a real deployment sets it
# from its secret store and the value never lives in source or in an image. The wordy default is a
# development convenience only, so the local tests and the sample webhook signer share one value.
# The secret scan in scripts/secret_scan.py checks that no secret is bound directly to a literal.
_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "shared-webhook-secret").encode()


class TransactionIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge.

    Mass-assignment protection lives here. The model lists only the fields a caller is allowed to
    set. Server-controlled fields (the owner, the status, any settled or approved flag) are not in
    the model, so a body that sends "owner" or "status" cannot bind them. extra="ignore" makes the
    rule explicit: unknown fields are dropped, not trusted, so a crafted body cannot smuggle in a
    field the server alone should decide.
    """

    model_config = ConfigDict(extra="ignore")

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
    """One accepted transaction as returned to a caller or in a listing.

    The id lets a caller fetch this one transaction later. The status is a server-controlled field:
    it is returned so the owner can read it, but it is never accepted from the request body.
    """

    id: str
    account_id: str
    amount: float
    currency: str
    status: str


class TransactionPage(BaseModel):
    """A single page of transactions, plus the paging information to fetch the next one."""

    items: list[TransactionOut]
    total: int
    limit: int
    offset: int


def _to_out(row: dict[str, str]) -> TransactionOut:
    """Build the response model from one stored row, in one place so every route agrees.

    The stored row keeps amounts as a string, so we convert to a number here. The owner is never
    copied into the response, because it is an internal authorization field, not part of the
    public shape a caller reads back.
    """
    return TransactionOut(
        id=row["id"],
        account_id=row["account_id"],
        amount=float(row["amount"]),
        currency=row["currency"],
        status=row["status"],
    )


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="transactions-insight", version="0.7.0")
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
        # Store the trace id on the request so a route handler or an error handler can put it on a
        # security event, tying that event to the same request as the routine request log line.
        request.state.trace_id = trace_id
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
        x_user_id: str | None = Header(default=None),
    ) -> TransactionOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        # The idempotency key can arrive in the Idempotency-Key header or in the body; the header
        # wins if both are sent. With a key, a retry (including one after a lost response) records
        # exactly one transaction and returns the same result, so an account is never charged
        # twice. Without a key, each call records a new transaction as before.
        key = idempotency_key or txn.idempotency_key
        # The owner is the caller, read from the X-User-Id header. In production this identity comes
        # from a validated token; the teaching point is that the server sets the owner, never the
        # body. When no identity is sent we fall back to "anonymous", so the reliability tests that
        # predate this auth layer still work. The record is built here from the validated caller
        # fields plus the server-set fields, so a body value for owner or status can never bind.
        owner = x_user_id or "anonymous"
        record = {
            "id": uuid.uuid4().hex,  # a server-generated id, so a caller cannot choose it
            "account_id": txn.account_id,
            "amount": str(txn.amount),
            "currency": txn.currency,
            "owner": owner,  # set from the caller, never from the body
            "status": "received",  # a server-controlled field, never from the body
        }
        stored, _created = store.add(record, key=key)
        return _to_out(stored)

    @app.get("/v1/transactions/{transaction_id}", response_model=TransactionOut)
    def get_transaction(
        transaction_id: str,
        request: Request,
        x_user_id: str | None = Header(default=None),
    ) -> TransactionOut:
        # Object-level authorization (the fix for a BOLA weakness): a transaction is returned only
        # when the caller owns it. A valid id is not enough; the caller must be the owner too.
        caller = x_user_id or "anonymous"
        record = store.get(transaction_id)
        if record is None or record.get("owner") != caller:
            # Fail secure: whether the transaction does not exist or the caller simply does not own
            # it, we answer with the same 404 and reveal nothing. A 403 here would leak that the id
            # is real, which lets an attacker enumerate ids that belong to other people.
            trace_id = getattr(request.state, "trace_id", "")
            masked = record.get("account_id", "") if record is not None else ""
            log_security_event(
                logger,
                "security.authorization_denied",
                trace_id,
                resource=f"transaction:{transaction_id}",
                account=masked,
            )
            raise HTTPException(status_code=404, detail="not found")
        return _to_out(record)

    @app.get("/v1/transactions", response_model=TransactionPage)
    def list_transactions(limit: int = 20, offset: int = 0) -> TransactionPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        rows = store.all()
        page = rows[offset : offset + limit]
        items = [_to_out(row) for row in page]
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
                "id": uuid.uuid4().hex,  # a server-generated id, the same rule as the submit route
                "account_id": str(payload["account_id"]),
                "amount": str(payload["amount"]),
                "currency": str(payload["currency"]),
                # A webhook is verified by its signature, not by a user identity, so it has no
                # X-User-Id owner. We record a system owner, so a normal user's ownership check
                # can never match it, and set the same server-controlled status.
                "owner": "system:webhook",
                "status": "received",
            },
            key=key,
        )
        return {"status": "accepted"}

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # The edge already rejects bad input with a 422 before any route runs. We add one structured
        # security event so a rejection is visible to a log tool, then return the same 422 shape as
        # before. We mask the account from the raw body, and we never log the errors' raw values, so
        # nothing sensitive reaches the log.
        trace_id = getattr(request.state, "trace_id", "")
        account = ""
        if isinstance(exc.body, dict):
            account = str(exc.body.get("account_id", ""))
        log_security_event(
            logger,
            "security.validation_rejected",
            trace_id,
            resource=request.url.path,
            account=account,
        )
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})

    return app


# A module-level app instance, so a server can load it as "transactions_insight.api:app".
app = create_app()
