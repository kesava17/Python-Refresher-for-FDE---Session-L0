"""The API at the edge, now made dependable (the reliable and trustworthy topic).

This carries forward everything from the interoperable topic (a versioned, validated HTTP
surface: trace-id middleware, GET /health, POST and GET /v1/reviews, GET /v1/insight, and a
signed webhook) and adds the operational habits that keep a service up under real conditions:

- an enrichment dependency called with a timeout and graceful degradation, so a slow or broken
  dependency cannot fail a submit,
- idempotency on submit, so a client that retries produces exactly one stored review,
- a readiness endpoint that reflects real in-flight capacity (separate from plain liveness),
- structured, leveled logging that carries the trace id for every request,
- in-process SLI metrics (request rate, error rate, duration) exposed at GET /metrics.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from collections.abc import Awaitable, Callable

import httpx
from fastapi import FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field

from reviews_insight.config import Config
from reviews_insight.enrichment import enrich_or_degrade
from reviews_insight.observability import Capacity, Metrics, get_logger, log_request
from reviews_insight.service import summarize_rows

# In real code this secret comes from configuration, never hard-coded. It is shared with the
# third party that sends the webhook, so both sides can compute the same signature.
_WEBHOOK_SECRET = b"shared-webhook-secret"

# How many requests may be in flight before readiness reports "no free capacity". Kept generous
# so ordinary traffic is always ready; the point is that the number is real and enforced.
_CAPACITY_LIMIT = 100


class ReviewIn(BaseModel):
    """The request contract. FastAPI validates incoming JSON against it at the edge."""

    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)  # a value outside 1 to 5 is rejected with a 422


class ReviewAccepted(BaseModel):
    """The response contract, checked on the way out."""

    status: str
    enriched: bool  # whether the enrichment dependency answered in time, or we degraded


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


def create_app(
    enrichment_client: httpx.AsyncClient | None = None,
    enrichment_url: str | None = None,
) -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent.

    enrichment_client and enrichment_url are injected so a test can supply a failing client (to
    prove graceful degradation) or a fake URL. When they are not given, the URL comes from
    config/env and a fresh httpx client is created per submit.
    """
    app = FastAPI(title="reviews-insight", version="0.6.0")
    store: list[dict[str, str]] = []
    # Idempotency ledger: an idempotency key maps to the result we already produced for it, so a
    # retry with the same key returns that result and does not store a second review.
    idempotent_results: dict[str, ReviewAccepted] = {}

    url = enrichment_url if enrichment_url is not None else Config.from_env().enrichment_url
    logger = get_logger()
    metrics = Metrics()
    capacity = Capacity(limit=_CAPACITY_LIMIT)

    @app.middleware("http")
    async def observe(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # One place for the cross-cutting concerns: reuse or start a trace id, count the request
        # as in-flight (for readiness), time it, record its SLIs, and log one structured line.
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        capacity.acquire()
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            capacity.release()  # released even if the handler raised, so capacity does not leak
        duration_ms = (time.perf_counter() - start) * 1000.0
        metrics.observe(status=response.status_code, duration_ms=duration_ms)
        log_request(
            logger,
            event=request.url.path,
            trace_id=trace_id,
            duration_ms=duration_ms,
            status=response.status_code,
        )
        # Passing the trace id back (and logging it above) lets one request be followed across
        # every service it touches.
        response.headers["x-trace-id"] = trace_id
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        # Liveness: is the process up and able to answer at all? It says nothing about capacity.
        return {"status": "ok"}

    @app.get("/ready")
    def ready(response: Response) -> dict[str, str]:
        # Readiness: should this instance receive traffic right now? It reflects real capacity,
        # so an orchestrator can route work away from a saturated instance instead of piling on.
        if capacity.has_free():
            return {"status": "ready"}
        response.status_code = 503
        return {"status": "at capacity"}

    @app.get("/metrics")
    def metrics_endpoint() -> Response:
        # The SLIs (request rate, error rate, duration) as plain text, hand-rolled to avoid a
        # heavy metrics dependency. A scraper or a person can read it.
        return Response(content=metrics.render(), media_type="text/plain")

    async def _enrich(review: dict[str, str]) -> dict[str, object]:
        # Use the injected client when present (tests do this); otherwise open a fresh one for
        # this call. Either way enrich_or_degrade bounds the call with a timeout and degrades.
        if enrichment_client is not None:
            return await enrich_or_degrade(review, enrichment_client, url)
        async with httpx.AsyncClient() as client:
            return await enrich_or_degrade(review, client, url)

    @app.post("/v1/reviews", status_code=201, response_model=ReviewAccepted)
    async def submit(
        review: ReviewIn,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> ReviewAccepted:
        # By the time we reach here, review is already valid: the edge rejected any bad input.
        # Idempotency: if we have seen this key before, return the earlier result unchanged. A
        # retry then has exactly one effect (one stored review), which is what makes it safe.
        if idempotency_key is not None and idempotency_key in idempotent_results:
            return idempotent_results[idempotency_key]

        raw = {"product_id": review.product_id, "rating": str(review.rating)}
        enriched = await _enrich(raw)  # enriched when the dependency answers, degraded otherwise
        # Store the enriched flag alongside the review, so downstream readers know whether this
        # record carries an insight or was accepted in degraded form.
        store.append({**raw, "enriched": str(enriched["enriched"])})

        result = ReviewAccepted(status="accepted", enriched=bool(enriched["enriched"]))
        if idempotency_key is not None:
            idempotent_results[idempotency_key] = result
        return result

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
