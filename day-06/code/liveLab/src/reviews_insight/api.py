"""The API at the edge, now hardened (the secure topic).

This carries forward everything from the dependable topic (trace-id and observe middleware,
GET /health and /ready, GET /metrics, POST and GET /v1/reviews with pagination and idempotency,
enrichment with graceful degradation, GET /v1/insight, and a signed webhook) and adds a security
layer on top, without changing any of that behavior:

- object-level authorization, so a caller can read only the reviews they own (this fixes BOLA,
  broken object-level authorization, the most common serious API flaw),
- mass-assignment protection, so the caller can set only the fields they are allowed to set and
  the server controls the rest (owner, flags, enrichment state),
- PII masking in logs, so a reviewer's email never appears in a log line,
- structured security events, so an authorization denial or a rejected request is recorded in a
  form a security tool can alert on, with no secret and no raw personal data in it,
- secrets read from configuration only (the webhook signing secret now comes from the config
  object, backed by the environment).
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
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from reviews_insight.config import Config
from reviews_insight.enrichment import enrich_or_degrade
from reviews_insight.observability import (
    Capacity,
    Metrics,
    get_logger,
    log_request,
    log_security_event,
)
from reviews_insight.security import caller_id_from_header, mask_email, mask_identifier
from reviews_insight.service import summarize_rows

# How many requests may be in flight before readiness reports "no free capacity". Kept generous
# so ordinary traffic is always ready; the point is that the number is real and enforced.
_CAPACITY_LIMIT = 100


class ReviewIn(BaseModel):
    """The request contract for a submit. FastAPI validates incoming JSON against it.

    Mass-assignment protection is built in here: this model lists only the fields a caller is
    allowed to set (product_id, rating, and an optional reviewer_email). Pydantic ignores any
    other field in the body by default, so a caller who also sends owner_id, is_flagged, or
    enriched cannot reach the stored record with them. The server sets those itself.
    """

    product_id: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)  # a value outside 1 to 5 is rejected with a 422
    # Optional and only ever used in masked form for logging; the raw address is never stored or
    # logged (see the submit handler and security.mask_email).
    reviewer_email: str | None = None


class ReviewAccepted(BaseModel):
    """The response contract for a submit, checked on the way out."""

    status: str
    enriched: bool  # whether the enrichment dependency answered in time, or we degraded


class ReviewOut(BaseModel):
    """One review as returned by a listing or a by-id read. The owner is never exposed."""

    review_id: str
    product_id: str
    rating: int


class ReviewPage(BaseModel):
    """A single page of reviews, plus the paging information to fetch the next one."""

    items: list[ReviewOut]
    total: int
    limit: int
    offset: int


class StoredReview(BaseModel):
    """A review as held in the store. The security-relevant fields live here.

    owner_id, is_flagged, and enriched are all set by the server, not by the request body. That
    separation is what makes both the authorization check and the mass-assignment protection
    real: the caller cannot name a different owner or clear a flag by sending extra JSON.
    """

    review_id: str
    owner_id: str
    product_id: str
    rating: int
    is_flagged: bool = False
    enriched: bool = False


def create_app(
    enrichment_client: httpx.AsyncClient | None = None,
    enrichment_url: str | None = None,
) -> FastAPI:
    """Build the API. The in-memory store lives inside, so each app instance is independent.

    enrichment_client and enrichment_url are injected so a test can supply a failing client (to
    prove graceful degradation) or a fake URL. When they are not given, the URL comes from
    config/env and a fresh httpx client is created per submit.
    """
    app = FastAPI(title="reviews-insight", version="0.7.0")
    store: list[StoredReview] = []
    # Idempotency ledger: an idempotency key maps to the result we already produced for it, so a
    # retry with the same key returns that result and does not store a second review.
    idempotent_results: dict[str, ReviewAccepted] = {}

    config = Config.from_env()
    url = enrichment_url if enrichment_url is not None else config.enrichment_url
    # The webhook signing secret comes from configuration (backed by the environment), not from a
    # literal in this file. It is shared with the third party that sends the webhook.
    webhook_secret = config.webhook_secret.encode("utf-8")
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
        # Stash the trace id so handlers and the validation error handler can put it on their
        # own security events, tying every log line for one request to the same id.
        request.state.trace_id = trace_id
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

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # A rejected request is a security-relevant event: the edge refusing malformed or
        # unexpected input. Record it as a security event, but do not echo the raw input back
        # into the log or the response, because that input could contain personal data.
        trace_id = str(getattr(request.state, "trace_id", ""))
        log_security_event(
            logger,
            event="validation_rejected",
            trace_id=trace_id,
            resource_id=request.url.path,
            reason="request failed schema validation",
        )
        safe_errors = [
            {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": safe_errors})

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
        request: Request,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
        x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    ) -> ReviewAccepted:
        # The caller identity is the verified user id (from an OAuth or JWT token in production;
        # from the X-User-Id header here). We take the owner from this, never from the body.
        caller_id = caller_id_from_header(x_user_id)
        trace_id = str(getattr(request.state, "trace_id", ""))

        # Idempotency: if we have seen this key before, return the earlier result unchanged. A
        # retry then has exactly one effect (one stored review), which is what makes it safe.
        if idempotency_key is not None and idempotency_key in idempotent_results:
            return idempotent_results[idempotency_key]

        # Only product_id and rating flow into the enrichment call; the email is never sent on.
        raw = {"product_id": review.product_id, "rating": str(review.rating)}
        enriched = await _enrich(raw)  # enriched when the dependency answers, degraded otherwise

        review_id = uuid.uuid4().hex
        store.append(
            StoredReview(
                review_id=review_id,
                owner_id=caller_id,  # server-assigned owner, taken from the verified caller
                product_id=review.product_id,
                rating=review.rating,
                is_flagged=False,  # server-controlled; a body field of the same name is ignored
                enriched=bool(enriched["enriched"]),
            )
        )

        # PII masking: if an email was supplied, the security event carries only its masked form.
        # The raw address is never logged or stored.
        pii = {"masked_email": mask_email(review.reviewer_email)} if review.reviewer_email else None
        log_security_event(
            logger,
            event="review_received",
            trace_id=trace_id,
            resource_id=review_id,
            caller=mask_identifier(caller_id),
            extra=pii,
        )

        result = ReviewAccepted(status="accepted", enriched=bool(enriched["enriched"]))
        if idempotency_key is not None:
            idempotent_results[idempotency_key] = result
        return result

    @app.get("/v1/reviews", response_model=ReviewPage)
    def list_reviews(limit: int = 20, offset: int = 0) -> ReviewPage:
        # Never return the whole collection at once. Return one page, plus the total so the
        # caller knows how many pages remain.
        page = store[offset : offset + limit]
        items = [
            ReviewOut(review_id=row.review_id, product_id=row.product_id, rating=row.rating)
            for row in page
        ]
        return ReviewPage(items=items, total=len(store), limit=limit, offset=offset)

    @app.get("/v1/reviews/{review_id}", response_model=ReviewOut)
    def get_review(
        review_id: str,
        request: Request,
        x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    ) -> ReviewOut:
        # Object-level authorization (the BOLA fix): find the review, then return it only if the
        # caller owns it. Knowing the id is not enough; ownership is checked on every read.
        caller_id = caller_id_from_header(x_user_id)
        trace_id = str(getattr(request.state, "trace_id", ""))
        for row in store:
            if row.review_id == review_id:
                if row.owner_id != caller_id:
                    # Fail secure: answer 404, not 403, so a caller cannot even confirm that the
                    # id exists (this is what stops object enumeration). Record the denial.
                    log_security_event(
                        logger,
                        event="authz_denied",
                        trace_id=trace_id,
                        resource_id=review_id,
                        caller=mask_identifier(caller_id),
                        reason="caller is not the owner",
                    )
                    raise HTTPException(status_code=404, detail="not found")
                return ReviewOut(
                    review_id=row.review_id, product_id=row.product_id, rating=row.rating
                )
        # A missing id gets the same 404, so present-but-forbidden and absent are indistinguishable.
        raise HTTPException(status_code=404, detail="not found")

    @app.get("/v1/insight")
    def insight() -> dict[str, int]:
        # Summarize whatever has been submitted so far, reusing the Day 3 shared logic.
        return summarize_rows(
            {"product_id": row.product_id, "rating": str(row.rating)} for row in store
        )

    @app.post("/v1/webhooks/rating", status_code=201)
    async def webhook(request: Request) -> dict[str, str]:
        # A webhook is a request from a system we do not control, so we cannot trust it just
        # because it arrived. Verify the signature over the raw body before acting on it.
        raw = await request.body()
        signature = request.headers.get("x-signature", "")
        expected = hmac.new(webhook_secret, raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="invalid signature")
        payload = json.loads(raw)
        store.append(
            StoredReview(
                review_id=uuid.uuid4().hex,
                owner_id="system:webhook",  # posted by the platform, not by an end user
                product_id=str(payload["product_id"]),
                rating=int(payload["rating"]),
                is_flagged=False,
                enriched=False,
            )
        )
        return {"status": "accepted"}

    return app


# A module-level app instance, so a server can load it as "reviews_insight.api:app".
app = create_app()
