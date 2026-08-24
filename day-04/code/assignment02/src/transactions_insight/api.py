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
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from transactions_insight.native import crc32_native

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class TransactionIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    account_id: str = Field(min_length=1)  # an empty account id is rejected with a 422
    amount: float = Field(gt=0)  # money in rupees; a non-positive amount is rejected with a 422
    currency: str = Field(min_length=3, max_length=3)  # a code like "US" (too short) fails here


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
    app = FastAPI(title="transactions-insight", version="0.5.0")
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

    @app.post("/v1/score", response_model=ScoreOut)
    def score(txn: TransactionIn) -> ScoreOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        # We fold the three fields into one byte string and hand it to the native checksum,
        # so the same request always yields the same score. This is the interop routine at work.
        payload = f"{txn.account_id}:{txn.amount}:{txn.currency}".encode()
        return ScoreOut(account_id=txn.account_id, score=crc32_native(payload) % 1000)

    @app.post("/v1/transactions", status_code=201, response_model=TransactionOut)
    def submit(txn: TransactionIn) -> TransactionOut:
        # By the time we reach here, txn is already valid: the edge rejected any bad input.
        store.append(
            {"account_id": txn.account_id, "amount": str(txn.amount), "currency": txn.currency}
        )
        return TransactionOut(account_id=txn.account_id, amount=txn.amount, currency=txn.currency)

    @app.get("/v1/transactions", response_model=TransactionPage)
    def list_transactions(limit: int = 20, offset: int = 0) -> TransactionPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [
            TransactionOut(
                account_id=row["account_id"],
                amount=float(row["amount"]),
                currency=row["currency"],
            )
            for row in page
        ]
        return TransactionPage(items=items, total=len(store), limit=limit, offset=offset)

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
        store.append(
            {
                "account_id": str(payload["account_id"]),
                "amount": str(payload["amount"]),
                "currency": str(payload["currency"]),
            }
        )
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "transactions_insight.api:app".
app = create_app()
