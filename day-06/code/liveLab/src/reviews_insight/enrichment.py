"""Enrichment with a timeout and graceful degradation (the dependable topic).

A dependable service does not let a slow or broken dependency take it down. This module calls
an external enrichment service to add an "insight" to a review, but it bounds the call with a
timeout and, if the call is slow or fails, it returns the review in a degraded form rather than
raising. The submit path stays available: a review is always accepted, enriched when the
dependency is healthy and plainly marked as not enriched when it is not.
"""

from __future__ import annotations

import httpx

# One second is our budget for the enrichment call. Past that we stop waiting and degrade,
# so one slow dependency cannot pile up requests and exhaust the service.
ENRICH_TIMEOUT_SECONDS = 1.0


async def enrich_or_degrade(
    review: dict[str, str],
    client: httpx.AsyncClient,
    url: str,
    timeout: float = ENRICH_TIMEOUT_SECONDS,
) -> dict[str, object]:
    """POST the review to the enrichment service, degrading gracefully on timeout or error.

    On success the enriched review is returned with an "insight" from the service and
    "enriched": True. On a timeout or any HTTP or transport error we return the same review
    with "insight": None and "enriched": False, so the caller still gets a usable result.
    The client is passed in (dependency injection), which lets a test inject a failing client.
    """
    try:
        response = await client.post(url, json=review, timeout=timeout)
        response.raise_for_status()
        body = response.json()
        insight = body.get("insight") if isinstance(body, dict) else None
        return {**review, "insight": insight, "enriched": True}
    except (httpx.TimeoutException, httpx.HTTPError):
        # httpx.TimeoutException covers the timeout; httpx.HTTPError covers connection failures
        # and non-2xx responses. Either way we degrade instead of failing the whole request.
        return {**review, "insight": None, "enriched": False}
