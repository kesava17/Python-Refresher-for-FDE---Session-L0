"""The API at the edge (Day 5): a versioned, validated HTTP surface over the service.

FastAPI plus pydantic give us the habits from the lesson for free: request and response models
checked at the edge, a versioned path, a generated OpenAPI document, plus the practical pieces a
real API needs: a paginated list, a signed webhook we can trust, and a trace id that ties a
request's logs together as it crosses services.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from reviews_insight.service import summarize_rows

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"


class ReviewIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)  # a value outside 1 to 5 is rejected with a 422


class ReviewAccepted(BaseModel):
    """The response contract, checked on the way out."""

    status: str


class ReviewOut(BaseModel):
    """One review as returned in a listing."""

    product_id: str
    rating: int


class ReviewPage(BaseModel):
    """A single page of reviews, plus the paging information to fetch the next one."""

    items: list[ReviewOut]
    total: int
    limit: int
    offset: int


def create_app() -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent."""
    app = FastAPI(title="reviews-insight", version="0.5.0")
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

    @app.post("/v1/reviews", status_code=201, response_model=ReviewAccepted)
    def submit(review: ReviewIn) -> ReviewAccepted:
        # By the time we reach here, review is already valid: the edge rejected any bad input.
        store.append({"product_id": review.product_id, "rating": str(review.rating)})
        return ReviewAccepted(status="accepted")

    @app.get("/v1/reviews", response_model=ReviewPage)
    def list_reviews(limit: int = 20, offset: int = 0) -> ReviewPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [ReviewOut(product_id=row["product_id"], rating=int(row["rating"])) for row in page]
        return ReviewPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        # Summarize whatever has been submitted so far, reusing the Day 3 shared logic.
        return summarize_rows(iter(store))

    @app.post("/v1/webhooks/rating", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(_WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        store.append({"product_id": str(payload["product_id"]), "rating": str(payload["rating"])})
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "reviews_insight.api:app".
app = create_app()
